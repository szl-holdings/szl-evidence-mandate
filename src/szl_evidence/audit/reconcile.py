"""Cross-surface reconciliation (3.4): GitHub <-> Hugging Face."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ..models import UNKNOWN
from ..safety import safe_walk

HF_LINK = re.compile(r"https?://huggingface\.co/(?:(spaces|datasets)/)?(SZLHOLDINGS)/([A-Za-z0-9._-]+)", re.I)
GH_LINK = re.compile(r"https?://github\.com/szl-holdings/([A-Za-z0-9._-]+?)(?:\.git)?(?=[/\s)`'\"#?]|$)", re.I)
PINNED_SRC = re.compile(r"szl-holdings/([A-Za-z0-9._-]+)@([0-9a-f]{7,40})", re.I)
SCHEMA_ID = re.compile(r"[\"'](?:schema|schema_version|\$id|predicateType|payloadType)[\"']\s*:\s*[\"']([^\"']{6,120})[\"']")
SCHEMA_TOKEN = re.compile(r"^[\w.:/+;=#@-]+$")
RECEIPTY = re.compile(r"(?i)receipt|attest|khipu|dsse|intoto|in-toto|envelope|evidence")


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _ts(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def scan_receipt_schemas(root: Path) -> list[str]:
    found: set[str] = set()
    for p in safe_walk(root, max_files=200_000):
        rel = p.relative_to(root).as_posix()
        if any(x in rel.split("/") for x in (".git", "node_modules", ".venv")) or p.suffix.lower() not in {".py", ".json", ".ts", ".js", ".md", ".yaml", ".yml"}:
            continue
        try:
            if p.stat().st_size > 1_000_000:
                continue
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for sid in SCHEMA_ID.findall(txt):
            if RECEIPTY.search(sid) and SCHEMA_TOKEN.match(sid) and not sid.startswith(("http://json-schema.org", "https://json-schema.org")):
                found.add(sid)
    return sorted(found)


def reconcile(gh: dict[str, Any], hf: dict[str, Any], files: dict[str, Any], clone_root: Path) -> dict[str, Any]:
    repos = {r["name"].lower(): r for r in gh["repos"]}
    arts = [a for a in hf["artifacts"] if "files" in a]
    art_ids = {a["id"].lower(): a for a in arts}
    rows_hf: list[dict[str, Any]] = []
    for a in arts:
        text = a.get("readme_text", "")
        links = sorted({m.lower() for m in GH_LINK.findall(text)} - {".github"})  # the org profile is not a source repo
        short = a["id"].split("/", 1)[1]
        best = next((lk for lk in links if norm(lk) == norm(short)), None) or next((lk for lk in links if norm(short) in norm(lk) or norm(lk) in norm(short)), None) or (links[0] if links else None)
        state = "LINKED"
        src = repos.get(best) if best else None
        if not best:
            state = "NO_SOURCE_LINK"
        elif not src:
            state = "BROKEN_SOURCE_LINK"
        elif src.get("archived"):
            state = "SOURCE_ARCHIVED"
        pins = [(r.lower(), s) for r, s in PINNED_SRC.findall(text)]
        drift = []
        for r, sha in pins:
            s = repos.get(r)
            head = ((s or {}).get("detail", {}).get("head") or {}) if s else {}
            hsha = head.get("sha") if isinstance(head, dict) else None
            if hsha:
                drift.append({"repo": r, "pinned": sha, "source_head": hsha[:12], "drifted": not hsha.startswith(sha)})
        lag = UNKNOWN
        if src and _ts(src.get("pushed_at")) and _ts(a.get("last_modified")):
            lag = (_ts(src["pushed_at"]) - _ts(a["last_modified"])).days
        rows_hf.append({"artifact": a["id"], "kind": a["kind"], "private": a.get("private"), "source_links": links[:8], "canonical_source": best or "NO_SOURCE_LINK", "state": state, "pinned_source_refs": drift, "source_newer_by_days": lag})
    # repo -> HF target
    rows_gh: list[dict[str, Any]] = []
    for name, r in sorted(repos.items()):
        f = files.get(r["name"]) or {}
        text = f.get("readme_text", "")
        targets = sorted({f"{(k or 'models')}/{o}/{n}".lower() for k, o, n in HF_LINK.findall(text)})
        missing = []
        for t in targets:
            kind, _, n = t.split("/", 2)
            if f"szlholdings/{n}".lower() not in art_ids:
                missing.append(t)
        publishes = any(re.search(r"(?i)hugging|hf[-_ ]|push_to_hub|upload_folder", w.get("name", "") + w.get("path", "")) for w in (r["detail"].get("workflows") or []) if isinstance(w, dict))
        back = [a["artifact"] for a in rows_hf if a["canonical_source"] == name]
        state = ("HAS_TARGET_WITH_MISSING" if missing else "HAS_TARGET") if (targets and not missing) or back else ("CLAIMED_TARGET_MISSING" if missing else ("NO_PUBLISHED_TARGET" if publishes else "NOT_A_PUBLISHER"))
        rows_gh.append({"repo": r["name"], "archived": r.get("archived"), "private": r.get("private"), "readme_hf_targets": targets[:10], "missing_targets": missing, "hf_artifacts_linking_back": back, "has_publish_workflow": publishes, "state": state})
    # naming
    naming = []
    gh_norm = defaultdict(list)
    for r in gh["repos"]:
        gh_norm[norm(r["name"])].append(r["name"])
    for a in arts:
        short = a["id"].split("/", 1)[1]
        for g in gh_norm.get(norm(short), []):
            if g != short:
                naming.append({"hf": a["id"], "github": f"szl-holdings/{g}", "issue": "same identifier, different casing/punctuation"})
    # receipt/schema skew
    schema_uses: dict[str, set[str]] = defaultdict(set)
    schema_not_tested = []
    for name, f in files.items():
        ids = f.get("receipt_schema_ids")
        if ids is None:
            ids = scan_receipt_schemas(clone_root / name) if (clone_root / name).is_dir() else None
        if ids is None:
            schema_not_tested.append(name)
            continue
        for sid in ids:
            schema_uses[sid].add(name)
    families: dict[str, list[str]] = defaultdict(list)
    for sid in schema_uses:
        fam = re.sub(r"(/v?\d+(\.\d+)*|[.-]v\d+(\.\d+)*)$", "", sid)
        families[fam].append(sid)
    skew = [{"family": fam, "versions": sorted(v), "repos": sorted({r for s in v for r in schema_uses[s]})[:15]} for fam, v in sorted(families.items()) if len(v) > 1]
    receipt_schemas = {sid: sorted(rs) for sid, rs in sorted(schema_uses.items())}
    return {
        "hf_to_source": rows_hf,
        "source_to_hf": rows_gh,
        "orphaned_hf": [r for r in rows_hf if r["state"] in ("NO_SOURCE_LINK", "BROKEN_SOURCE_LINK", "SOURCE_ARCHIVED")],
        "orphaned_repo_claims": [r for r in rows_gh if r["missing_targets"]],
        "version_drift": [dict(artifact=r["artifact"], **d) for r in rows_hf for d in r["pinned_source_refs"] if d["drifted"]],
        "naming_inconsistencies": naming,
        "receipt_schema_ids": receipt_schemas,
        "receipt_schema_distinct": len(receipt_schemas),
        "receipt_schema_scan_not_tested": schema_not_tested,
        "schema_version_skew": skew,
    }
