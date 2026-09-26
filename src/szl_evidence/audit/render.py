"""Render reports 00-11 from persisted stage state.

Rules: values that were not measured render as UNKNOWN / UNAVAILABLE / NOT_TESTED, never as
0 or blank; no Python reprs; capped lists say "N of M"; every STATUS is derived from the
report's own content; every audit report carries coverage accounting; host paths are
redacted by ReportWriter; ``public=True`` leaves out private repositories and artifacts.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from ..models import NOT_TESTED, UNAVAILABLE, utcnow
from ..reports import ReportWriter, md_table, report
from .common import SEVERITY_ORDER
from .findings import FLAGSHIPS, bus_factor
from .pipeline import load
from .secrets_scan import PATTERNS as SECRET_PATTERNS

AXES = ["identity", "license", "provenance", "tests", "ci", "release_integrity", "security_posture", "docs", "honest_scoping", "evidence_boundary", "cross_links", "maintenance"]
ABBR = {"PASS": "P", "PARTIAL": "~", "FAIL": "F", "NOT_TESTED": "NT"}
CARD_AXES = ["card_exists", "not_a_stub", "license", "intended_use", "out_of_scope", "limitations", "evaluation", "training_data", "provenance", "reproduction", "contact", "non_establishment"]
HOST_NOTE = "Clean-install/test runs executed on a Windows 11 host (Python 3.12 venv, stripped environment, shallow clones with core.symlinks=false); Windows-specific outcomes are attributed HOST_PLATFORM, not to repositories."
TIMER_NOTE = "Latencies were timed with a ~15.6 ms-resolution clock on this host (values are multiples of it; differences below that are not measurable)."
VENDORED = re.compile(r"(\.min\.js|(^|/)(vendor|vendors|third_party|cesium|node_modules|dist|static/lib)/)", re.I)
SECRET_CONF = {t: c for t, _, c in SECRET_PATTERNS}


# ------------------------------------------------------------------ formatting helpers
def fmt(x: Any) -> str:
    """Human-readable value; never a Python repr."""
    if x is None:
        return UNAVAILABLE
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.2f}".rstrip("0").rstrip(".")
    if isinstance(x, dict):
        if "state" in x and len(x) <= 4:
            extra = f" (HTTP {x['http']})" if x.get("http") else ""
            msg = f" — {x['message']}" if x.get("message") else ""
            return f"{x['state']}{extra}{msg}"
        if not x:
            return "none"
        return ", ".join(f"{k}: {fmt(v)}" for k, v in x.items())
    if isinstance(x, (list, tuple, set)):
        return ", ".join(fmt(i) for i in x) if x else "none"
    return str(x)


def capped(items: list[Any], n: int, where: str) -> tuple[list[Any], str]:
    if len(items) <= n:
        return items, ""
    return items[:n], f"(showing {n} of {len(items)}; full list in {where})"


def bullets(items: Iterable[Any]) -> list[str]:
    out = [f"- {fmt(i)}" for i in items]
    return out or ["- none"]


def _hdr(**kw: Any) -> dict[str, Any]:
    keys = ["STATUS", "WHAT WAS EXPECTED", "WHAT WAS EXAMINED", "WHAT ACTUALLY RAN", "WHAT PASSED", "WHAT FAILED", "WHAT ABSTAINED", "WHAT REMAINS UNRESOLVED", "WHAT THIS RESULT DOES NOT PROVE"]
    return {k: kw.get(k.lower().replace(" ", "_"), "UNKNOWN") for k in keys}


def sev_status(findings: list[dict[str, Any]]) -> str:
    c = Counter(f["severity"] for f in findings)
    return "FAIL" if (c.get("CRITICAL") or c.get("HIGH")) else ("ATTENTION" if c.get("MEDIUM") else "PASS")


def smoke_source(s: dict[str, Any]) -> str:
    if s.get("evidence_admission"):
        return f"admitted from interim run (HEAD at test {str(s.get('head_at_test'))[:8]}; {'changed since' if s.get('head_changed_since') is True else 'unchanged'})"
    if s.get("harness_revision") == "fix2":
        return "fresh (harness fix2)"
    if s.get("reused_from_identical_head"):
        return "fresh (pip-cache fix; pre-fix2 clone)"
    return "fresh"


def counts_text(summary: Any) -> str:
    if not summary:
        return "UNKNOWN (not parsed)"
    return ", ".join(f"{v} {k}" for k, v in summary.items())


# ------------------------------------------------------------------ coverage
def gh_coverage(g: dict[str, Any]) -> dict[str, Any]:
    repos = g["gh"]["repos"]
    not_tested: dict[str, str] = {}
    for r in repos:
        if r.get("archived"):
            not_tested[r["name"]] = "archived: metadata-only scoring, not cloned"
        elif not r["clone"].get("ok"):
            not_tested[r["name"]] = r["clone"].get("reason") or f"clone/checkout failed (exit {r['clone'].get('exit_code')}): file-level analysis NOT_TESTED"
        else:
            s = g["smoke"].get(r["name"])
            if s is None:
                not_tested[r["name"]] = "no Python/Node entry point: installability NOT_TESTED (file-level analysis done)"
            elif s.get("install_ok") == NOT_TESTED:
                not_tested[r["name"]] = s.get("reason", "installability NOT_TESTED")
    tested = sum(1 for s in g["smoke"].values() if s.get("install_ok") in (True, False))
    pub = g["gh"]["org_meta"].get("public_repos") if isinstance(g["gh"].get("org_meta"), dict) else None
    return {
        "artifacts_expected": f"public {pub} (org metadata, OBSERVED) + private UNAVAILABLE (not exposed by the org API)" if pub is not None else UNAVAILABLE,
        "artifacts_discovered": f"{len(repos)} (authenticated listing, all pages; {sum(1 for r in repos if r.get('private'))} private)",
        "artifacts_examined": sum(1 for r in repos if r["clone"].get("ok")),
        "artifacts_functionally_tested": tested,
        "artifacts_not_tested": len(not_tested),
        "denominator_state": g["gh"]["listing"]["denominator_state"],
        "not_tested_reasons": not_tested,
    }


def hf_coverage(h: dict[str, Any]) -> dict[str, Any]:
    arts = h["hf"]["artifacts"]
    nt: dict[str, str] = {}
    tested = 0
    for a in arts:
        fn = a.get("functional") or {}
        key = f"{a['kind']}:{a['id']}"
        if a["kind"] == "space":
            st = (fn.get("http") or {}).get("state")
            if st in ("RESPONDED", "DID_NOT_LOAD"):
                tested += 1
            else:
                nt[key] = (fn.get("http") or {}).get("reason", NOT_TESTED)
        elif a["kind"] == "model":
            ld = (fn.get("load") or {}).get("state")
            if ld in ("LOADED", "LOAD_FAILED") or fn.get("headers"):
                tested += 1
            if ld in ("TOO_LARGE_NOT_TESTED", "RUNTIME_UNAVAILABLE_NOT_TESTED", "NOT_A_MODEL_REPO", NOT_TESTED):
                nt[key] = f"full load not performed ({load_label(fn)}): {(fn.get('load') or {}).get('reason', '')}"
        else:
            st = (fn.get("slice") or {}).get("state") or (fn.get("splits") or {}).get("state")
            if st and st != "SOURCE_UNAVAILABLE":
                tested += 1
            else:
                nt[key] = f"slice {st}"
    lst = h["hf"]["listing"]
    return {
        "artifacts_expected": sum(x["count"] for x in lst.values()),
        "artifacts_discovered": f"{len(arts)} (authenticated listing; {sum(1 for a in arts if a.get('private'))} private)",
        "artifacts_examined": sum(1 for a in arts if "files" in a),
        "artifacts_functionally_tested": tested,
        "artifacts_not_tested": len(nt),
        "denominator_state": "OBSERVED" if all(x["denominator_state"] == "OBSERVED" for x in lst.values()) else "UNAVAILABLE",
        "not_tested_reasons": nt,
    }


def rollup_coverage(g: dict[str, Any], h: dict[str, Any]) -> dict[str, Any]:
    gc, hc = gh_coverage(g), hf_coverage(h)
    return {
        "artifacts_expected": f"GitHub: {gc['artifacts_expected']}; HF: {hc['artifacts_expected']}",
        "artifacts_discovered": f"GitHub: {gc['artifacts_discovered']}; HF: {hc['artifacts_discovered']}",
        "artifacts_examined": f"GitHub: {gc['artifacts_examined']} cloned; HF: {hc['artifacts_examined']}",
        "artifacts_functionally_tested": f"GitHub: {gc['artifacts_functionally_tested']}; HF: {hc['artifacts_functionally_tested']}",
        "artifacts_not_tested": f"GitHub: {gc['artifacts_not_tested']}; HF: {hc['artifacts_not_tested']} (per-artifact reasons in 02 and 03)",
        "denominator_state": "OBSERVED" if gc["denominator_state"] == hc["denominator_state"] == "OBSERVED" else "UNAVAILABLE",
    }


def load_label(fn: dict[str, Any]) -> str:
    st = (fn.get("load") or {}).get("state")
    return "RUNTIME_UNAVAILABLE_NOT_TESTED" if st == "TOO_LARGE_NOT_TESTED" else fmt(st)


# ------------------------------------------------------------------ 01 engine
def r01(w: ReportWriter, e: dict[str, Any] | None) -> None:
    if not e:
        w.text("01-engine-verification.md", report("01 — Engine verification", _hdr(status="NOT_TESTED", what_was_expected="engine report state", what_was_examined="nothing", what_actually_ran="nothing", what_passed="none", what_failed="none", what_abstained="all", what_remains_unresolved="run `szl-audit engine report`", what_this_result_does_not_prove="anything"), "Engine stage has not run."))
        return
    fx = e["fixtures"]
    ms = e["mutations"]
    res = ms["results"]
    matched = sum(f["match"] for f in fx)
    blind = [r for r in res if r["status"] == "BLIND_SPOT"]
    partial = [r for r in res if r["status"] == "DETECTED" and r["missed_invariants"]]
    expected_det = [r for r in res if r["expected_detection"]]
    abst_fx = [f["fixture"] for f in fx if f["observed_status"] == "ABSTAIN"]
    abst_mut = [r["id"] for r in res if r["observed"] == "ABSTAIN"]
    by_target = Counter(r["target"] for r in res)
    body = ["## Fixtures", "", md_table(["fixture", "expected", "observed", "exit exp/obs", "evidence ok", "primary reason", "failure taxonomy", "claim not established"], [[f["fixture"], f["expected_status"], f["observed_status"], f"{f['expected_exit']}/{f['observed_exit']}", fmt(f["required_evidence_present"]), f["primary_reason"], ", ".join(f["failures"]) or "none", f["claim_not_established"]] for f in fx]), ""]
    body += ["## Mutation testing", "", f"Baseline: `{ms.get('baseline_status')}`. {len(res)} mutations: {by_target.get('input', 0)} input, {by_target.get('receipt', 0)} receipt, {by_target.get('engine', 0)} engine-configuration. Detected {ms['summary']['detected']}; correctly ignored {ms['summary']['correctly_ignored']}; blind spots {len(blind)}; false positives {len(ms['summary']['false_positives'])}.", "", md_table(["id", "mutation", "target", "expected detection", "detected", "engine verdict", "status", "detecting invariants", "missed", "note"], [[r["id"], r["mutation"], r["target"], fmt(r["expected_detection"]), fmt(r["actual_detection"]), r["observed"], f"**{r['status']}**" if r["status"] in ("BLIND_SPOT", "FALSE_POSITIVE") else r["status"], ", ".join(r["detecting_invariants"]) or "none", ", ".join(r["missed_invariants"]) or "none", r.get("note") or "none"] for r in res]), ""]
    body += ["### Blind spots and partial detections (published, not suppressed)", ""]
    body += [f"- **{r['id']} {r['mutation']}** — engine verdict {r['observed']} (missed detection). {r['note']}" for r in blind]
    body += [f"- **{r['id']} {r['mutation']}** — detected by other invariants, but the intended check missed it: {', '.join(r['missed_invariants'])}. {r.get('note', '')}" for r in partial]
    d = e["dependencies"]
    body += ["", "## Dependency-aware validity demo", "", f"- Impact of changing `design`: descendants marked stale = {fmt(d['impact_of_design_change']['descendants_marked_stale'])}; recomputed = {fmt(d['impact_of_design_change']['recomputed'])}; declared false = {fmt(d['impact_of_design_change']['declared_false'])}.", f"- After design v2→v3: stale = {fmt(d['evaluation_after_change']['stale'])}; publication blocked = {fmt(d['evaluation_after_change']['publication_blocked'])}.", f"- Revalidation with identical output: {d['revalidate_unchanged']['result']}; still pending: {fmt(d['revalidate_unchanged']['descendants_still_pending'])}.", f"- Revalidation with changed output: {d['revalidate_changed']['result']}; still pending: {fmt(d['revalidate_changed']['descendants_still_pending'])}.", "", "Staleness is not falsity: no stale node was declared false or silently recomputed."]
    det = e["determinism"]
    body += ["", "## Determinism across hash seeds", "", md_table(["PYTHONHASHSEED", "exit", "receipt file sha256"], [[r["seed"], r["exit"], r["receipt_sha256_of_file"]] for r in det["runs"]]), "", f"Byte-identical: **{fmt(det['byte_identical'])}** (clock fixed via SOURCE_DATE_EPOCH)."]
    body += ["", "## Receipt statement", "", "> A receipt supports integrity, provenance, and replayability. It does not establish scientific truth, accuracy, safety, or fitness for use.", "", f"Signature state of every fixture receipt: {fmt(sorted({f['signature_state'] for f in fx}))} (no signing key configured; no signature fabricated)."]
    status = "FAIL" if matched != len(fx) else ("PASS_WITH_BLIND_SPOTS" if blind else "PASS")
    hdr = _hdr(
        status=status,
        what_was_expected=f"{len(fx)} fixtures with declared status/exit/evidence; {len(expected_det)} mutations that must be detected and {len(res) - len(expected_det)} that must be ignored",
        what_was_examined=f"{len(fx)} fixture corpora; {by_target.get('input', 0) + by_target.get('receipt', 0)} mutated corpora/receipts + {by_target.get('engine', 0)} engine-configuration mutation",
        what_actually_ran="engine verify on every fixture; mutation harness; dependency impact + 2 revalidations; 3 hash-seed runs",
        what_passed=f"{matched}/{len(fx)} fixtures matched (including {len(abst_fx)} whose correct outcome is ABSTAIN); {ms['summary']['detected']}/{len(expected_det)} required detections; {ms['summary']['correctly_ignored']} neutral mutation(s) correctly ignored; receipts byte-identical across hash seeds",
        what_failed=f"{len(fx) - matched} fixture mismatches; missed detections: {', '.join(r['id'] for r in blind) or 'none'}; false positives: {fmt(ms['summary']['false_positives'])}",
        what_abstained=f"fixtures with ABSTAIN verdict (as declared): {', '.join(abst_fx) or 'none'}; mutations with ABSTAIN verdict: {', '.join(abst_mut) or 'none'}",
        what_remains_unresolved=f"blind spots {', '.join(r['id'] for r in blind) or 'none'}; partial detections {', '.join(r['id'] for r in partial) or 'none'}",
        what_this_result_does_not_prove="that the engine detects defect classes outside the mutation set; that any receipt is authentic (receipts are UNSIGNED)",
    )
    w.text("01-engine-verification.md", report("01 — Engine verification", hdr, "\n".join(body)))
    w.json("01-engine-verification.json", e)


# ------------------------------------------------------------------ 02 github
def protection_text(r: dict[str, Any], authenticated_admin: bool) -> str:
    bp = r["detail"].get("branch_protection")
    if isinstance(bp, dict) and bp.get("enabled"):
        return f"enabled (required reviews {fmt(bp.get('required_reviews'))}, status checks {fmt(bp.get('required_status_checks'))})"
    if isinstance(bp, dict) and bp.get("http") == 404:
        if "not protected" in str(bp.get("message", "")).lower() or authenticated_admin:
            return "not protected (HTTP 404 'Branch not protected')" if "not protected" in str(bp.get("message", "")).lower() else "not protected (HTTP 404; the same token reads protection on other repos)"
    return fmt(bp)


def alert_text(x: Any) -> str:
    if isinstance(x, dict) and "open" in x:
        n = f">={x['open']} (first page only)" if x.get("lower_bound") or x["open"] >= 100 else str(x["open"])
        extra = f" [{fmt(x.get('types'))}]" if x.get("types") else ""
        return f"open {n}{extra}"
    return fmt(x)


def r02(w: ReportWriter, g: dict[str, Any]) -> None:
    gh = g["gh"]
    cov = gh_coverage(g)
    admin = any(isinstance(r["detail"].get("branch_protection"), dict) and r["detail"]["branch_protection"].get("enabled") for r in gh["repos"])
    rows = []
    tally = Counter()
    nt_axis_repos = 0
    for r in sorted(gh["repos"], key=lambda x: (bool(x.get("archived")), x["name"].lower())):
        sc = g["scores"][r["name"]]
        cells = [ABBR[sc[a]["state"]] for a in AXES]
        tally.update(sc[a]["state"] for a in AXES)
        nt_axis_repos += any(sc[a]["state"] == "NOT_TESTED" for a in AXES)
        rows.append([r["name"] + (" (archived)" if r.get("archived") else "") + (" (private)" if r.get("private") else ""), *cells])
    body = [
        f"Org: `{gh['org']}` · authenticated: {fmt((gh.get('auth') or {}).get('authenticated'))} · listing: {gh['listing'].get('pages', 'UNKNOWN')} pages, denominator {gh['listing'].get('denominator_state', 'UNKNOWN')} · HTTP requests: {fmt((gh.get('http') or {}).get('requests'))}",
        "",
        HOST_NOTE,
        "",
        "## Scorecard (P=PASS, ~=PARTIAL, F=FAIL, NT=NOT_TESTED)",
        "",
        md_table(["repo", *AXES], rows),
        "",
        f"Axis-state totals: PASS {tally.get('PASS', 0)}, PARTIAL {tally.get('PARTIAL', 0)}, FAIL {tally.get('FAIL', 0)}, NOT_TESTED {tally.get('NOT_TESTED', 0)}.",
        "",
        "## Installability smoke tests",
        "",
        "Test attribution: REPO_DEFECT (cause identified in the repository), REPO_DEFECT_UNCONFIRMED (no harness/host cause recognised; confirm on Linux CI), HOST_LIMITED (Windows host limitation), UNRESOLVED / POSSIBLE_HARNESS (recorded under the interim harness; not charged to the repository), NOT_TESTED (not run or harness failure). Time-to-first-run = seconds from venv creation to the first successful import, --help, quickstart command or passing test suite; NOT_TESTED when none was attempted.",
        "",
    ]
    srows = []
    for n, s in sorted(g["smoke"].items()):
        if s.get("install_ok") == NOT_TESTED:
            continue
        t = s.get("tests") or {}
        srows.append([n, s.get("kind"), fmt(s.get("install_ok")), fmt(s.get("build_ok", NOT_TESTED)), fmt(s.get("imports_ok", NOT_TESTED)), fmt(s.get("help_ok", NOT_TESTED)), fmt(s.get("quickstart_ok", NOT_TESTED)), t.get("state", NOT_TESTED), counts_text(t.get("summary")) if t.get("state") not in (NOT_TESTED, None) else NOT_TESTED, t.get("attribution", "none"), t.get("reason", "none"), fmt(s.get("time_to_first_run_s")), smoke_source(s)])
    body += [md_table(["repo", "kind", "install", "build", "import", "--help", "quickstart", "tests", "test counts", "attribution", "reason", "time-to-first-run (s)", "evidence"], srows), ""]
    body += ["## Per-repository evidence", ""]
    for r in sorted(gh["repos"], key=lambda x: x["name"].lower()):
        sc = g["scores"][r["name"]]
        d = r["detail"]
        head = d.get("head") if isinstance(d.get("head"), dict) else {}
        lic = (r.get("license") or {}).get("spdx_id") if r.get("license") else "none"
        body += [f"### {r['name']}", "", f"- {r.get('html_url')} · visibility {r.get('visibility')} · archived {fmt(r.get('archived'))} · default {r.get('default_branch')} · HEAD {fmt((head or {}).get('sha'))[:12]} · pushed {r.get('pushed_at')} · size {r.get('size_kb')} KB · language {fmt(r.get('language'))} · stars {r.get('stars')} · forks {r.get('forks')} · watchers {fmt(r.get('watchers'))} · licence metadata {lic} · bus factor {fmt(bus_factor(r))}", f"- Dependabot {alert_text(d.get('dependabot_alerts'))} · code scanning {alert_text(d.get('code_scanning_alerts'))} · secret scanning {alert_text(d.get('secret_scanning_alerts'))} · branch protection {protection_text(r, admin)} · rulesets {fmt(d.get('rulesets'))}"]
        s = g["smoke"].get(r["name"])
        if s and s.get("steps"):
            body.append("- smoke commands: " + "; ".join(f"`{' '.join(str(a) for a in st.get('argv', [])[-4:])}` → {st.get('exit_code')} ({st.get('duration_s')} s)" for st in s["steps"][:8]))
        body += [f"  - **{a}**: {sc[a]['state']} — {sc[a]['evidence']}" for a in AXES]
        body.append("")
    hdr = _hdr(
        status="ABSTAIN" if cov["denominator_state"] != "OBSERVED" else ("ATTENTION" if tally.get("FAIL") else "PASS"),
        what_was_expected=f"every repository of {gh['org']}: {cov['artifacts_expected']}",
        what_was_examined=f"{cov['artifacts_discovered']} repos listed; {cov['artifacts_examined']} shallow-cloned and file-analysed",
        what_actually_ran=f"REST/GraphQL collection; clones; secret + risky-pattern scan; {cov['artifacts_functionally_tested']} clean-environment install/test runs",
        what_passed=f"{tally.get('PASS', 0)} axis results PASS across {len(gh['repos'])} repos",
        what_failed=f"{tally.get('FAIL', 0)} axis results FAIL",
        what_abstained=f"{tally.get('NOT_TESTED', 0)} axis results NOT_TESTED across {nt_axis_repos} repos",
        what_remains_unresolved=f"{cov['artifacts_not_tested']} repos not functionally tested (per-repo reasons in the coverage block); interim-harness test failures await a re-run under harness fix2",
        what_this_result_does_not_prove="code correctness, security, or fitness; scores are evidence summaries from heuristics labelled with confidence; " + HOST_NOTE,
    )
    w.text("02-github-audit.md", report("02 — GitHub organisation audit: szl-holdings", hdr, "\n".join(body), cov))
    w.json("02-github-audit.json", {"coverage": cov, "org": gh["org_meta"], "listing": gh["listing"], "repos": [{k: r[k] for k in r if k != "detail"} | {"detail": r["detail"], "scorecard": g["scores"][r["name"]], "smoke": g["smoke"].get(r["name"], NOT_TESTED), "files": {k: vv for k, vv in (g["files"].get(r["name"]) or {}).items() if k != "readme_text"}} for r in gh["repos"]], "lean": g.get("lean")})


# ------------------------------------------------------------------ 03 huggingface
def space_probe_text(a: dict[str, Any]) -> str:
    http = (a["functional"].get("http") or {})
    probes = http.get("probes", [])
    if not probes:
        return http.get("reason", NOT_TESTED)
    return "; ".join(f"{p['path']} → {p['status']} ({'<16' if isinstance(p.get('latency_ms'), (int, float)) and p['latency_ms'] < 16 else fmt(p.get('latency_ms'))} ms)" for p in probes)


def dataset_rows_text(fn: dict[str, Any]) -> str:
    sz = fn.get("size") or {}
    if sz.get("state") == "OBSERVED" and sz.get("splits"):
        return fmt(sz.get("num_rows"))
    return UNAVAILABLE


def pii_text(fn: dict[str, Any]) -> str:
    if "pii_patterns" not in fn:
        return NOT_TESTED
    if not fn["pii_patterns"]:
        return f"0 hits (first {fmt((fn.get('slice') or {}).get('rows_loaded'))} rows)"
    return f"{fmt(fn['pii_patterns'])} (first {fmt((fn.get('slice') or {}).get('rows_loaded'))} rows; manual review)"


def coherence_text(a: dict[str, Any]) -> list[str]:
    issues = list(a["model_class"]["coherence_issues"])
    for x in (a["functional"].get("headers") or {}).values():
        if x.get("state") == "INVALID":
            issues.append(f"{x.get('file')}: {x.get('detail', 'invalid header')} ({fmt(x.get('bytes'))} bytes)")
    return issues


def r03(w: ReportWriter, h: dict[str, Any]) -> None:
    hf = h["hf"]
    cov = hf_coverage(h)
    arts = [a for a in hf["artifacts"] if "files" in a]
    sp = [a for a in arts if a["kind"] == "space"]
    ms = [a for a in arts if a["kind"] == "model"]
    ds = [a for a in arts if a["kind"] == "dataset"]
    pc = (h.get("public_counts") or {}).get("counts", {})
    auth_public_spaces = sum(1 for a in sp if not a.get("private"))
    body = [f"Org `{hf['org']}` · authenticated listing: " + ", ".join(f"{k} {x['count']} ({x['denominator_state']})" for k, x in hf["listing"].items()) + f" · anonymous public counts: models {fmt(pc.get('models'))}, datasets {fmt(pc.get('datasets'))}, spaces {fmt(pc.get('spaces'))} (at {fmt((h.get('public_counts') or {}).get('observed_at'))})", ""]
    if isinstance(pc.get("spaces"), int) and auth_public_spaces != pc["spaces"]:
        body += [f"Reconciliation: {auth_public_spaces} non-private Spaces in the authenticated listing vs {pc['spaces']} in the anonymous listing — SZLHOLDINGS/README (org card Space) is public but absent from the anonymous author listing.", ""]
    body += ["## Card scorecard (P/~/F/NT)", "", md_table(["artifact", "kind", "private", *CARD_AXES, "capability w/o evidence"], [[a["id"].split("/", 1)[1], a["kind"], fmt(a.get("private")), *[ABBR[a["card"]["axes"][x]["state"]] for x in CARD_AXES], fmt(a["card"]["capability_without_evidence"])] for a in sorted(arts, key=lambda x: (x["kind"], x["id"].lower()))]), ""]
    body += ["## Spaces — runtime and read-only probes", "", TIMER_NOTE, "", md_table(["space", "private", "sdk", "hardware", "runtime (raw stage)", "http", "probes", "title"], [[a["id"].split("/", 1)[1], fmt(a.get("private")), a["functional"].get("sdk"), a["functional"].get("hardware"), a["functional"].get("runtime_stage_raw"), (a["functional"].get("http") or {}).get("state"), space_probe_text(a), next((p["title"] for p in (a["functional"].get("http") or {}).get("probes", []) if p.get("title")), "none")] for a in sp]), ""]
    body += ["## Models — artifact class, coherence, load", "", "Load state RUNTIME_UNAVAILABLE_NOT_TESTED = weights present but no torch/llama.cpp runtime in the audit environment (headers validated by HTTP range request instead); it is not a size judgement.", "", md_table(["model", "class", "library", "pipeline", "weights (bytes)", "config", "header check", "load", "downloads 30d", "mistakable-for-trained signals", "coherence issues"], [[a["id"].split("/", 1)[1], a["model_class"]["artifact_class"], a["library"], a["pipeline_tag"], a["model_class"]["weight_bytes"], (a["functional"].get("config") or {}).get("state"), "; ".join(f"{x.get('file', k)}: {x.get('state')}" for k, x in (a["functional"].get("headers") or {}).items()) or "none", load_label(a["functional"]), fmt(a.get("downloads_30d")), "; ".join(a["model_class"]["mistakable_for_trained_model"]) or "none", "; ".join(coherence_text(a)) or "none"] for a in sorted(ms, key=lambda x: x["id"].lower())]), ""]
    body += ["## Datasets — load, schema, counts, sensitive patterns", "", md_table(["dataset", "private", "splits", "slice", "rows loaded", "observed rows", "card schema match", "direct file parse", "PII patterns", "downloads 30d"], [[a["id"].split("/", 1)[1], fmt(a.get("private")), (a["functional"].get("splits") or {}).get("state"), (a["functional"].get("slice") or {}).get("state", NOT_TESTED), fmt((a["functional"].get("slice") or {}).get("rows_loaded", NOT_TESTED)), dataset_rows_text(a["functional"]), fmt((a["functional"].get("card_schema") or {}).get("schema_match", (a["functional"].get("card_schema") or {}).get("state"))), (a["functional"].get("direct_files") or {}).get("state", NOT_TESTED), pii_text(a["functional"]), fmt(a.get("downloads_30d"))] for a in sorted(ds, key=lambda x: x["id"].lower())]), ""]
    body += ["## Conformance corpora (most important functional test)", ""]
    mismatches = 0
    for c in h["conformance"].get("corpora", []):
        body.append(f"### {c['dataset']} ({c.get('type')})")
        if c.get("type") == "fixture_corpus":
            body.append(f"Declared fixtures: {c.get('declared_fixtures')} · paired verifier: `{c.get('verifier_repo')}` · card-pinned commit: `{c.get('card_pinned_commit')}`")
            for r in c.get("runs", []):
                if "results" not in r:
                    body.append(f"- {r.get('verifier')}: {r.get('state')} {r.get('detail', r.get('reason', ''))}")
                    continue
                mismatches += len(r.get("mismatched") or [])
                body.append(f"- **{r['verifier']}** → {r['matched']}/{r['fixtures']} declared outcomes reproduced; mismatched: {fmt(r['mismatched'])}")
                body.append(md_table(["fixture", "declared", "observed", "exit", "exit consistent", "match"], [[x["file"], x["declared"], x["observed"], x.get("exit_code"), fmt(x.get("exit_consistent_with_verdict")), fmt(x["match"])] for x in r["results"]]))
        else:
            for r in c.get("runs", []):
                body.append(f"- `{r.get('command')}` → exit {r.get('exit_code')} in {r.get('duration_s')} s")
            body.append(f"- all exit zero: {fmt(c.get('all_exit_zero', NOT_TESTED))}")
        body.append("")
    load_fail = [a for a in ds if "LOAD_FAILED" in str((a["functional"].get("slice") or a["functional"].get("splits") or {}).get("state"))]
    invalid_hdr = [a for a in ms if any(x.get("state") == "INVALID" for x in (a["functional"].get("headers") or {}).values())]
    incoherent = [a for a in ms if a["model_class"]["coherence_issues"]]
    responded = [a for a in sp if (a["functional"].get("http") or {}).get("state") == "RESPONDED"]
    hdr = _hdr(
        status="ABSTAIN" if cov["denominator_state"] != "OBSERVED" else ("FAIL" if (load_fail or mismatches or invalid_hdr) else "PASS"),
        what_was_expected=f"every model, dataset and Space authored by {hf['org']} ({cov['artifacts_expected']} in the authenticated listing)",
        what_was_examined=f"{cov['artifacts_examined']} artifacts (metadata, card, file list)",
        what_actually_ran=f"Hub API enumeration; card scoring; Space runtime + read-only HTTP probes; config/header/array loads; datasets-server slices; conformance replay ({len(h['conformance'].get('corpora', []))} corpora)",
        what_passed=f"{len(responded)} Spaces responded; {sum(1 for a in ds if (a['functional'].get('slice') or {}).get('state') == 'LOADED')} dataset slices loaded; {sum(1 for a in ms if (a['functional'].get('load') or {}).get('state') == 'LOADED')} small-array models loaded",
        what_failed=f"{len(load_fail)} dataset loads failed; {mismatches} conformance fixture mismatch(es); {len(invalid_hdr)} model(s) with an invalid weights-extension file; {len(incoherent)} model(s) with file-set/framework coherence issues",
        what_abstained=f"{cov['artifacts_not_tested']} artifacts not functionally tested (reasons listed)",
        what_remains_unresolved="large-weight inference quality; private Space behaviour; sleeping Spaces (not woken)",
        what_this_result_does_not_prove="model quality, safety, or that any card claim is true beyond the checks listed",
    )
    w.text("03-huggingface-audit.md", report("03 — Hugging Face estate audit: SZLHOLDINGS", hdr, "\n".join(body), cov))
    w.json("03-huggingface-audit.json", {"coverage": cov, "listing": hf["listing"], "public_counts": h["public_counts"], "artifacts": [{k: a[k] for k in a if k != "readme_text"} for a in hf["artifacts"]], "conformance": h["conformance"]})


# ------------------------------------------------------------------ 04 reconcile
STANDARD_MEDIA = re.compile(r"^(application/vnd\.(dsse|in-toto)\+json|app/vnd\.dsse\+json|https://in-toto\.io/|https://slsa\.dev/)")
TEST_IDS = re.compile(r"(?i)(example|fixture|test|dummy|sample)")


def schema_buckets(ids: dict[str, list[str]]) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    std = {k: v for k, v in ids.items() if STANDARD_MEDIA.search(k)}
    test = {k: v for k, v in ids.items() if k not in std and TEST_IDS.search(k)}
    estate = {k: v for k, v in ids.items() if k not in std and k not in test}
    return std, test, estate


def version_skew(ids: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fam: dict[str, dict[str, set[str]]] = {}
    for sid, repos in ids.items():
        m = re.search(r"[./]v?(\d+(?:\.\d+)*)(?:\+json)?$|;v=(\d+)$", sid)
        if not m:
            continue
        ver = m.group(1) or m.group(2)
        base = re.sub(r"[./]v?\d+(?:\.\d+)*(\+json)?$|;v=\d+$", "", sid)
        fam.setdefault(base, {}).setdefault(ver, set()).update([sid])
        fam[base].setdefault("__repos__", set()).update(repos)
    skew, naming = [], []
    for base, vers in sorted(fam.items()):
        repos = sorted(vers.pop("__repos__", set()))
        if len(vers) > 1:
            skew.append({"family": base, "versions": sorted(vers), "ids": sorted(i for s in vers.values() for i in s), "repos": repos})
        for ver, idset in vers.items():
            if len(idset) > 1:
                naming.append({"family": base, "version": ver, "spellings": sorted(idset), "repos": repos})
    return skew, naming


def r04(w: ReportWriter, rec: dict[str, Any], h: dict[str, Any], g: dict[str, Any]) -> None:
    missing = [r for r in rec["source_to_hf"] if r["missing_targets"]]
    std, test, estate = schema_buckets(rec["receipt_schema_ids"])
    skew, naming = version_skew(estate)
    body = ["## HF artifact → canonical source", "", md_table(["artifact", "kind", "private", "canonical source", "state", "source newer by (days)"], [[r["artifact"], r["kind"], fmt(r["private"]), r["canonical_source"], r["state"], fmt(r["source_newer_by_days"])] for r in rec["hf_to_source"]]), ""]
    body += ["## Source repo → HF target", "", md_table(["repo", "archived", "state", "README HF targets", "missing targets", "HF artifacts linking back"], [[r["repo"], fmt(r["archived"]), r["state"], ", ".join(r["readme_hf_targets"]) or "none", ", ".join(r["missing_targets"]) or "none", ", ".join(r["hf_artifacts_linking_back"]) or "none"] for r in rec["source_to_hf"] if r["state"] != "NOT_A_PUBLISHER" or r["missing_targets"]]), ""]
    body += ["## Version drift (pinned source commit vs source HEAD)", "", md_table(["artifact", "repo", "pinned", "source HEAD"], [[d["artifact"], d["repo"], d["pinned"], d["source_head"]] for d in rec["version_drift"]]) if rec["version_drift"] else "none observed", ""]
    body += ["## Naming inconsistencies", ""]
    body += [md_table(["HF", "GitHub", "issue"], [[n["hf"], n["github"], n["issue"]] for n in rec["naming_inconsistencies"]])] if rec["naming_inconsistencies"] else ["none observed between HF ids and GitHub repo names"]
    body += ["", md_table(["schema family", "version", "spellings", "repos"], [[n["family"], n["version"], ", ".join(n["spellings"]), ", ".join(n["repos"])] for n in naming]) if naming else "no separator/spelling variants within a schema version", ""]
    body += ["## Receipt/schema identifiers in use", "", f"{len(rec['receipt_schema_ids'])} receipt-like identifiers found in cloned sources: {len(estate)} estate-defined, {len(std)} standard media types (DSSE/in-toto), {len(test)} test/example ids. Scan scope: {rec.get('receipt_schema_scan_not_tested') and str(len(rec['receipt_schema_scan_not_tested'])) + ' repos NOT_TESTED' or 'all cloned repos'}.", ""]
    body += [md_table(["estate schema id", "repos"], [[k, ", ".join(vv)] for k, vv in sorted(estate.items())]), ""]
    body += ["### Version skew within an estate schema family (distinct version numbers only)", "", md_table(["family", "versions", "ids", "repos"], [[s["family"], ", ".join(s["versions"]), ", ".join(s["ids"]), ", ".join(s["repos"])] for s in skew]) if skew else "none", ""]
    gh_at = g["gh"].get("completed_at")
    pc = (h.get("public_counts") or {})
    body += ["## Public inventory recount vs stated counts", "", f"HF anonymous listing at {fmt(pc.get('observed_at'))}: " + ", ".join(f"{k} {v}" for k, v in (pc.get("counts") or {}).items()) + f". GitHub: {sum(1 for r in g['gh']['repos'] if not r.get('private'))} public of {len(g['gh']['repos'])} discovered repos (authenticated org listing at {gh_at}).", ""]
    drift = rec.get("inventory_drift", [])
    body += [md_table(["location", "private source", "claim", "verdict", "evidence"], [[c["location"], fmt(c.get("source_private", False)), c["text"][:120], c["verdict"], c["evidence"]] for c in drift]) if drift else "all inventory counts matched", ""]
    cov = {
        "artifacts_expected": f"{len(rec['hf_to_source'])} HF artifacts + {len(rec['source_to_hf'])} repos",
        "artifacts_discovered": f"{len(rec['hf_to_source'])} HF artifacts; {len(rec['source_to_hf'])} repos",
        "artifacts_examined": f"{len(rec['hf_to_source'])} HF cards; {sum(1 for r in g['gh']['repos'] if r['clone'].get('ok'))} repo READMEs (cloned repos)",
        "artifacts_functionally_tested": NOT_TESTED + " (reconciliation is link/metadata based)",
        "artifacts_not_tested": sum(1 for r in g["gh"]["repos"] if not r["clone"].get("ok")),
        "denominator_state": "OBSERVED",
        "not_tested_reasons": {r["name"]: ("archived (README not cloned)" if r.get("archived") else (r["clone"].get("reason") or "clone failed")) for r in g["gh"]["repos"] if not r["clone"].get("ok")},
    }
    bad = bool(rec["orphaned_hf"] or missing or rec["version_drift"] or any(c["verdict"] == "CONTRADICTED" for c in drift))
    hdr = _hdr(status="FAIL" if bad else "PASS", what_was_expected="every HF artifact mapped to a source and every publishing repo mapped to a target", what_was_examined=cov["artifacts_examined"], what_actually_ran="link extraction from cards/READMEs, inventory lookups, pinned-SHA comparison, schema-id scan of cloned sources", what_passed=f"{sum(1 for r in rec['hf_to_source'] if r['state'] == 'LINKED')} artifacts linked to a living source", what_failed=f"{len(rec['orphaned_hf'])} artifacts without a living source link; {len(missing)} repos link HF targets that do not exist; {len(rec['version_drift'])} pinned-version drifts; inventory claims {sum(1 for c in drift if c['verdict'] == 'CONTRADICTED')} CONTRADICTED, {sum(1 for c in drift if c['verdict'] == 'STALE')} STALE", what_abstained="relationships not written in any card/README are invisible to this method", what_remains_unresolved="whether unlinked artifacts have an owner outside these surfaces", what_this_result_does_not_prove="that linked artifacts were built from the linked source")
    w.text("04-reconciliation.md", report("04 — Cross-surface reconciliation", hdr, "\n".join(body), cov))
    w.json("04-reconciliation.json", rec | {"estate_schema_ids": estate, "standard_media_types": std, "test_ids": test, "version_skew_normalised": skew, "schema_spelling_variants": naming})


# ------------------------------------------------------------------ 05 claims
def r05(w: ReportWriter, cl: dict[str, Any], g: dict[str, Any], h: dict[str, Any]) -> None:
    claims = cl["claims"]
    cnt = Counter(c["verdict"] for c in claims)
    types = Counter(c["claim_type"] for c in claims)
    order = {"CONTRADICTED": 0, "STALE": 1, "VERIFIED": 2, "UNVERIFIABLE": 3}
    rows = [[c["verdict"], c["claim_type"], c["value"], c.get("unit") or "none", "private" if c.get("source_private") else "public", c["location"], c["text"][:160], c["verification_method"], c["observed_value"], c["evidence"] or "none"] for c in sorted(claims, key=lambda x: (order[x["verdict"]], x["claim_type"], x["location"]))]
    f = cl["facts"]
    lean = f.get("lean") or {}
    cons_rows = []
    for c in cl.get("consistency", []):
        vals = []
        for k, locs in c["values"].items():
            shown, more = capped(locs, 5, "state/claims.json")
            vals.append(f"{k}: {', '.join(shown)} {more}".strip())
        cons_rows.append([c["claim_type"], c.get("unit") or "none", c.get("basis", "any"), " ‖ ".join(vals), c.get("locations_total")])
    body = [
        f"Facts used: HF anonymous listing at {fmt(f.get('public_counts_at'))} (spaces {fmt((f.get('public_counts') or {}).get('spaces'))}, models {fmt((f.get('public_counts') or {}).get('models'))}, datasets {fmt((f.get('public_counts') or {}).get('datasets'))}); GitHub public repos {fmt((f.get('public_counts') or {}).get('repos'))} from the authenticated org listing at {fmt(f.get('repos_counted_at'))}; authenticated totals {fmt(f.get('auth_counts'))}; Lean HEAD {str(lean.get('head_sha'))[:8]} and pinned {str(lean.get('pinned_sha'))[:8]} counted with the org's own counter (which also counts axiom-like words in comments — see 11).",
        "",
        "Verdicts: " + ", ".join(f"{k} {v}" for k, v in cnt.items()) + " · claim types: " + ", ".join(f"{k} {v}" for k, v in types.items()),
        "",
        "## Cross-location consistency (same unit and same basis only)",
        "",
        md_table(["type", "unit", "basis", "values → locations", "locations"], cons_rows) if cons_rows else "none",
        "",
        "## Every extracted claim",
        "",
        md_table(["verdict", "type", "value", "unit", "visibility", "location", "claim text", "method", "observed", "evidence"], rows),
    ]
    readmes = sum(1 for x in g["files"].values() if x.get("readme_text"))
    cards = sum(1 for a in h["hf"]["artifacts"] if a.get("readme_text"))
    cov = {
        "artifacts_expected": f"{len(g['gh']['repos'])} repo READMEs + org profile + {len(h['hf']['artifacts'])} HF cards",
        "artifacts_discovered": f"{readmes} repo READMEs (cloned repos) + org profile + {cards} HF cards",
        "artifacts_examined": readmes + cards + 1,
        "artifacts_functionally_tested": f"{len(claims)} claims extracted and verified",
        "artifacts_not_tested": len(g["gh"]["repos"]) - readmes,
        "denominator_state": "OBSERVED",
        "not_tested_reasons": {r["name"]: ("archived (README not cloned)" if r.get("archived") else (r["clone"].get("reason") or "no README")) for r in g["gh"]["repos"] if not (g["files"].get(r["name"]) or {}).get("readme_text")},
    }
    hdr = _hdr(status="FAIL" if cnt.get("CONTRADICTED") else ("ATTENTION" if cnt.get("STALE") else "PASS"), what_was_expected="every quantitative/categorical claim in org+repo READMEs and HF cards", what_was_examined=f"{len(claims)} distinct claims (deduplicated by location, type, value, unit)", what_actually_ran="regex extraction (code blocks skipped; section-heading dates inherited); live recount of inventory; Lean recount at HEAD and pinned revision; DOI handle resolution", what_passed=f"{cnt.get('VERIFIED', 0)} VERIFIED", what_failed=f"{cnt.get('CONTRADICTED', 0)} CONTRADICTED", what_abstained=f"{cnt.get('UNVERIFIABLE', 0)} UNVERIFIABLE (incl. subset/scope-qualified figures)", what_remains_unresolved=f"{cnt.get('STALE', 0)} STALE (drifted dated observations — not false)", what_this_result_does_not_prove="claims phrased in ways the extractor does not match; DOI existence does not verify content")
    w.text("05-claims-verification.md", report("05 — Claims verification", hdr, "\n".join(body), cov))


# ------------------------------------------------------------------ 06 security
def r06(w: ReportWriter, g: dict[str, Any]) -> None:
    rows, risk_rows = [], []
    vendored_hits = 0
    for n, f in sorted(g["files"].items()):
        for hit in f.get("secrets", {}).get("hits", []):
            rows.append([n, hit["path"], hit["line"], hit["type"], SECRET_CONF.get(hit["type"], "UNKNOWN"), fmt(hit["likely_live"]), hit["note"] or "none"])
        for k, x in f.get("code_risks", {}).items():
            locs = list(dict.fromkeys(x["locations"]))
            own = [loc for loc in locs if not VENDORED.search(loc.rsplit(":", 1)[0])]
            vendored_hits += len(locs) - len(own)
            if own:
                risk_rows.append([n, k, len(own), ", ".join(own[:3]) + (f" (+{len(own) - 3} more)" if len(own) > 3 else "")])
    alerts, unav = [], Counter()
    for r in g["gh"]["repos"]:
        d = r["detail"]
        for key in ("dependabot_alerts", "code_scanning_alerts", "secret_scanning_alerts"):
            x = d.get(key)
            if isinstance(x, dict) and "state" in x:
                unav[(key, x.get("http"))] += 1
        alerts.append([r["name"], alert_text(d.get("dependabot_alerts")), alert_text(d.get("code_scanning_alerts")), alert_text(d.get("secret_scanning_alerts"))])
    live = [x for x in rows if x[5] == "yes"]
    platform_secret_repos = [r["name"] for r in g["gh"]["repos"] if isinstance(r["detail"].get("secret_scanning_alerts"), dict) and r["detail"]["secret_scanning_alerts"].get("open")]
    body = ["Values are never printed. Each hit carries only location, type and a non-reversible fingerprint (in JSON).", "", f"Files scanned: {sum(f.get('secrets', {}).get('files_scanned', 0) for f in g['files'].values())}; skipped (binary/oversize/vendor): {sum(f.get('secrets', {}).get('files_skipped', 0) for f in g['files'].values())}.", "", "## Secret-pattern hits", "", "`pattern confidence` is the specificity of the matched pattern; `likely live` also accounts for context (test path, rule file, placeholder, key header without body).", "", md_table(["repo", "path", "line", "type", "pattern confidence", "likely live", "context"], rows) if rows else "none", "", f"CRITICAL_MANUAL_REVIEW items (likely live, local scan): {len(live)}. Repositories with open GitHub secret-scanning alerts (class and count only): {', '.join(platform_secret_repos) or 'none'}.", "", "## Risky code patterns (location only; each needs human review)", "", f"Distinct sites only; {vendored_hits} matches in vendored/minified third-party files excluded.", "", md_table(["repo", "pattern", "distinct sites", "first locations"], risk_rows), "", "## Platform alert visibility", "", "Counts of 100 are first-page lower bounds (the API was not paginated in this run).", "", md_table(["repo", "Dependabot", "code scanning", "secret scanning"], alerts), "", "## This tool's own security limitations", "", "- Clean-environment smoke tests execute repository code inside a venv with a stripped environment and redirected HOME/APPDATA/HF_HOME. This is process isolation, not a sandbox: code could still reach the network or the OS credential store.", "- `gh` CLI is used for authenticated clones; the token stays in the OS keyring and is never written to reports, logs or the HTTP cache (Authorization headers are not cached; URLs are redacted).", "- Entropy/pattern scanning has false negatives (custom formats) and false positives (patterns inside rules/tests)."]
    cov = {
        "artifacts_expected": f"{len(g['gh']['repos'])} repositories",
        "artifacts_discovered": len(g["gh"]["repos"]),
        "artifacts_examined": f"{len(g['files'])} cloned repositories scanned (HEAD only)",
        "artifacts_functionally_tested": len(g["files"]),
        "artifacts_not_tested": len(g["gh"]["repos"]) - len(g["files"]),
        "denominator_state": "OBSERVED",
        "not_tested_reasons": {r["name"]: ("archived (not cloned)" if r.get("archived") else (r["clone"].get("reason") or "clone failed")) for r in g["gh"]["repos"] if r["name"] not in g["files"]},
    }
    ab = "; ".join(f"{k.replace('_alerts', '').replace('_', '-')} UNAVAILABLE {n}/{len(g['gh']['repos'])} (HTTP {code})" for (k, code), n in sorted(unav.items(), key=lambda kv: str(kv[0])))
    hdr = _hdr(status="FAIL" if (live or platform_secret_repos) else "PASS", what_was_expected="secret and unsafe-pattern scan of every cloned repository; platform alert counts for every repository", what_was_examined=cov["artifacts_examined"], what_actually_ran="pattern+entropy secret scan; static risky-pattern scan; alert API queries", what_passed=f"{len(g['files']) - len({x[0] for x in live})} scanned repos with no likely-live credential in the local scan", what_failed=f"{len(live)} likely-live local hits; {len(platform_secret_repos)} repos with open platform secret-scanning alerts", what_abstained=ab or "none", what_remains_unresolved="git history (only HEAD scanned); blobs >2MB not fetched by partial clone", what_this_result_does_not_prove="absence of secrets in git history, CI logs, or HF repos")
    w.text("06-security-findings.md", report("06 — Security findings (locations and classes only)", hdr, "\n".join(body), cov))


# ------------------------------------------------------------------ 07 investor
def r07(w: ReportWriter, g: dict[str, Any], h: dict[str, Any], z: dict[str, Any], cl: dict[str, Any]) -> None:
    gh = g["gh"]
    smoke = g["smoke"]
    runnable = sorted(n for n, s in smoke.items() if s.get("install_ok") is True and (s.get("tests") or {}).get("state") == "PASSED")
    install_only = sorted(n for n, s in smoke.items() if s.get("install_ok") is True and n not in runnable)
    broken = sorted(n for n, s in smoke.items() if s.get("install_ok") is False)
    sp = [a for a in h["hf"]["artifacts"] if a["kind"] == "space" and "files" in a]
    pub_sp = [a for a in sp if not a.get("private")]
    probed = [a for a in pub_sp if (a["functional"].get("http") or {}).get("probes")]
    ok_root = [a for a in probed if any(p["path"] == "/" and p["status"] == 200 for p in a["functional"]["http"]["probes"])]
    not_probed = [a for a in pub_sp if a not in probed]
    models = [a for a in h["hf"]["artifacts"] if a["kind"] == "model" and "files" in a]
    cls = Counter(a["model_class"]["artifact_class"] for a in models)
    top = sorted([a for a in h["hf"]["artifacts"] if isinstance(a.get("downloads_30d"), int)], key=lambda a: -a["downloads_30d"])[:10]
    langs = Counter(r.get("language") or "none" for r in gh["repos"] if not r.get("archived"))
    lic = Counter(((r.get("license") or {}) or {}).get("spdx_id", "NONE") if r.get("license") else "NONE" for r in gh["repos"] if not r.get("private"))
    crit = sorted([f for f in z["findings"] if f["severity"] in ("CRITICAL", "HIGH")], key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(f["confidence"], 3)))
    stale = sum(1 for c in cl["claims"] if c["verdict"] == "STALE")
    contra = sum(1 for c in cl["claims"] if c["verdict"] == "CONTRADICTED")
    body = [
        "Only measured facts. No valuation, market or fundraising commentary.",
        "",
        "## What exists and is independently runnable today (measured)",
        f"- Installed in a clean venv **and** passed their own test suite: {len(runnable)} — {', '.join(runnable) or 'none'}",
        f"- Installed; tests failed, unresolved or not run: {len(install_only)} — {', '.join(install_only) or 'none'}",
        f"- Failed clean install: {len(broken)} — {', '.join(broken) or 'none'}",
        f"- Public Spaces: {len(ok_root)} of {len(probed)} probed returned HTTP 200 at `/`; {len(not_probed)} public Space(s) not probed ({', '.join(a['id'].split('/')[1] + ': ' + (a['functional'].get('http') or {}).get('reason', NOT_TESTED) for a in not_probed) or 'none'}); {len(sp) - len(pub_sp)} private Spaces not probed.",
        "",
        "## Demonstrated vs asserted",
        f"- Claims: {len(cl['claims'])}; VERIFIED {sum(1 for c in cl['claims'] if c['verdict'] == 'VERIFIED')}, STALE {stale}, CONTRADICTED {contra}, UNVERIFIABLE {sum(1 for c in cl['claims'] if c['verdict'] == 'UNVERIFIABLE')} (see 05).",
        "- Model repositories by measured class (TRAINED_WEIGHTS/TRAINED_ADAPTER = neural-network weight files present; SMALL_ARRAYS = numpy arrays only):",
        *bullets(f"{k}: {v}" for k, v in cls.most_common()),
        "- Conformance: " + "; ".join(f"{c['dataset']}: " + ", ".join(f"{r.get('verifier')} {r.get('matched')}/{r.get('fixtures')}" for r in c.get("runs", []) if "fixtures" in r) for c in h["conformance"].get("corpora", []) if c.get("type") == "fixture_corpus"),
        "",
        "## Pre-launch, simulated or historical (as labelled by the estate itself)",
        "- Artifacts tagged roadmap / test-fixture / simulated / synthetic on HF:",
        *bullets(sorted(a["id"] for a in h["hf"]["artifacts"] if set(a.get("tags", [])) & {"roadmap", "test-fixture", "simulated", "synthetic"})),
        f"- Claims explicitly marked historical in text: {sum(1 for c in cl['claims'] if 'historical' in c['evidence'].lower())}",
        "",
        "## Concentration risk",
        "- Primary languages (non-archived repos): " + ", ".join(f"{k} {v}" for k, v in langs.most_common(8)),
        *[f"- {s['type']}: {fmt(s['evidence'])}" for s in z.get("spof", [])],
        "- Contributor figures are per GitHub account (type User) and do not merge aliases of the same person or exclude automation identities; treat concentration as a lower bound.",
        "",
        "## License and IP clarity (public repos, GitHub licence metadata)",
        "- " + ", ".join(f"{k} {v}" for k, v in lic.most_common()),
        "",
        "## Dependency and supply-chain exposure",
        f"- Repos with a lockfile: {sum(1 for f in g['files'].values() if f.get('lockfiles'))} of {len(g['files'])} cloned.",
        f"- Dependabot alert data visible for {sum(1 for r in gh['repos'] if isinstance(r['detail'].get('dependabot_alerts'), dict) and 'open' in r['detail']['dependabot_alerts'])} of {len(gh['repos'])} repos.",
        "",
        "## Flagships: backed by runnable artifacts?",
        md_table(["flagship", "install", "tests", "CI (merge gate)", "release", "bus factor"], [[n, fmt((smoke.get(n) or {}).get("install_ok", NOT_TESTED)), ((smoke.get(n) or {}).get("tests") or {}).get("state", NOT_TESTED), g["scores"].get(n, {}).get("ci", {}).get("state", "UNKNOWN"), g["scores"].get(n, {}).get("release_integrity", {}).get("state", "UNKNOWN"), fmt(z.get("bus_factor", {}).get(n, "UNKNOWN"))] for n in FLAGSHIPS]),
        "",
        "## Most-downloaded artifacts (HF downloads, last 30 days)",
        md_table(["artifact", "kind", "downloads 30d", "class"], [[a["id"], a["kind"], a["downloads_30d"], (a.get("model_class") or {}).get("artifact_class", "n/a")] for a in top]),
        "",
        "## Highest-severity findings (sorted by severity, then confidence)",
        *[f"{i}. **[{f['severity']}] {f['artifact']} — {f['title']}**: {' '.join(f['evidence'].split())[:300]}" for i, f in enumerate(crit[:3], 1)],
    ]
    unresolved = f"{sum(1 for s in smoke.values() if (s.get('tests') or {}).get('state') == 'UNRESOLVED')} test outcomes UNRESOLVED (interim harness); {sum(1 for a in sp if a.get('private'))} private Spaces not probed; HF inference quality not measured"
    hdr = _hdr(status=sev_status(z["findings"]), what_was_expected="investor-relevant facts from measured evidence only", what_was_examined="outputs of 02, 03, 04, 05", what_actually_ran="aggregation only (no new measurement)", what_passed=f"{len(runnable)} repos installed + tests passed; {len(ok_root)} public Spaces returned 200; {sum(1 for c in cl['claims'] if c['verdict'] == 'VERIFIED')} claims VERIFIED", what_failed=f"{len(crit)} CRITICAL/HIGH findings; {len(broken)} failed clean installs; {contra} CONTRADICTED claims", what_abstained="valuation, market, revenue: not measured, not discussed", what_remains_unresolved=unresolved, what_this_result_does_not_prove="commercial viability, product-market fit, or future maintenance")
    w.text("07-investor-view.md", report("07 — Investor view", hdr, "\n".join(body), rollup_coverage(g, h)))


# ------------------------------------------------------------------ 08 developer
CITABLE = re.compile(r"(\b10\.\d{4,9}/\S+|arxiv\.org/abs/|\barXiv:\d{4}\.\d{4,5}|@(article|inproceedings|misc)\{|^#+\s*(citation|cite this|how to cite)\b)", re.I | re.M)


def r08(w: ReportWriter, g: dict[str, Any], h: dict[str, Any], z: dict[str, Any], rec: dict[str, Any]) -> None:
    smoke = g["smoke"]
    ttfr = sorted([(n, s["time_to_first_run_s"]) for n, s in smoke.items() if isinstance(s.get("time_to_first_run_s"), (int, float))], key=lambda x: x[1])
    blockers = Counter()
    for s in smoke.values():
        if s.get("install_ok") is False:
            out = str(next((x.get("output", "") for x in s.get("steps", []) if x.get("step") == "install"), ""))
            key = "dependency not on PyPI / unresolvable" if "No matching distribution" in out or "Could not find a version" in out else ("packaging: setuptools flat-layout discovery / build backend error" if "flat-layout" in out or "backend" in out.lower() else "other install error")
            blockers[key] += 1
        tt = s.get("tests") or {}
        if tt.get("state") in ("FAILED", "ERROR"):
            blockers[f"test suite fails on clean install ({tt.get('attribution', 'unattributed')})"] += 1
        if tt.get("state") == "UNRESOLVED":
            blockers["test outcome UNRESOLVED (recorded under interim harness; re-run needed)"] += 1
        if s.get("time_to_first_run_s") == NOT_TESTED and s.get("install_ok") is True:
            blockers["NOT_TESTED: no entry point detected (no import, --help or quickstart attempted)"] += 1
        if s.get("time_to_first_run_s") == "NEVER_SUCCEEDED" and s.get("install_ok") is True:
            blockers["installs but no attempted entry point succeeded"] += 1
    missing_tests = [n for n, f in g["files"].items() if n in FLAGSHIPS and not f.get("test_files")]
    no_cff = sorted(r["name"] for r in g["gh"]["repos"] if not r.get("archived") and not r.get("private") and g["files"].get(r["name"]) and not g["files"][r["name"]]["presence"].get("CITATION.cff") and CITABLE.search(g["files"][r["name"]].get("readme_text", "")))
    names = [r["name"] for r in g["gh"]["repos"] if not r.get("archived")]
    base = {n: n.lower().replace("szl-", "").replace("-", "") for n in names}
    near = sorted({f"{a} ↔ {b}" for a in names for b in names if a < b and (base[a] == base[b] or (len(base[a]) > 4 and (base[a] in base[b] or base[b] in base[a])))})
    spaces_ok = []
    for a in h["hf"]["artifacts"]:
        if a["kind"] != "space" or a.get("private"):
            continue
        for p in (a.get("functional") or {}).get("http", {}).get("probes", []) if isinstance((a.get("functional") or {}).get("http"), dict) else []:
            if p["path"] == "/" and p["status"] == 200 and isinstance(p.get("latency_ms"), (int, float)):
                spaces_ok.append((a["id"], p["latency_ms"]))
    spaces_ok.sort(key=lambda x: x[1])
    dead_spaces = [a["id"] for a in h["hf"]["artifacts"] if a["kind"] == "space" and ((a.get("functional") or {}).get("http") or {}).get("state") == "DID_NOT_LOAD"]
    failing_ds = [a["id"] for a in h["hf"]["artifacts"] if a["kind"] == "dataset" and "LOAD_FAILED" in str(((a.get("functional") or {}).get("slice") or (a.get("functional") or {}).get("splits") or {}).get("state"))]
    misleading = [f"{f['artifact']}: {f['title']}" for f in z["findings"] if f["category"] in ("misleading-presentation", "unverified-claim")]
    mis_shown, mis_more = capped(misleading, 15, "09/11")
    first = next(((n, t) for n, t in ttfr if (smoke[n].get("tests") or {}).get("state") == "PASSED"), None)
    impl, impl_more = capped(z.get("verifier_implementations", []), 40, "state/zoomout.json")
    body = [
        "## Time-to-first-successful-run (clean venv, seconds)",
        "",
        "Definition: seconds from venv creation to the first successful import, `--help`, quickstart command or passing test suite. Import, build and test results are shown separately in 02.",
        "",
        md_table(["repo", "seconds", "tests", "evidence"], [[n, t, (smoke[n].get("tests") or {}).get("state"), smoke_source(smoke[n])] for n, t in ttfr]),
        "",
        "Flagships without a successful measured run:",
        *bullets(n for n in FLAGSHIPS if not isinstance(smoke.get(n, {}).get("time_to_first_run_s"), (int, float))),
        "",
        "## Onboarding blockers (ranked by frequency)",
        *[f"{i}. {k} — {c} repos" for i, (k, c) in enumerate(blockers.most_common(), 1)],
        "",
        "## Flagships with no test files",
        *bullets(missing_tests),
        "",
        "## Files matching verifier file-name patterns (lower bound; independence NOT_TESTED)",
        f"{len(z.get('verifier_implementations', []))} files match `verify|verifier|verify_receipt|receipt_verify|verify_chain|dsse_verify`.py outside tests {impl_more}",
        *bullets(impl),
        "",
        "## Near-duplicate repository names (merge/rename candidates; human judgement needed)",
        *bullets(near),
        "",
        "## Receipt-like schema identifiers",
        f"- {rec['receipt_schema_distinct']} identifiers found; see 04 for the estate/standard/test split and genuine version skew.",
        "",
        "## Missing CITATION.cff on repos whose README contains a DOI, arXiv id, BibTeX block or citation heading",
        *bullets(no_cff),
        "",
        "## For a newcomer",
        f"- Try first (fastest measured success with passing tests): {first[0] + f' ({first[1]} s)' if first else 'no repo met the bar'}",
        f"- Public Spaces answering `/` with 200 (fastest first; {TIMER_NOTE.lower()}): " + (", ".join(f"{i} ({'<16' if ms < 16 else fmt(ms)} ms)" for i, ms in spaces_ok[:5]) or "none"),
        f"- Can they succeed in five minutes? {'yes for ' + first[0] if first and first[1] <= 300 else 'not demonstrated'}",
        f"- Cards that may mislead {mis_more}:",
        *bullets(mis_shown),
        f"- Dead Spaces: {', '.join(dead_spaces) or 'none among publicly probeable Spaces'}",
        "- Datasets that fail to load:",
        *bullets(failing_ds),
    ]
    tested = sum(1 for s in smoke.values() if s.get("install_ok") in (True, False))
    fails = [n for n, s in smoke.items() if s.get("install_ok") is False]
    tfails = [n for n, s in smoke.items() if (s.get("tests") or {}).get("state") in ("FAILED", "ERROR")]
    cov = gh_coverage(g)
    hdr = _hdr(status="FAIL" if (fails or tfails) else "PASS", what_was_expected="developer-experience facts from measured runs", what_was_examined=f"{tested} clean-environment runs; HF functional results", what_actually_ran="aggregation of 02/03/04 measurements", what_passed=f"{len(ttfr)} repos reached a first successful run", what_failed=f"{len(fails)} failed install ({', '.join(fails) or 'none'}); {len(tfails)} test suites FAILED/ERROR with attribution", what_abstained=f"not smoke-tested: {cov['artifacts_not_tested']} of {len(g['gh']['repos'])} repos (reasons in 02 coverage block)", what_remains_unresolved=f"{sum(1 for s in smoke.values() if (s.get('tests') or {}).get('state') == 'UNRESOLVED')} UNRESOLVED test outcomes (interim harness)", what_this_result_does_not_prove="that failures reproduce on Linux; " + HOST_NOTE)
    w.text("08-developer-view.md", report("08 — Developer view", hdr, "\n".join(body), cov))


# ------------------------------------------------------------------ 09 gaps
def r09(w: ReportWriter, z: dict[str, Any], g: dict[str, Any], h: dict[str, Any]) -> None:
    s = z["systemic"]
    body = ["## Band-aids (root cause → structural fix; symptom-only fixes marked INSUFFICIENT)", ""]
    for b in z["bandaids"]:
        rec = b["symptom_only_recommendation"]
        body += [f"### {b['band_aid']}", f"- Evidence: {b['evidence']}", f"- Root cause: {b['root_cause']}", f"- Symptom-only recommendation: “{rec['text']}” → **{rec['verdict']}**", f"- Structural fix (replacement): {b['structural_fix']}", ""]
    groups = [c for c in s["contradictions"] if "values" in c]
    claims_c = [c for c in s["contradictions"] if "values" not in c]
    body += ["## Contradictions", "", "### Same fact stated with different values (same unit and basis)", ""]
    body += [md_table(["type", "unit", "basis", "value → locations"], [[c["claim_type"], c.get("unit") or "none", c.get("basis", "any"), " ‖ ".join(f"{k}: {', '.join(v[:4])}{' (+' + str(len(v) - 4) + ' more)' if len(v) > 4 else ''}" for k, v in c["values"].items())] for c in groups])] if groups else ["none"]
    shown, more = capped(claims_c, 40, "05-claims-verification.md")
    body += ["", f"### Claims contradicted by measurement {more}", "", md_table(["location", "type", "claimed", "observed", "evidence"], [[c["location"], c["claim_type"], f"{c['value']} {c.get('unit') or ''}".strip(), c.get("observed_value", "UNKNOWN"), c.get("evidence", "")] for c in shown]) if shown else "none", ""]
    orph = s["orphans"]["hf_without_living_source"]
    nolink = [o for o in orph if o["state"] == "NO_SOURCE_LINK"]
    arch = [o for o in orph if o["state"] == "SOURCE_ARCHIVED"]
    broken = [o for o in orph if o["state"] == "BROKEN_SOURCE_LINK"]
    body += ["## Orphans", f"- HF artifacts whose card declares no source link: {len(nolink)} ({sum(1 for o in nolink if o.get('private'))} private)", *[f"  - {o['artifact']}" for o in nolink], f"- HF artifacts whose linked source repo is archived: {len(arch)}", *[f"  - {o['artifact']} → {', '.join(o['source_links'])}" for o in arch], f"- HF artifacts linking a source repo that does not exist: {len(broken)}", *[f"  - {o['artifact']} → {', '.join(o['source_links'])}" for o in broken], "- Repos linking HF targets that do not exist:", *bullets(f"{o['repo']}: {', '.join(o['missing_targets'])}" for o in s["orphans"]["repos_claiming_missing_targets"]), ""]
    impl, impl_more = capped(s["duplicates"], 40, "state/zoomout.json")
    body += [f"## Possible duplicates: files matching verifier file-name patterns (lower bound; independence NOT_TESTED) {impl_more}", *bullets(impl), ""]
    doc, doc_more = capped(s["unenforced_doctrine"], 30, "05-claims-verification.md")
    body += [f"## Unenforced doctrine (stated in prose, no machine check found) {doc_more}", md_table(["type", "location", "text"], [[c["claim_type"], c["location"], c["text"][:120]] for c in doc]), ""]
    unv, unv_more = capped(s["unverified_claims"], 30, "05-claims-verification.md")
    body += [f"## Unverified categorical claims {unv_more}", md_table(["type", "location", "text"], [[c["claim_type"], c["location"], c["text"][:120]] for c in unv]), ""]
    body += ["## Single points of failure", *[f"- {x['type']}: {fmt(x['evidence'])}" for x in s["single_points_of_failure"]], "- Contributor figures are per GitHub account (type User); aliases are not merged and automation-named identities are not excluded.", ""]
    body += ["## Schema skew", "Genuine skew (distinct version numbers within an estate schema family) is listed in 04; separator-only variants are naming inconsistencies, not skew.", ""]
    ebv = [f"- {f['artifact']}: {f['title']} — {' '.join(f['evidence'].split())[:240]}" for f in s["evidence_boundary_violations"]] or ["- none detected by rule"]
    body += ["## Evidence-boundary violations (integrity allowed to imply validity)", *ebv]
    hdr = _hdr(status="FAIL" if z["bandaids"] else "PASS", what_was_expected="systemic gap analysis across both estates", what_was_examined=f"{len(z['findings'])} findings + reconciliation + claims", what_actually_ran="rule-based band-aid detection (each rule fires only on evidence)", what_passed="no rule-detected evidence-boundary violation" if not s["evidence_boundary_violations"] else "none", what_failed=f"{len(z['bandaids'])} band-aids identified; {len(groups)} contradiction groups; {len(claims_c)} contradicted claims", what_abstained="band-aids without machine-visible evidence are not reported", what_remains_unresolved="organisational causes (staffing, priorities) are out of scope", what_this_result_does_not_prove="that the listed structural fixes are sufficient on their own")
    w.text("09-gaps-and-bandaids.md", report("09 — Gaps and band-aids", hdr, "\n".join(body), rollup_coverage(g, h)))


# ------------------------------------------------------------------ 10 frontier
def r10(w: ReportWriter, z: dict[str, Any], rec: dict[str, Any], g: dict[str, Any], h: dict[str, Any]) -> None:
    byc: dict[str, list[str]] = {}
    for f in z["findings"]:
        byc.setdefault(f["category"], []).append(f["id"])

    def ids(*cats: str) -> str:
        out = [i for c in cats for i in byc.get(c, [])]
        return ", ".join(out[:12]) + (f" (+{len(out) - 12} more)" if len(out) > 12 else "") if out else "none"

    body = [
        "Each item is buildable with named components and has an acceptance test; evidence IDs refer to 11-remediation-table.",
        "",
        "## 1. One canonical receipt schema, one shared library, one conformance suite",
        f"- Evidence: {ids('conformance', 'vacuous-pass')}; {rec['receipt_schema_distinct']} receipt-like identifiers (04); {len(z.get('verifier_implementations', []))} files matching verifier file-name patterns (lower bound).",
        "- Build: publish `szl-receipt-core` (Python + TS) containing the JSON Schema, canonicalisation, hash-chain and DSSE checks; receipt-emitting/verifying repos depend on it.",
        "- Conformance: move `governed-receipts-bench` fixtures into the library repo as `conformance/` with expected outcomes **per library version**; a reusable workflow runs them in every consumer's CI and fails on drift.",
        "- Acceptance: the default branch of every verifier reproduces all declared outcomes; a PR that changes semantics updates expected outcomes and the changelog in the same PR.",
        "",
        "## 2. Verifier mutation testing in CI; blind spots published",
        "- Evidence: this repo's engine publishes blind spots P02/P03 (01); szl-eclipse's README states ten attack classes (UNVERIFIED by this audit).",
        "- Build: a required CI job per verifier runs a mutation harness (pattern: `szl_evidence.mutations`) and writes `BLIND_SPOTS.md`.",
        "- Acceptance: CI fails if a previously detected mutation becomes undetected; blind-spot list changes require review.",
        "",
        "## 3. One machine-readable estate inventory from live APIs",
        f"- Evidence: {ids('claim-accuracy', 'stale-claim')}.",
        "- Build: daily workflow running `szl-audit hf` + `szl-audit github` in list mode, committing `inventory.json` with `observed_at`; README/card numbers are templated from it.",
        "- Acceptance: `szl-audit reconcile` reports zero STALE/CONTRADICTED inventory claims.",
        "",
        "## 4. Automated card and README claim verification on every publish",
        f"- Evidence: {ids('unverified-claim', 'misleading-presentation', 'card-accuracy')}.",
        "- Build: pre-publish gate running `claims_extract` over the card; capability language without an evaluation section blocks upload; numbers carry a `claim_id` resolvable in a claim registry.",
        "- Acceptance: a card PR adding an unregistered number or unevidenced capability phrase fails the gate.",
        "",
        "## 5. Fail-closed publication gating",
        f"- Evidence: {ids('functional', 'version-drift', 'availability')}.",
        "- Build: the publish workflow evaluates the dependency DAG (`szl_evidence.dependencies`) and refuses to upload while any node is STALE_PENDING_REVALIDATION or any claim is UNVERIFIED; the refusal is itself a receipt.",
        "- Acceptance: bumping an upstream version blocks publication of every descendant until revalidated (as demonstrated in 01).",
        "",
        "## 6. Signing key custody, rotation, honest UNSIGNED path",
        f"- Evidence: {ids('vacuous-pass')}.",
        "- Build: keys in a KMS/HSM or Sigstore keyless (OIDC); rotation every 90 days with a published key history; verifiers print NOT_TESTED/UNSIGNED when no key is supplied (never PASS); relabel `hmac-stub` fixtures UNSIGNED.",
        "- Acceptance: running a verifier without a key yields ABSTAIN, and a conformance fixture asserts it.",
        "",
        "## 7. Public entry-point map",
        f"- Evidence: {ids('developer-experience', 'tests')}.",
        "- Build: one page routing *verify a receipt* → receipt-core + bench; *run governed inference* → szl-router + llm-router-live; *inspect formal proofs* → lutar-lean; each link carries a CI-measured time-to-first-run.",
        "- Acceptance: every linked artifact passes a clean-install job in CI; the page is regenerated by CI.",
        "",
        "## 8. Contributor intake with typed access classes",
        f"- Evidence: {ids('governance', 'license')}.",
        "- Build: `CONTRIBUTING.md` + org rulesets defining classes (public-docs, code, receipts/keys, release) with explicit permissions; CODEOWNERS per class.",
        "- Acceptance: every default branch is covered by an org ruleset; a contributor outside a class cannot merge into its paths.",
    ]
    hdr = _hdr(status="NOT_APPLICABLE (plan)", what_was_expected="specific, buildable forward plan", what_was_examined="findings, band-aids, reconciliation", what_actually_ran="none (planning document derived from evidence)", what_passed="NOT_APPLICABLE", what_failed="NOT_APPLICABLE", what_abstained="effort estimates beyond S/M/L", what_remains_unresolved="owner assignment and scheduling", what_this_result_does_not_prove="that executing the plan resolves every finding")
    w.text("10-frontier-plan.md", report("10 — Frontier plan", hdr, "\n".join(body), rollup_coverage(g, h)))


# ------------------------------------------------------------------ 11 remediation
def five_first_command(f: dict[str, Any]) -> str:
    a = f["artifact"]
    repo = a.split("/")[-1]
    cat = f["category"]
    if cat == "conformance":
        return "git clone https://github.com/szl-holdings/governed-receipt-spec && cd governed-receipt-spec\npython verify.py <bench>/valid/lake-inference-receipt.json   # reproduce: bind FAIL UNBOUND\n# in the HF dataset: move valid/lake-inference-receipt.json to invalid/, set expected_result FAIL in bench.jsonl,\n# and add a CI job in governed-receipt-spec that replays every bench fixture on each PR"
    if cat == "vacuous-pass":
        return "# governed-receipt-spec/verify.py: when --verify-key is absent print 'sig: NOT_TESTED' and exit 2 (ABSTAIN), not PASS\n# add bench fixture valid-no-key expecting ABSTAIN"
    if cat == "functional" and "Dataset" in f["title"]:
        return f"python -c \"import datasets; datasets.load_dataset('{a}', split='train[:5]')\"   # reproduce\n# README.md YAML: add configs: [{{config_name: default, data_files: <files with one schema>}}] and dataset_info.features;\n# put files with a different schema in their own config"
    if cat == "developer-experience" and "vsp-otel" in f["evidence"]:
        return f"cd {repo}\n# requirements.txt: replace 'vsp-otel>=0.1' with\n#   vsp-otel @ git+https://github.com/szl-holdings/vsp-otel@<tag>\n# or delete the line (the package is vendored in ./vsp_otel)\npython -m venv .v && .v/Scripts/pip install -r requirements.txt   # must succeed"
    if cat == "ci":
        return f"gh run list -R szl-holdings/{repo} --branch main --limit 20   # inspect the failing gate\n# fix the failing job, then make it a required check:\ngh api -X PUT repos/szl-holdings/{repo}/branches/main/protection --input protection.json"
    if cat == "tests":
        return f"cd {repo} && python -m venv .v && .v/Scripts/pip install -e .[test] && .v/Scripts/python -m pytest -q"
    return f"# {f['structural_fix']}"


def r11(w: ReportWriter, z: dict[str, Any], g: dict[str, Any], h: dict[str, Any]) -> list[dict[str, Any]]:
    table = z["remediation"]
    headers = ["ID", "Severity", "Surface", "Artifact", "Finding", "Evidence", "Root cause", "Structural fix", "Effort", "Blocks"]
    rows = [[f["id"], f["severity"], f["surface"], f["artifact"], f["title"], " ".join(f["evidence"].split())[:400], f["root_cause"] or "UNKNOWN (not assessed)", f["structural_fix"] or "UNKNOWN (not assessed)", f["effort"], f["blocks"] or "none"] for f in table]
    w.csv("11-remediation-table.csv", headers + ["Source", "Observed at", "Confidence"], [r + [f["source"], f["observed_at"], f["confidence"]] for r, f in zip(rows, table, strict=True)])
    five = []
    seen_cat: set[str] = set()
    for f in table:
        if f["category"] in seen_cat:
            continue
        seen_cat.add(f["category"])
        five.append(f)
        if len(five) == 5:
            break
    cnt = Counter(f["severity"] for f in table)
    body = ["## Fix these five first", "", "Selection rule: the highest-ranked finding (severity, then effort) from each of the first five distinct categories.", ""]
    for i, f in enumerate(five, 1):
        body += [f"{i}. **{f['id']} [{f['severity']}] {f['artifact']} — {f['title']}**", f"   - Evidence: {' '.join(f['evidence'].split())[:300]}", f"   - Root cause: {f['root_cause'] or 'UNKNOWN (not assessed)'}", f"   - Structural fix: {f['structural_fix']}", "   - Command / diff:", "", "```bash", five_first_command(f), "```", ""]
    body += ["## Full table (severity, then effort)", "", md_table(headers, rows), ""]
    res = z.get("resolved", [])
    body += ["## Resolved after the audit snapshot (re-checked live)", "", md_table(["artifact", "finding at audit time", "severity then", "resolution evidence"], [[r["artifact"], r["title"], r["severity_at_audit"], r["reason"]] for r in res]) if res else "none", ""]
    ref = z.get("refuted", [])
    body += ["## Removed after adversarial verification (refuted)", "", md_table(["artifact", "original finding", "why it was refuted"], [[r["artifact"], r["title"], r["reason"]] for r in ref]) if ref else "none"]
    info = sum(1 for f in z["findings"] if f["severity"] == "INFO")
    hdr = _hdr(status=sev_status(table), what_was_expected="one prioritised remediation table", what_was_examined=f"{len(z['findings'])} findings (after adversarial verification: refuted findings removed, confirmed ones re-graded)", what_actually_ran="sort by severity then effort", what_passed=f"none ({len(table)} actionable findings)" if table else "no actionable findings", what_failed="by severity: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 9))), what_abstained=f"INFO-level items excluded ({info})", what_remains_unresolved=f"{sum(1 for f in table if f['effort'] == 'UNKNOWN')} findings with UNKNOWN effort", what_this_result_does_not_prove="that severity reflects business impact; " + HOST_NOTE)
    w.text("11-remediation-table.md", report("11 — Prioritised remediation", hdr, "\n".join(body), rollup_coverage(g, h)))
    return five


# ------------------------------------------------------------------ 00 summary
def r00(w: ReportWriter, e: dict[str, Any] | None, g: dict[str, Any], h: dict[str, Any], z: dict[str, Any], cl: dict[str, Any], five: list[dict[str, Any]]) -> None:
    cnt = Counter(f["severity"] for f in z["findings"])
    gc, hc = gh_coverage(g), hf_coverage(h)
    fx_ok = sum(f["match"] for f in e["fixtures"]) if e else NOT_TESTED
    blind = e["mutations"]["summary"]["blind_spots"] if e else []
    v = Counter(c["verdict"] for c in cl["claims"])
    unresolved_tests = sum(1 for s in g["smoke"].values() if (s.get("tests") or {}).get("state") == "UNRESOLVED")
    body = [
        md_table(["item", "measured"], [
            ["Engine fixtures matching declared outcome", f"{fx_ok}/{len(e['fixtures']) if e else NOT_TESTED}"],
            ["Mutation blind spots (published)", ", ".join(blind) or "none"],
            ["GitHub repos discovered / cloned / smoke-tested", f"{len(g['gh']['repos'])} / {gc['artifacts_examined']} / {gc['artifacts_functionally_tested']}"],
            ["HF artifacts discovered / functionally tested", f"{len(h['hf']['artifacts'])} / {hc['artifacts_functionally_tested']}"],
            ["Claims VERIFIED / STALE / CONTRADICTED / UNVERIFIABLE", f"{v.get('VERIFIED', 0)} / {v.get('STALE', 0)} / {v.get('CONTRADICTED', 0)} / {v.get('UNVERIFIABLE', 0)}"],
            ["Findings by severity", ", ".join(f"{k} {n}" for k, n in sorted(cnt.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 9)))],
        ]),
        "",
        "## Critical and high findings",
        *bullets(f"[{f['severity']}] {f['artifact']}: {f['title']}" for f in sorted(z["findings"], key=lambda f: SEVERITY_ORDER.get(f["severity"], 9)) if f["severity"] in ("CRITICAL", "HIGH")),
        "",
        "## Fix first (highest-ranked finding per category)",
        *[f"{i}. {f['id']} {f['artifact']}: {f['title']}" for i, f in enumerate(five, 1)],
    ]
    hdr = _hdr(
        status=sev_status(z["findings"]),
        what_was_expected="engine verification + full GitHub and HF audits + reconciliation + zoom-out",
        what_was_examined=f"{len(g['gh']['repos'])} repos, {len(h['hf']['artifacts'])} HF artifacts, {len(cl['claims'])} claims",
        what_actually_ran="all stages (see receipts/); CRITICAL/HIGH findings adversarially verified by two independent reviewers each",
        what_passed=f"{fx_ok} engine fixtures; {gc['artifacts_functionally_tested']} repos smoke-tested; {v.get('VERIFIED', 0)} claims VERIFIED",
        what_failed=f"{cnt.get('CRITICAL', 0)} CRITICAL, {cnt.get('HIGH', 0)} HIGH, {cnt.get('MEDIUM', 0)} MEDIUM findings",
        what_abstained=f"{gc['artifacts_not_tested']} repos and {hc['artifacts_not_tested']} HF artifacts not functionally tested (reasons in 02/03)",
        what_remains_unresolved=f"engine blind spots {', '.join(blind) or 'none'}; {unresolved_tests} UNRESOLVED test outcomes (interim harness); {v.get('STALE', 0)} STALE claims",
        what_this_result_does_not_prove="product quality, security, scientific validity, or business value",
    )
    w.text("00-executive-summary.md", report("00 — Executive summary", hdr, "\n".join(body), rollup_coverage(g, h)))


# ------------------------------------------------------------------ public filtering + entry point
def _public(g: dict[str, Any], h: dict[str, Any], rec: dict[str, Any], cl: dict[str, Any], z: dict[str, Any]) -> tuple[dict, dict, dict, dict, dict]:
    import copy

    g, h, rec, cl, z = (copy.deepcopy(x) for x in (g, h, rec, cl, z))
    priv_repos = {r["name"] for r in g["gh"]["repos"] if r.get("private")}
    priv_arts = {a["id"] for a in h["hf"]["artifacts"] if a.get("private")}
    g["gh"]["repos"] = [r for r in g["gh"]["repos"] if r["name"] not in priv_repos]
    for k in ("files", "smoke", "scores", "links"):
        g[k] = {n: x for n, x in (g.get(k) or {}).items() if n not in priv_repos}
    h["hf"]["artifacts"] = [a for a in h["hf"]["artifacts"] if a["id"] not in priv_arts]
    rec["hf_to_source"] = [r for r in rec["hf_to_source"] if not r.get("private")]
    rec["source_to_hf"] = [r for r in rec["source_to_hf"] if not r.get("private")]
    rec["orphaned_hf"] = [r for r in rec["orphaned_hf"] if not r.get("private")]
    rec["receipt_schema_ids"] = {k: [r for r in v if r not in priv_repos] for k, v in rec["receipt_schema_ids"].items() if any(r not in priv_repos for r in v)}
    rec["inventory_drift"] = [c for c in rec.get("inventory_drift", []) if not c.get("source_private")]
    cl["claims"] = [c for c in cl["claims"] if not c.get("source_private")]
    z["findings"] = [f for f in z["findings"] if f["artifact"] not in priv_repos and f["artifact"] not in priv_arts]
    z["remediation"] = [f for f in z["remediation"] if f["artifact"] not in priv_repos and f["artifact"] not in priv_arts]
    return g, h, rec, cl, z


def render_all(out: Path, public: bool = False) -> list[str]:
    e = load(out, "engine")
    g, h, rec, cl, z = load(out, "github"), load(out, "hf"), load(out, "reconcile"), load(out, "claims"), load(out, "zoomout")
    private_names: list[str] = []
    if public and g and h:
        for r in g["gh"]["repos"]:
            if r.get("private"):
                private_names += [r["name"], f"szl-holdings/{r['name']}"]
        for a in h["hf"]["artifacts"]:
            if a.get("private"):
                private_names += [a["id"], a["id"].split("/", 1)[1]]
    w = ReportWriter(out / "public" if public else out, redact_names=private_names)
    r01(w, e)
    if None in (g, h, rec, cl, z):
        return sorted(w.hashes)
    if public:
        g, h, rec, cl, z = _public(g, h, rec, cl, z)
    r02(w, g)
    r03(w, h)
    r04(w, rec, h, g)
    r05(w, cl, g, h)
    r06(w, g)
    r07(w, g, h, z, cl)
    r08(w, g, h, z, rec)
    r09(w, z, g, h)
    r10(w, z, rec, g, h)
    five = r11(w, z, g, h)
    r00(w, e, g, h, z, cl, five)
    w.json("receipts/report-hashes.json", {"generated_at": utcnow(), "public_only": public, "sha256": w.hashes})
    return sorted(w.hashes)
