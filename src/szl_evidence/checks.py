"""Evidence checks (1.8). Each check is versioned and produces a CheckResult per subject.

A check never converts missing evidence into success: absent inputs yield ABSTAIN with
INSUFFICIENT_EVIDENCE (or a more specific reason), never PASS and never FAIL.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .adapters.citations import CitationResolver, Resolution
from .claims import (
    RECIPE_INTERPRETER,
    NumberParseError,
    RecipeOutOfScope,
    input_manifest_sha256,
    missing_chain_links,
    quantities_equal,
    run_recipe,
    value_matches,
)
from .dependencies import DependencyError, DependencyGraph
from .discovery import Discovery
from .manifest import Manifest
from .models import CheckResult, Failure, Reason, Status, sha256_file, sha256_json
from .safety import UnsafeInput, contained

S, R, F = Status, Reason, Failure


@dataclass
class Context:
    manifest: Manifest
    disc: Discovery
    resolver: CitationResolver

    def sec(self, name: str) -> dict[str, Any] | None:
        v = self.manifest.sections.get(name)
        return v if isinstance(v, dict) else None

    def table(self, tid: str) -> list[dict[str, str]] | None:
        return self.disc.tables.get(tid)

    def data(self, did: str) -> Any:
        return self.disc.data.get(did)

    def available(self, *ids: str) -> list[str]:
        """IDs among ``ids`` that are not opened (missing/failed)."""
        return [i for i in ids if i not in self.disc.opened]


def abstain_missing(ids: list[str]) -> CheckResult:
    return CheckResult(
        S.ABSTAIN,
        R.INSUFFICIENT_EVIDENCE,
        [{"missing_or_unopened_inputs": ids}],
        detail="required evidence for this check was not available",
    )


@dataclass
class Check:
    name: str
    version: str
    section: str | None  # manifest section that activates this check; None = always
    inputs: Callable[[Context], list[str]]
    run: Callable[[Context], dict[str, CheckResult]]  # subject -> result ("" = whole)
    subjects: Callable[[Context], list[str]] | None = None


# ---------------------------------------------------------------- core checks
def _all_inputs(ctx: Context) -> list[str]:
    return [i.id for i in ctx.manifest.inputs]


def chk_inputs_present(ctx: Context) -> dict[str, CheckResult]:
    d = ctx.disc
    required = [i.id for i in ctx.manifest.inputs if i.required]
    if not ctx.manifest.inputs:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [{"declared_inputs": 0}], [F.VACUOUS_PASS], "manifest declares no inputs")}
    miss = [i for i in required if i in d.missing]
    failed = {k: v for k, v in d.failed.items() if k in required}
    ev = [{"expected": d.expected, "opened": d.opened, "missing": d.missing, "failed": failed}]
    if failed:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [], f"inputs failed to open/parse: {sorted(failed)}")}
    if miss:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [], f"missing required inputs: {miss}")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(d.opened))}


def chk_inputs_nonempty(ctx: Context) -> dict[str, CheckResult]:
    d = ctx.disc
    ev = [{"inputs_dir_exists": d.inputs_dir_exists, "discovered_files": len(d.discovered), "empty_inputs": d.empty}]
    if not d.inputs_dir_exists or not d.discovered:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "input directory missing or empty: nothing examined")}
    if sum(d.rows_examined.values()) == 0 and d.tables is not None and any(i.kind == "table" for i in ctx.manifest.inputs):
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "zero rows examined")}
    empty_required = [e for e in d.empty if (ctx.manifest.input(e) and ctx.manifest.input(e).required)]
    if empty_required:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], f"empty required inputs: {empty_required}")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(d.discovered))}


def chk_discovery_complete(ctx: Context) -> dict[str, CheckResult]:
    d = ctx.disc
    ev = [{"discovered": d.discovered, "undeclared": d.undeclared}]
    if not d.discovered:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "nothing discovered")}
    if d.undeclared:
        return {"": CheckResult(S.FAIL, R.UNVERIFIED, ev, [F.OMITTED_POPULATION], f"discovered but never opened: {d.undeclared}")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(d.discovered))}


def chk_rows_complete(ctx: Context) -> dict[str, CheckResult]:
    d = ctx.disc
    ev = [{"rows_parsed": d.rows_parsed, "rows_examined": d.rows_examined}]
    short = {k: (d.rows_examined.get(k, 0), v) for k, v in d.rows_parsed.items() if d.rows_examined.get(k, 0) < v}
    if short:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.PARTIAL_EXECUTION], f"subset examined (examined, parsed): {short}")}
    if not d.rows_parsed:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "no tables parsed")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=sum(d.rows_examined.values()))}


def chk_input_closure(ctx: Context) -> dict[str, CheckResult]:
    acct = ctx.disc.accounting()
    ok = acct["input_closure"]["closes"]
    return {"": CheckResult(S.PASS if ok else S.ERROR, R.VERIFIED if ok else R.PROTOCOL_BROKEN, [acct["input_closure"]], detail="" if ok else "input accounting does not close")}


def chk_duplicates(ctx: Context) -> dict[str, CheckResult]:
    out: dict[str, CheckResult] = {}
    for spec in ctx.manifest.inputs:
        if spec.kind != "table" or spec.id not in ctx.disc.tables:
            continue
        rows = ctx.disc.tables[spec.id]
        full = Counter(sha256_json(r) for r in rows)
        dup_full = sum(c - 1 for c in full.values() if c > 1)
        dup_keys: list[str] = []
        if spec.key:
            kc = Counter(r.get(spec.key) for r in rows)
            dup_keys = sorted(str(k) for k, c in kc.items() if c > 1)
        ev = [{"table": spec.id, "rows": len(rows), "duplicate_full_rows": dup_full, "duplicate_keys": dup_keys}]
        if dup_full or dup_keys:
            out[spec.id] = CheckResult(S.FAIL, R.UNVERIFIED, ev, detail="duplicate records", rows_examined=len(rows))
        else:
            out[spec.id] = CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(rows))
    if not out:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [{"tables_opened": 0}], [F.VACUOUS_PASS], "no tables available to check for duplicates")}
    return out


def _dup_subjects(ctx: Context) -> list[str]:
    return [s.id for s in ctx.manifest.inputs if s.kind == "table" and s.id in ctx.disc.tables]


# ---------------------------------------------------------------- snapshot
def _row_sha(row: dict[str, str]) -> str:
    return sha256_json(row)


def chk_snapshot(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("snapshot") or {}
    miss = ctx.available(sec.get("input", ""), sec.get("table", ""))
    if miss:
        return {"": abstain_missing(miss)}
    snap = ctx.data(sec["input"]) or {}
    key = snap.get("key")
    rows = ctx.table(sec["table"]) or []
    accepted = snap.get("row_sha256") or {}
    current = {r.get(key): _row_sha(r) for r in rows}
    deleted = sorted(k for k in accepted if k not in current)
    added = sorted(k for k in current if k not in accepted)
    changed = sorted(k for k in accepted if k in current and current[k] != accepted[k])
    ev = [{"accepted_rows": len(accepted), "current_rows": len(current), "deleted": deleted, "added": added, "changed": changed}]
    if not accepted:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [], "accepted snapshot is empty")}
    if deleted or added or changed:
        return {"": CheckResult(S.FAIL, R.SOURCE_MISMATCH, ev, [F.SOURCE_MISMATCH], "rows differ from accepted snapshot", rows_examined=len(rows))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(rows))}


# ---------------------------------------------------------------- reviews
def chk_reviews(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("reviews") or {}
    miss = ctx.available(sec.get("table", ""), sec.get("target_table", ""))
    if miss:
        return {"": CheckResult(S.ABSTAIN, R.REQUIRES_HUMAN_REVIEW, [{"missing": miss}], [], "human review evidence missing")}
    reviews = ctx.table(sec["table"]) or []
    targets = ctx.table(sec["target_table"]) or []
    rf, vf, need = sec["record_field"], sec["reviewer_field"], int(sec["required_per_record"])
    if not reviews:
        return {"": CheckResult(S.ABSTAIN, R.REQUIRES_HUMAN_REVIEW, [{"reviews": 0}], [], "no human review recorded")}
    pairs = Counter((r[rf], r[vf]) for r in reviews)
    dup_pairs = sorted(f"{a}|{b}" for (a, b), c in pairs.items() if c > 1)
    per: dict[str, set[str]] = {}
    for r in reviews:
        per.setdefault(r[rf], set()).add(r[vf])
    roster = sec.get("authorized_reviewers")
    shortfall = {t[rf]: len(per.get(t[rf], set())) for t in targets if len(per.get(t[rf], set())) < need}
    unauthorized = sorted({r[vf] for r in reviews if r[vf] not in roster}) if roster else []
    ev = [{"required_per_record": need, "records": len(targets), "duplicate_reviewer_pairs": dup_pairs, "shortfall": shortfall, "roster_declared": bool(roster), "unauthorized_reviewers": unauthorized}]
    if unauthorized:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [F.PROTOCOL_DRIFT], "reviews by reviewers outside the declared roster", rows_examined=len(reviews))}
    if dup_pairs:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [F.PROTOCOL_DRIFT], "duplicate reviewer pairs", rows_examined=len(reviews))}
    if shortfall:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [F.PROTOCOL_DRIFT], "reviewer-count shortfall", rows_examined=len(reviews))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(reviews))}


# ---------------------------------------------------------------- sources + timestamps
def chk_sources(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("sources") or {}
    miss = ctx.available(sec.get("table", ""), sec.get("records_table", ""))
    if miss:
        return {"": abstain_missing(miss)}
    sources = {r[sec["key"]]: r for r in ctx.table(sec["table"]) or []}
    recs = ctx.table(sec["records_table"]) or []
    unknown = sorted({r[sec["records_field"]] for r in recs if r[sec["records_field"]] not in sources})
    ev = [{"sources": len(sources), "records": len(recs), "unknown_source_ids": unknown}]
    if unknown:
        return {"": CheckResult(S.FAIL, R.SOURCE_MISMATCH, ev, [F.SOURCE_MISMATCH], "records cite unknown source identifiers", rows_examined=len(recs))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(recs))}


def parse_ts(s: str) -> datetime | None:
    """Parse ISO-8601; return None for timezone-naive values (they cannot be compared)."""
    t = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    return t if t.tzinfo is not None else None


def chk_timestamps(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("timestamps") or {}
    j = sec.get("join") or {}
    miss = ctx.available(sec.get("table", ""), j.get("table", ""))
    if miss:
        return {"": abstain_missing(miss)}
    recs = ctx.table(sec["table"]) or []
    src = {r[j["key"]]: r for r in ctx.table(j["table"]) or []}
    naive, mismatch, conv = [], [], []
    for r in recs:
        s = src.get(r[j["key"]])
        if s is None:
            continue
        try:
            a, b = parse_ts(r[sec["field"]]), parse_ts(s[j["field"]])
        except ValueError:
            naive.append(r[j["key"]])
            continue
        if a is None or b is None:
            naive.append(r[j["key"]])
            continue
        if a != b:
            rid = r.get(sec.get("record_key", "record_id"), r[j["key"]])
            mismatch.append({"record": rid, "source_id": r[j["key"]], "record_value": r[sec["field"]], "source_value": s[j["field"]], "delta_s": (a - b).total_seconds()})
            if a.replace(tzinfo=None) == b.replace(tzinfo=None):
                conv.append(rid)
    ev = [{"compared": len(recs), "naive": naive, "mismatch": mismatch, "same_wallclock_different_offset": conv}]
    if mismatch:
        return {"": CheckResult(S.FAIL, R.SOURCE_MISMATCH, ev, [F.SOURCE_MISMATCH], "timestamp instants disagree with source", rows_examined=len(recs))}
    if naive:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [], "timezone-naive timestamps cannot be compared", rows_examined=len(recs))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(recs))}


# ---------------------------------------------------------------- protocol
def chk_protocol(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("protocol") or {}
    miss = ctx.available(sec.get("execution_log", ""))
    if miss:
        return {"": abstain_missing(miss)}
    log = ctx.data(sec["execution_log"]) or {}
    declared = [str(s) for s in sec.get("steps", [])]
    executed = [str(s) for s in log.get("steps_executed", [])]
    ev = [{"declared_version": str(sec.get("version")), "executed_version": str(log.get("protocol_version")), "declared_steps": declared, "executed_steps": executed}]
    problems = []
    if str(log.get("protocol_version")) != str(sec.get("version")):
        problems.append("protocol version differs")
    if [s for s in declared if s not in executed]:
        problems.append(f"missing steps {[s for s in declared if s not in executed]}")
    if [s for s in executed if s not in declared]:
        problems.append(f"undeclared steps {[s for s in executed if s not in declared]}")
    if not problems and executed != declared:
        problems.append("steps executed out of declared order")
    if not declared:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [], "protocol declares no steps")}
    if problems:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [F.PROTOCOL_DRIFT], "; ".join(problems), rows_examined=len(executed))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(executed))}


# ---------------------------------------------------------------- claims
def _claims(ctx: Context) -> list[dict[str, Any]]:
    sec = ctx.sec("claims") or {}
    data = ctx.data(sec.get("input", "")) or {}
    return list(data.get("claims", [])) if isinstance(data, dict) else []


def _claim_subjects(ctx: Context) -> list[str]:
    return sorted(str(c.get("id")) for c in _claims(ctx))


def _stored_metrics(ctx: Context, entry: dict[str, Any]) -> tuple[dict[str, str] | None, str | None, str]:
    try:
        p = contained(ctx.manifest.root, entry["stored_output"])
    except (UnsafeInput, KeyError) as e:
        return None, None, f"stored output path invalid: {e}"
    if not p.exists():
        return None, None, "stored output missing"
    import csv
    import io

    rows = list(csv.DictReader(io.StringIO(p.read_text(encoding="utf-8"))))
    return {r["metric"]: r["value"] for r in rows}, sha256_file(p), ""


def chk_claims(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("claims") or {}
    miss = ctx.available(sec.get("input", ""), sec.get("registry", ""))
    if miss:
        return {s: abstain_missing(miss) for s in (_claim_subjects(ctx) or [""])}
    reg = (ctx.data(sec["registry"]) or {}).get("claims", {}) or {}
    out: dict[str, CheckResult] = {}
    for c in _claims(ctx):
        cid = str(c.get("id"))
        entry = reg.get(cid)
        links = missing_chain_links(entry)
        ev: dict[str, Any] = {"claim": c.get("text"), "published_value": c.get("value")}
        if links:
            ev["missing_registry_links"] = links
            out[cid] = CheckResult(S.FAIL, R.UNVERIFIED, [ev], [F.EPHEMERAL_CLAIM], "published claim is not fully registered", 1)
            continue
        metrics, out_sha, err = _stored_metrics(ctx, entry)
        if metrics is None:
            ev["stored_output"] = err
            out[cid] = CheckResult(S.FAIL, R.UNVERIFIED, [ev], [F.EPHEMERAL_CLAIM], err, 1)
            continue
        ev["stored_output_sha256"] = out_sha
        if out_sha != entry["output_sha256"]:
            ev["registered_output_sha256"] = entry["output_sha256"]
            out[cid] = CheckResult(S.FAIL, R.SOURCE_MISMATCH, [ev], [F.SOURCE_MISMATCH], "stored output differs from registered hash", 1)
            continue
        recipes = entry["recipe"] if isinstance(entry["recipe"], list) else [entry["recipe"]]
        if entry["code_version"] != RECIPE_INTERPRETER:
            ev["registered_code_version"] = entry["code_version"]
            ev["interpreter"] = RECIPE_INTERPRETER
            out[cid] = CheckResult(S.ABSTAIN, R.UNVERIFIED, [ev], [], "registered code version is not the interpreter that can replay it", 1)
            continue
        actual_inputs = input_manifest_sha256(recipes, ctx.disc.hashes)
        ev["input_manifest_sha256"] = actual_inputs
        if actual_inputs != entry["input_manifest_sha256"]:
            ev["registered_input_manifest_sha256"] = entry["input_manifest_sha256"]
            out[cid] = CheckResult(S.FAIL, R.SOURCE_MISMATCH, [ev], [F.SOURCE_MISMATCH], "inputs differ from those the claim was registered against", 1)
            continue
        try:
            # 1. replay the recipe against current inputs and compare to the stored output
            replay = []
            for rcp in recipes:
                recomputed = run_recipe(rcp, ctx.disc.tables)
                stored = metrics.get(rcp["metric"])
                if stored is None:
                    raise KeyError(f"metric {rcp['metric']!r} absent from stored output")
                ok, info = value_matches(stored, recomputed)
                replay.append({"metric": rcp["metric"], "stored": stored, "recomputed": str(recomputed), "agrees": ok})
            ev["replay"] = replay
            if not all(r["agrees"] for r in replay):
                out[cid] = CheckResult(S.FAIL, R.SOURCE_MISMATCH, [ev], [F.SOURCE_MISMATCH], "recipe replay disagrees with stored output", 1)
                continue
            # 2. compare the published claim with the stored output (numerically)
            if c.get("relation") == "equal":
                a, b = (metrics[m] for m in c["metrics"])
                eq, info = quantities_equal(a, b, c.get("tolerance", "0"))
                ev["equality"] = info
                if c.get("value") is not None:
                    va, ia = value_matches(c["value"], a)
                    vb, ib = value_matches(c["value"], b)
                    ev["rounded_agreement"] = [ia, ib]
                if not eq:
                    out[cid] = CheckResult(S.FAIL, R.UNVERIFIED, [ev], [F.DEFECTIVE_VERIFICATION], "claimed equality fails on unrounded values", 1)
                    continue
            else:
                ok, info = value_matches(c["value"], metrics[c["metric"]])
                ev["comparison"] = info
                if not ok:
                    out[cid] = CheckResult(S.FAIL, R.UNVERIFIED, [ev], [], "published value disagrees with stored output", 1)
                    continue
        except RecipeOutOfScope as e:
            ev["error"] = str(e)
            out[cid] = CheckResult(S.ABSTAIN, R.OUT_OF_SCOPE, [ev], [], "recipe uses an operation outside the engine's scope", 1)
            continue
        except (NumberParseError, KeyError, ValueError) as e:
            ev["error"] = f"{e.__class__.__name__}: {e}"
            out[cid] = CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [ev], [], "claim could not be evaluated", 1)
            continue
        rs = entry.get("review_state")
        if rs != "reviewed":
            out[cid] = CheckResult(S.ABSTAIN, R.REQUIRES_HUMAN_REVIEW, [ev], [], f"claim review_state={rs!r}", 1)
            continue
        out[cid] = CheckResult(S.PASS, R.VERIFIED, [ev], rows_examined=1)
    return out


# ---------------------------------------------------------------- dependencies
def chk_dependencies(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("dependencies") or {}
    miss = ctx.available(sec.get("input", ""))
    if miss:
        return {"": abstain_missing(miss)}
    try:
        g = DependencyGraph.load(ctx.data(sec["input"]) or {}, ctx.manifest.root)
        broken = g.broken_refs()
        if broken:
            return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, [{"broken_refs": broken}], [], "broken dependency references")}
        ev = g.evaluate()
    except (DependencyError, KeyError, ValueError, UnsafeInput) as e:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, [{"error": str(e)}], [], "dependency graph invalid")}
    if not g.nodes:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [ev], [], "empty dependency graph")}
    invalid = sorted(k for k, n in g.nodes.items() if n.state.value == "INVALIDATED")
    unresolved = sorted(k for k, n in g.nodes.items() if n.state.value == "UNRESOLVED")
    if invalid:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, [ev | {"invalidated": invalid}], [], "invalidated nodes present; publication blocked", len(g.nodes))}
    if unresolved:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [ev | {"unresolved": unresolved}], [], "unresolved nodes present; publication blocked", len(g.nodes))}
    if ev["stale"]:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [ev], [], "stale downstream nodes pending revalidation; publication blocked", len(g.nodes))}
    return {"": CheckResult(S.PASS, R.VERIFIED, [ev], rows_examined=len(g.nodes))}


# ---------------------------------------------------------------- citations
def _norm_author(a: str) -> str:
    return " ".join(a.strip().lower().replace(".", "").split())


def chk_citations(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("citations") or {}
    miss = ctx.available(sec.get("table", ""))
    if miss:
        return {"": abstain_missing(miss)}
    rows = ctx.table(sec["table"]) or []
    ctx.resolver.configure(ctx, sec)
    bad, notfound, unavailable, ok = [], [], [], 0
    for r in rows:
        res: Resolution = ctx.resolver.resolve(r["doi"])
        if res.state == "UNAVAILABLE":
            unavailable.append({"doi": r["doi"], "reason": res.detail})
            continue
        if res.state == "NOT_FOUND":
            notfound.append(r["doi"])
            continue
        claimed = [_norm_author(a) for a in r["authors"].split(";") if a.strip()]
        actual = [_norm_author(a) for a in res.authors]
        if claimed != actual:
            bad.append({"doi": r["doi"], "claimed": r["authors"], "registered": "; ".join(res.authors)})
        elif "year" in r and res.year is not None and str(r["year"]) != str(res.year):
            bad.append({"doi": r["doi"], "claimed_year": r["year"], "registered_year": res.year})
        else:
            ok += 1
    ev = [{"citations": len(rows), "verified": ok, "author_or_year_mismatch": bad, "doi_not_found": notfound, "resolver_unavailable": unavailable, "resolver": ctx.resolver.describe()}]
    if bad:
        return {"": CheckResult(S.FAIL, R.SOURCE_MISMATCH, ev, [F.SOURCE_MISMATCH], "citation metadata disagrees with registry", len(rows))}
    if notfound:
        return {"": CheckResult(S.FAIL, R.UNVERIFIED, ev, [], "DOI does not exist in authoritative registry", len(rows))}
    if unavailable:
        # Network failure is never evidence of a defect.
        return {"": CheckResult(S.ABSTAIN, R.SOURCE_UNAVAILABLE, ev, [], "resolver unavailable", len(rows))}
    if not rows:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "no citations")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(rows))}


# ---------------------------------------------------------------- population / screening
def chk_population(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("screening") or {}
    miss = ctx.available(sec.get("candidates", ""), sec.get("decisions", ""))
    if miss:
        return {"": abstain_missing(miss)}
    key = sec["key"]
    cands = [r[key] for r in ctx.table(sec["candidates"]) or []]
    dec = {r[key]: r["decision"] for r in ctx.table(sec["decisions"]) or []}
    counts = Counter(dec.values())
    omitted = sorted(c for c in cands if c not in dec)
    phantom = sorted(k for k in dec if k not in set(cands))
    invalid = sorted(k for k, v in dec.items() if v not in {"admitted", "excluded", "unresolved", "deferred"})
    retrieved = len(cands)
    closure = {
        "identity": "retrieved_records = admitted + excluded + unresolved (+ deferred)",
        "retrieved_records": retrieved,
        "admitted": counts.get("admitted", 0),
        "excluded": counts.get("excluded", 0),
        "unresolved": counts.get("unresolved", 0),
        "deferred": counts.get("deferred", 0),
    }
    closure["closes"] = retrieved == closure["admitted"] + closure["excluded"] + closure["unresolved"] + closure["deferred"]
    ev = [{"closure": closure, "omitted": omitted, "phantom": phantom, "invalid_decisions": invalid}]
    if omitted:
        return {"": CheckResult(S.FAIL, R.UNVERIFIED, ev, [F.OMITTED_POPULATION], f"candidates never entered the checked set: {omitted}", retrieved)}
    if phantom or invalid:
        return {"": CheckResult(S.FAIL, R.SOURCE_MISMATCH, ev, [F.SOURCE_MISMATCH], "decisions for unknown candidates or invalid decisions", retrieved)}
    if closure["unresolved"] or closure["deferred"]:
        return {"": CheckResult(S.ABSTAIN, R.REQUIRES_HUMAN_REVIEW, ev, [], "unresolved/deferred records remain", retrieved)}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=retrieved)}


# ---------------------------------------------------------------- attestations (external verification claims)
def chk_attestation(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("attestations") or {}
    miss = ctx.available(sec.get("input", ""))
    if miss:
        return {"": abstain_missing(miss)}
    att = ctx.data(sec["input"]) or {}
    invs = ctx.data(sec.get("invocations", "")) or []
    by_check: dict[str, list[dict[str, Any]]] = {}
    for i in invs:
        by_check.setdefault(str(i.get("check")), []).append(i)
    claimed = [str(c) for c in att.get("checks_claimed", [])]
    narrated = [c for c in claimed if not any(i.get("invocation_id") and i.get("result") for i in by_check.get(c, []))]
    ev = [{"producer": att.get("producer"), "claimed_status": att.get("claimed_status"), "checks_claimed": claimed, "invocations_supplied": len(invs), "claims_without_invocation": narrated}]
    if att.get("claimed_status") == "PASS" and not claimed:
        return {"": CheckResult(S.ABSTAIN, R.UNVERIFIED, ev, [F.NARRATED_VERIFICATION], "PASS asserted with no checks named")}
    if narrated:
        return {"": CheckResult(S.ABSTAIN, R.UNVERIFIED, ev, [F.NARRATED_VERIFICATION], f"claimed checks with no invocation evidence: {narrated}", len(claimed))}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(claimed))}


def chk_children(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("attestations") or {}
    miss = ctx.available(sec.get("input", ""))
    if miss:
        return {"": abstain_missing(miss)}
    kids = (ctx.data(sec["input"]) or {}).get("children", [])
    hidden = [k for k in kids if int(k.get("exit_code", 1)) == 0 and str(k.get("result", "")).upper() in {"FAIL", "ERROR"}]
    ev = [{"children": len(kids), "failures_behind_exit_0": hidden}]
    if hidden:
        return {"": CheckResult(S.FAIL, R.UNVERIFIED, ev, [F.DEFECTIVE_VERIFICATION], "child failure masked by exit code 0", len(kids))}
    if not kids:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, ev, [F.VACUOUS_PASS], "no child processes recorded")}
    return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(kids))}


# ---------------------------------------------------------------- determinism
def chk_determinism(ctx: Context) -> dict[str, CheckResult]:
    sec = ctx.sec("determinism") or {}
    specs = [x if isinstance(x, dict) else {"input": str(x)} for x in sec.get("replicates", [])]
    reps = [str(x.get("input")) for x in specs]
    miss = ctx.available(*reps)
    if miss or len(reps) < 2:
        return {"": abstain_missing(miss or ["<need >= 2 replicates>"])}
    seeds = {x.get("hash_seed") for x in specs}
    if None in seeds or len(seeds) < 2:
        return {"": CheckResult(S.ABSTAIN, R.INSUFFICIENT_EVIDENCE, [{"replicates": specs}], [], "replicates lack distinct declared hash seeds: cannot show independence from hash randomisation", len(reps))}
    raw = {r: ctx.disc.hashes[r] for r in reps}
    canon = {r: hashlib.sha256("\n".join(sorted(sha256_json(x) for x in ctx.table(r) or [])).encode()).hexdigest() for r in reps}
    ev = [{"raw_sha256": raw, "order_insensitive_sha256": canon, "hash_seeds": {x["input"]: x["hash_seed"] for x in specs}}]
    if len(set(raw.values())) == 1:
        return {"": CheckResult(S.PASS, R.VERIFIED, ev, rows_examined=len(reps))}
    if len(set(canon.values())) == 1:
        return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [], "replicates differ only in ordering: nondeterministic output order", len(reps))}
    return {"": CheckResult(S.FAIL, R.PROTOCOL_BROKEN, ev, [], "replicate outputs differ in content", len(reps))}


# ---------------------------------------------------------------- registry
def _sec_inputs(*keys: str, section: str) -> Callable[[Context], list[str]]:
    def f(ctx: Context) -> list[str]:
        s = ctx.sec(section) or {}
        out = []
        for k in keys:
            v = s.get(k)
            if isinstance(v, list):
                out += [str(x) for x in v]
            elif v:
                out.append(str(v))
        return out

    return f


CHECKS: list[Check] = [
    Check("inputs_present", "1.0", None, _all_inputs, chk_inputs_present),
    Check("inputs_nonempty", "1.0", None, _all_inputs, chk_inputs_nonempty),
    Check("discovery_complete", "1.0", None, _all_inputs, chk_discovery_complete),
    Check("rows_examined_complete", "1.0", None, _all_inputs, chk_rows_complete),
    Check("input_accounting_closure", "1.0", None, _all_inputs, chk_input_closure),
    Check("duplicate_records", "1.0", None, _all_inputs, chk_duplicates, _dup_subjects),
    Check("snapshot_rows", "1.0", "snapshot", _sec_inputs("input", "table", section="snapshot"), chk_snapshot),
    Check("reviewer_protocol", "1.0", "reviews", _sec_inputs("table", "target_table", section="reviews"), chk_reviews),
    Check("source_identity", "1.0", "sources", _sec_inputs("table", "records_table", section="sources"), chk_sources),
    Check("timestamp_consistency", "1.0", "timestamps", _sec_inputs("table", section="timestamps"), chk_timestamps),
    Check("protocol_conformance", "1.0", "protocol", _sec_inputs("execution_log", section="protocol"), chk_protocol),
    Check("claim_value", "1.0", "claims", _sec_inputs("input", "registry", section="claims"), chk_claims, _claim_subjects),
    Check("dependency_validity", "1.0", "dependencies", _sec_inputs("input", section="dependencies"), chk_dependencies),
    Check("citation_metadata", "1.0", "citations", _sec_inputs("table", "registry", section="citations"), chk_citations),
    Check("population_closure", "1.0", "screening", _sec_inputs("candidates", "decisions", section="screening"), chk_population),
    Check("attested_invocations", "1.0", "attestations", _sec_inputs("input", "invocations", section="attestations"), chk_attestation),
    Check("child_exit_integrity", "1.0", "attestations", _sec_inputs("input", section="attestations"), chk_children),
    Check("output_determinism", "1.0", "determinism", lambda ctx: [str(x.get("input") if isinstance(x, dict) else x) for x in (ctx.sec("determinism") or {}).get("replicates", [])], chk_determinism),
]

CHECKS_BY_NAME = {c.name: c for c in CHECKS}


def applicable_checks(manifest: Manifest) -> list[Check]:
    if manifest.required_checks:
        unknown = [n for n in manifest.required_checks if n not in CHECKS_BY_NAME]
        if unknown:
            raise KeyError(f"manifest requires unimplemented checks: {unknown}")
        names = set(manifest.required_checks) | {c.name for c in CHECKS if c.section is None}
        return [c for c in CHECKS if c.name in names]
    return [c for c in CHECKS if c.section is None or c.section in manifest.sections]


def _unused(_: Path) -> None:  # keep import graph explicit for linters
    return None
