"""Conformance-corpus replay: the single most important functional test in the estate.

For a dataset that ships known-valid and deliberately tampered fixtures with declared
outcomes, run the paired verifier against every fixture - at the pinned commit the card
names and at the verifier's current default branch - and report every fixture whose
declared outcome does not match observed behaviour (CRITICAL).
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import httpx

from ..models import NOT_TESTED, utcnow
from ..safety import contained, isolated_env, run_argv
from .functional import _venv, run_paired_verifier

HF = "https://huggingface.co"
CARD_REPO = re.compile(r"github\.com/(szl-holdings/[A-Za-z0-9._-]+?)(?:\.git)?(?=[\s/)`'\"]|$)")
CARD_PIN = re.compile(r"git (?:checkout|switch --detach) ([0-9a-f]{7,40})")


def download_dataset(rid: str, files: list[dict[str, Any]], dest: Path, token: str | None, max_file: int = 5_000_000, max_total: int = 60_000_000) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    got, skipped, total = [], [], 0
    with httpx.Client(headers=headers, timeout=60, follow_redirects=True) as c:
        for f in files:
            size = f.get("size") if isinstance(f.get("size"), int) else 0
            if size > max_file or total + size > max_total:
                skipped.append(f["path"])
                continue
            target = contained(dest, f["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                r = c.get(f"{HF}/datasets/{rid}/resolve/main/{f['path']}")
            except httpx.HTTPError as e:
                skipped.append(f"{f['path']} (SOURCE_UNAVAILABLE {e.__class__.__name__})")
                continue
            if r.status_code != 200:
                skipped.append(f"{f['path']} (http {r.status_code})")
                continue
            target.write_bytes(r.content)
            total += len(r.content)
            got.append(f["path"])
    return {"downloaded": len(got), "skipped": skipped, "bytes": total}


def clone_at(full: str, dest: Path, ref: str | None) -> dict[str, Any]:
    gh = shutil.which("gh")
    git = shutil.which("git") or "git"
    argv = [gh, "repo", "clone", full, str(dest), "--", "--filter=blob:none", "-c", "core.longpaths=true"] if gh else [git, "clone", "--filter=blob:none", f"https://github.com/{full}.git", str(dest)]
    r = run_argv(argv, timeout=600)
    if r["exit_code"] != 0:
        return {"ok": False, "detail": r["output"][-400:]}
    if ref:
        co = run_argv([git, "-C", str(dest), "checkout", "--quiet", ref], timeout=120)
        if co["exit_code"] != 0:
            return {"ok": False, "detail": f"checkout {ref} failed: {co['output'][-300:]}"}
    head = run_argv([git, "-C", str(dest), "rev-parse", "HEAD"], timeout=30)["output"].strip()
    return {"ok": True, "head": head}


def replay_fixture_corpus(art: dict[str, Any], token: str | None) -> dict[str, Any]:
    rid = art["id"]
    card = art.get("readme_text", "")
    manifests = [f for f in art["files"] if f["path"].endswith(".jsonl") and "bench" in f["path"]]
    work = Path(tempfile.mkdtemp(prefix="szl-bench-"))
    try:
        ds = work / "ds"
        dl = download_dataset(rid, art["files"], ds, token)
        rows: list[dict[str, Any]] = []
        for m in manifests:
            for line in (ds / m["path"]).read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        rows = [r for r in rows if "file" in r and "expected_result" in r]
        repos = sorted(set(CARD_REPO.findall(card)))
        pin = (CARD_PIN.findall(card) or [None])[0]
        verifier_repo = next((r for r in repos if "spec" in r or "verif" in r), repos[0] if repos else None)
        out: dict[str, Any] = {"dataset": rid, "type": "fixture_corpus", "declared_fixtures": len(rows), "download": dl, "verifier_repo": verifier_repo or "NO_SOURCE_LINK", "card_pinned_commit": pin or "NONE", "runs": []}
        if not verifier_repo or not rows:
            out["state"] = NOT_TESTED
            out["reason"] = "no paired verifier link or no fixture manifest rows"
            return out
        for label, ref in (("pinned", pin), ("default-branch HEAD", None)):
            if label == "pinned" and not pin:
                continue
            vdir = work / f"v-{label.split()[0]}"
            cl = clone_at(verifier_repo, vdir, ref)
            if not cl["ok"]:
                out["runs"].append({"verifier": f"{verifier_repo}@{label}", "state": "SOURCE_UNAVAILABLE", "detail": cl["detail"]})
                continue
            if not (vdir / "verify.py").exists():
                out["runs"].append({"verifier": f"{verifier_repo}@{cl['head'][:12]}", "state": NOT_TESTED, "reason": "verify.py not present at this revision"})
                continue
            res = run_paired_verifier(ds, rows, vdir, f"{verifier_repo}@{cl['head'][:12]} ({label})")
            res["revision"] = cl["head"]
            out["runs"].append(res)
        out["state"] = "RAN"
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def run_card_scorer(art: dict[str, Any], token: str | None) -> dict[str, Any]:
    """Datasets that ship their own scorer: run the exact command the card documents."""
    rid = art["id"]
    cmds = [c.split("#")[0].strip() for c in re.findall(r"(?m)^\s*(python [^\n]*score\.py[^\n]*)", art.get("readme_text", ""))]
    if not cmds:
        return {"dataset": rid, "type": "bundled_scorer", "state": NOT_TESTED, "reason": "card documents no scorer command"}
    work = Path(tempfile.mkdtemp(prefix="szl-score-"))
    try:
        ds = work / "ds"
        dl = download_dataset(rid, art["files"], ds, token)
        home = work / "home"
        home.mkdir()
        r, py = _venv(work / "env", home)
        runs = []
        for c in cmds[:3]:
            argv = c.split()
            argv[0] = str(py)
            if any(".." in a or Path(a).is_absolute() for a in argv[1:]):
                runs.append({"command": c, "state": NOT_TESTED, "reason": "argument escapes dataset directory"})
                continue
            vr = run_argv(argv, cwd=ds, env=isolated_env(home), timeout=300, max_output=3000)
            runs.append({"command": c, "exit_code": vr["exit_code"], "duration_s": vr["duration_s"], "output_tail": vr["output"][-900:]})
        return {"dataset": rid, "type": "bundled_scorer", "download": dl, "state": "RAN", "runs": runs, "all_exit_zero": all(x.get("exit_code") == 0 for x in runs)}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def run_all(hf: dict[str, Any], token: str | None) -> dict[str, Any]:
    started = utcnow()
    results = []
    for a in hf.get("artifacts", []):
        if a.get("kind") != "dataset" or "files" not in a:
            continue
        names = [f["path"] for f in a["files"]]
        if any(n.endswith("bench.jsonl") for n in names):
            results.append(replay_fixture_corpus(a, token))
        elif any(n.endswith("score.py") for n in names):
            results.append(run_card_scorer(a, token))
    return {"started_at": started, "completed_at": utcnow(), "corpora": results}
