"""Audit pipeline stages. Each stage persists its state under ``<out>/state/`` so later
stages (reconcile, zoomout) can run as separate commands, and emits a run receipt."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..adapters.http import CachedClient
from ..models import NOT_TESTED, UNAVAILABLE, sha256_json, utcnow
from ..receipts import simple_receipt, write_receipt
from . import claims_extract, conformance, findings, functional, github, huggingface, reconcile, zoomout
from .common import FindingSink, hf_token

LINK_DOMAINS = re.compile(r"https?://(?:www\.)?(huggingface\.co|github\.com/szl-holdings|a-11-oy\.com|a11oy\.net|doi\.org|zenodo\.org)[^\s)\]>\"'`]*", re.I)


def _state(out: Path, name: str) -> Path:
    p = out / "state" / f"{name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save(out: Path, name: str, obj: Any) -> None:
    _state(out, name).write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False), encoding="utf-8")


def load(out: Path, name: str) -> Any:
    p = _state(out, name)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def receipt(out: Path, kind: str, payload: dict[str, Any], started: str, status: str, limitations: list[str]) -> dict[str, Any]:
    """Seal a stage receipt and chain it to the previous stage's receipt (receipts/HEAD)."""
    from ..receipts import chain, seal

    head = out / "receipts" / "HEAD"
    parent = None
    if head.exists():
        try:
            parent = json.loads((out / "receipts" / head.read_text(encoding="utf-8").strip()).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            parent = None
    r = simple_receipt(kind, payload, started, utcnow(), status, limitations)
    chain(r, parent)
    r = seal(r)
    name = f"{kind}-{r['run_id']}.json"
    write_receipt(r, out / "receipts" / name)
    head.write_text(name, encoding="utf-8")
    return r


def verify_receipt_chain(receipts_dir: Path) -> dict[str, Any]:
    """Walk receipts/HEAD back through parent_sha256 links; every link must resolve and every
    receipt's content hash must match."""
    from ..receipts import receipt_hash

    by_hash = {}
    for f in receipts_dir.glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(r, dict) and "receipt_sha256" in r:
            by_hash[r["receipt_sha256"]] = (f.name, r)
    head = receipts_dir / "HEAD"
    if not head.exists():
        return {"state": "ABSTAIN", "reason": "no HEAD"}
    cur = json.loads((receipts_dir / head.read_text(encoding="utf-8").strip()).read_text(encoding="utf-8"))
    walked, problems = [], []
    while cur:
        if receipt_hash(cur) != cur["receipt_sha256"]:
            problems.append(f"content hash mismatch in {cur.get('kind')} {cur.get('run_id')}")
        walked.append(f"{cur.get('kind')}:{cur['receipt_sha256'][:12]}")
        p = cur.get("parent_sha256")
        if not p:
            break
        if p not in by_hash:
            problems.append(f"parent {p[:12]} not found")
            break
        cur = by_hash[p][1]
    return {"state": "PASS" if not problems else "FAIL", "chain": walked, "problems": problems}


# ------------------------------------------------------------------ link resolution
def resolve_links(gh: dict[str, Any], files: dict[str, Any], hf_ids: set[str], cache: Path) -> dict[str, Any]:
    repo_names = {r["name"].lower(): r for r in gh["repos"]}
    per_repo: dict[str, list[str]] = {}
    ext: set[str] = set()
    for name, f in files.items():
        urls = sorted({u.rstrip(".,);") for u in (m.group(0) for m in LINK_DOMAINS.finditer(f.get("readme_text", "")))})
        per_repo[name] = urls[:40]
        ext.update(u for u in urls if not re.match(r"https?://(huggingface\.co|github\.com)", u, re.I))
    client = CachedClient(cache, surface="links", min_interval=0.1, timeout=20, max_retries=1)
    ext_status: dict[str, Any] = {}

    def chk(u: str) -> tuple[str, Any]:
        r = client.get(u, max_bytes=4096)
        return u, r.status

    with ThreadPoolExecutor(6) as ex:
        for u, st in ex.map(chk, sorted(ext)[:400]):
            ext_status[u] = st
    client.close()
    out: dict[str, Any] = {}
    for name, urls in per_repo.items():
        broken, checked = [], 0
        for u in urls:
            m = re.match(r"https?://huggingface\.co/(?:(spaces|datasets)/)?([^/\s]+)/([^/\s#?]+)", u, re.I)
            g = re.match(r"https?://github\.com/szl-holdings/([^/\s#?]+)", u, re.I)
            if m and m.group(2).lower() == "szlholdings":
                checked += 1
                if f"szlholdings/{m.group(3)}".lower() not in hf_ids:
                    broken.append(u)
            elif g:
                checked += 1
                rn = g.group(1).removesuffix(".git").lower()
                if rn not in repo_names:
                    broken.append(u)
            elif u in ext_status:
                checked += 1
                st = ext_status[u]
                if isinstance(st, int) and st in (404, 410):
                    broken.append(u)
        out[name] = {"checked": checked, "broken": broken, "method": "HF/GitHub links resolved against live inventories; others by GET (404/410 = broken; unavailable != broken)"}
    return out


# ------------------------------------------------------------------ stage: github
def stream_repos(gh: dict[str, Any], root: Path, deep: bool, smoke_cache: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Clone -> analyse -> smoke -> delete, one repository at a time. Peak disk = one repo.
    `.github` is kept (the org counter script and profile are needed by later stages)."""
    from ..safety import rmtree_force

    files: dict[str, Any] = {}
    smoke: dict[str, Any] = {}
    root.mkdir(parents=True, exist_ok=True)
    for r in gh["repos"]:
        if r.get("archived"):
            r["clone"] = {"ok": False, "reason": "archived"}
            continue
        dest = root / r["name"]
        import shutil as _sh

        free = _sh.disk_usage(root).free
        need = int((r.get("size_kb") or 0) * 1024 * 1.2) + 600 * 2**20
        if free < need:
            r["clone"] = {"ok": False, "exit_code": "NOT_TESTED", "reason": f"insufficient free disk on audit host to clone ({free // 2**20} MB free < {need // 2**20} MB needed)"}
            continue
        res = github.clone_repo(r["full_name"], dest)
        r["clone"] = {k: v for k, v in res.items() if k != "output"} | {"output": str(res.get("output", ""))[-400:], "mode": "streamed (deleted after analysis)" if r["name"] != ".github" else "streamed (kept)"}
        if not res.get("ok"):
            rmtree_force(dest)
            continue
        try:
            files[r["name"]] = github.analyze_clone(dest)
        except Exception as e:  # noqa: BLE001
            files[r["name"]] = {"error": f"{e.__class__.__name__}: {e}"}
        f = files[r["name"]]
        if "error" not in f and set(f.get("manifests", {})) & {"pyproject.toml", "setup.py", "requirements.txt", "package.json"} and (deep or r["name"] in findings.FLAGSHIPS):
            key = f"{r['name']}@{res.get('head')}"
            smoke[r["name"]] = dict(smoke_cache[key], reused_from_identical_head=smoke_cache[key].get("completed_at")) if key in smoke_cache else functional.smoke_repo(dest, f.get("readme_text", ""))
        if r["name"] != ".github":
            rmtree_force(dest)
    return files, smoke


def run_github(org: str, out: Path, clone: bool, deep: bool, dry_run: bool, admit_smoke: Path | None = None, stream: bool = False) -> dict[str, Any]:
    started = utcnow()
    raw = out / "raw"
    gh = github.collect(org, raw, clone=clone and not dry_run and not stream, dry_run=dry_run)
    if dry_run:
        return {"dry_run": True, "repos_listed": len(gh["repos"]), "listing": gh["listing"]}
    if gh["listing"]["denominator_state"] != "OBSERVED":
        # Never replace previously observed evidence with an unavailable observation.
        receipt(out, "github-audit", {"org": org, "inputs_sha256": sha256_json([]), "listing": gh["listing"]}, started, "ABSTAIN", ["Listing unavailable (e.g. rate limit); prior state left untouched."])
        return {"gh": gh, "smoke": {}, "state": "ABSTAIN", "reason": gh["listing"]["detail"]}
    root = Path(gh.get("clone_root") or github.tmp_clone_root())
    files: dict[str, Any] = {}
    streamed_smoke: dict[str, Any] = {}
    if stream:
        files, streamed_smoke = stream_repos(gh, root, deep, load(out, "smoke-cache") or {})
    elif clone:
        names = [r["name"] for r in gh["repos"] if r["clone"].get("ok")]

        def an(n: str) -> tuple[str, Any]:
            try:
                return n, github.analyze_clone(root / n)
            except Exception as e:  # noqa: BLE001
                return n, {"error": f"{e.__class__.__name__}: {e}"}

        with ThreadPoolExecutor(6) as ex:
            files = dict(ex.map(an, names))
    # installability smoke tests
    smoke_cache = load(out, "smoke-cache") or {}
    smoke: dict[str, Any] = {}
    tier = findings.FLAGSHIPS
    candidates = [n for n, f in files.items() if "error" not in f and set(f.get("manifests", {})) & {"pyproject.toml", "setup.py", "requirements.txt", "package.json"}]
    targets = candidates if deep else [n for n in candidates if n in tier]
    heads = {r["name"]: r["clone"].get("head") for r in gh["repos"]}

    def sm(n: str) -> tuple[str, Any]:
        key = f"{n}@{heads.get(n)}"
        if n in streamed_smoke:
            return n, streamed_smoke[n]
        if key in smoke_cache:
            res = dict(smoke_cache[key])
            res["reused_from_identical_head"] = res.get("completed_at")
            return n, res
        return n, functional.smoke_repo(root / n, files[n].get("readme_text", ""))

    # Sequential: the audit host's free disk is the binding constraint (see functional.MIN_FREE_BYTES).
    with ThreadPoolExecutor(1) as ex:
        for n, res in ex.map(sm, targets):
            smoke[n] = res
            if res.get("install_ok") != NOT_TESTED:  # never cache an audit-host (disk/timeout) outcome
                smoke_cache[f"{n}@{heads.get(n)}"] = res
    save(out, "smoke-cache", smoke_cache)
    admission: dict[str, Any] = {}
    if admit_smoke:
        from .admission import admit

        prior = json.loads(Path(admit_smoke).read_text(encoding="utf-8"))
        admission = admit(prior["results"], prior["heads"], heads, prior["label"], raw)
        for n, res in admission["admitted"].items():
            if n in candidates and smoke.get(n, {}).get("install_ok") in (None, NOT_TESTED):
                smoke[n] = res
        for n, why in admission["excluded"].items():
            if n in smoke and smoke[n].get("install_ok") == NOT_TESTED:
                smoke[n]["prior_evidence_excluded"] = why
    for n in candidates:
        if n not in smoke:
            smoke[n] = {"install_ok": NOT_TESTED, "reason": "outside priority tier (run with --deep to test all)"}
    from .attribution import classify_all

    smoke = classify_all(smoke)
    # Lean corpus recomputation
    lean = lean_facts(root, gh)
    hf_ids = {a["id"].lower() for a in (load(out, "hf") or {}).get("artifacts", [])}
    if not hf_ids:
        hf_ids = anon_hf_ids()
    links = resolve_links(gh, files, hf_ids, raw) if files else {}
    now = datetime.now(timezone.utc)
    scores = {r["name"]: github.scorecard(r, r["detail"], files.get(r["name"]), smoke.get(r["name"]) if isinstance(smoke.get(r["name"]), dict) and smoke[r["name"]].get("install_ok") is not NOT_TESTED else None, links.get(r["name"]), now) for r in gh["repos"]}
    state = {"admission": {"admitted": sorted(admission.get("admitted", {})), "excluded": admission.get("excluded", {})}, "gh": gh, "files": {k: {kk: vv for kk, vv in v.items() if kk != "readme_text"} | {"readme_text": v.get("readme_text", "")[:200_000]} for k, v in files.items()}, "smoke": smoke, "scores": scores, "lean": lean, "links": links}
    save(out, "github", state)
    status = "PASS" if gh["listing"]["denominator_state"] == "OBSERVED" else "ABSTAIN"
    receipt(out, "github-audit", {"org": org, "repos": len(gh["repos"]), "inputs_sha256": sha256_json([r["name"] for r in gh["repos"]]), "state_sha256": sha256_json(scores)}, started, status, ["Scores are heuristic evidence summaries, not certifications."])
    return state


def enrich_protection_messages(gh: dict[str, Any], raw: Path) -> int:
    """Recover GitHub's error message for 404 branch-protection responses from the raw cache
    (e.g. 'Branch not protected'), so a 404 is not reported as an opaque UNAVAILABLE."""
    from ..safety import redact

    n = 0
    for r in gh["repos"]:
        bp = r["detail"].get("branch_protection")
        if not (isinstance(bp, dict) and bp.get("http") == 404 and not bp.get("message")):
            continue
        url = f"https://api.github.com/repos/{r['full_name']}/branches/{r.get('default_branch')}/protection"
        f = raw / "github" / f"{sha256_json(['GET', redact(url), None])[:32]}.json"
        if f.exists():
            try:
                body = json.loads(json.loads(f.read_text(encoding="utf-8")).get("body") or "{}")
                bp["message"] = str(body.get("message", ""))[:120]
                n += 1
            except ValueError:
                pass
    return n


def rescore(out: Path) -> dict[str, Any]:
    """Offline: re-attribute recorded smoke outcomes and recompute scorecards from persisted
    evidence (no network collection, no cloning, no code execution)."""
    from .attribution import classify_all

    started = utcnow()
    st = load(out, "github")
    if not st or not st.get("gh", {}).get("repos"):
        return {"state": "ABSTAIN", "reason": "no persisted GitHub evidence to rescore"}
    st["smoke"] = classify_all(st["smoke"])
    enrich_protection_messages(st["gh"], out / "raw")
    now = datetime.now(timezone.utc)
    sm = st["smoke"]
    st["scores"] = {r["name"]: github.scorecard(r, r["detail"], st["files"].get(r["name"]), sm.get(r["name"]) if isinstance(sm.get(r["name"]), dict) and sm[r["name"]].get("install_ok") is not NOT_TESTED else None, (st.get("links") or {}).get(r["name"]), now) for r in st["gh"]["repos"]}
    st["rescored_at"] = started
    save(out, "github", st)
    receipt(out, "github-rescore", {"inputs_sha256": sha256_json(sorted(st["scores"])), "state_sha256": sha256_json(st["scores"])}, started, "PASS", ["Offline re-attribution of recorded outputs; nothing re-executed."])
    from collections import Counter

    return {"state": "PASS", "tests_by_state": dict(Counter(str((v.get("tests") or {}).get("state")) for v in sm.values() if isinstance(v, dict)))}


def anon_hf_ids(org: str = "SZLHOLDINGS") -> set[str]:
    c = CachedClient(None, surface="hf-anon")
    ids = set()
    for kind in ("models", "datasets", "spaces"):
        r = c.get(f"https://huggingface.co/api/{kind}", params={"author": org, "limit": 1000})
        if r.ok:
            ids |= {x["id"].lower() for x in r.json()}
    c.close()
    return ids


def lean_facts(root: Path, gh: dict[str, Any]) -> dict[str, Any]:
    """Recompute Lean counts at HEAD and at the revision the org's own lean_numbers.json pins."""
    import shutil
    import tempfile

    from ..safety import run_argv

    repo = root / "lutar-lean"
    pinned_file = root / ".github" / ".github" / "data" / "lean_numbers.json"
    pinned_meta = json.loads(pinned_file.read_text(encoding="utf-8")) if pinned_file.exists() else {}
    org_script = root / ".github" / ".github" / "scripts" / "lean_numbers.py"
    _ = repo
    tmp = Path(tempfile.mkdtemp(prefix="szl-lean-"))
    git = shutil.which("git") or "git"
    gh_cli = shutil.which("gh")
    full = tmp / "lutar-lean"
    argv = [gh_cli, "repo", "clone", "szl-holdings/lutar-lean", str(full), "--", "--filter=blob:none", "-c", "core.longpaths=true"] if gh_cli else [git, "clone", "--filter=blob:none", "https://github.com/szl-holdings/lutar-lean.git", str(full)]
    cl = run_argv(argv, timeout=900)
    res: dict[str, Any] = {"published": pinned_meta.get("numbers"), "published_sha": pinned_meta.get("sha"), "published_at": pinned_meta.get("measured_at_utc")}
    try:
        if cl["exit_code"] != 0:
            res["state"] = "SOURCE_UNAVAILABLE"
            return res
        head_sha = run_argv([git, "-C", str(full), "rev-parse", "HEAD"])["output"].strip()
        res["head_sha"] = head_sha
        res["independent_head"] = functional.lean_counts(full)
        if org_script.exists():
            from ..safety import isolated_env

            (tmp / "home").mkdir(exist_ok=True)
            o = run_argv([str(Path(__import__("sys").executable)), str(org_script), "--repo-path", str(full), "--out", str(tmp / "head.json")], env=isolated_env(tmp / "home"), timeout=300)
            if (tmp / "head.json").exists():
                res["head"] = json.loads((tmp / "head.json").read_text())["numbers"]
            res["org_script_exit_head"] = o["exit_code"]
        if pinned_meta.get("sha"):
            wt = tmp / "pinned"
            run_argv([git, "-C", str(full), "worktree", "add", "-f", "--detach", str(wt), pinned_meta["sha"]], timeout=300)
            res["pinned_sha"] = run_argv([git, "-C", str(wt), "rev-parse", "HEAD"])["output"].strip()
            res["pinned_date"] = run_argv([git, "-C", str(wt), "log", "-1", "--format=%cI"])["output"].strip()
            res["independent_pinned"] = functional.lean_counts(wt)
            if org_script.exists():
                run_argv([str(Path(__import__("sys").executable)), str(org_script), "--repo-path", str(wt), "--out", str(tmp / "pinned.json")], env=isolated_env(tmp / "home"), timeout=300)
                if (tmp / "pinned.json").exists():
                    res["pinned"] = json.loads((tmp / "pinned.json").read_text())["numbers"]
        res["state"] = "OBSERVED"
        res["method_note"] = "Primary counts use the org's own counter (.github/scripts/lean_numbers.py); independent_* use this tool's parser, which also counts @[attr]/protected/indented declarations."
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ stage: huggingface
def run_hf(org: str, out: Path, functional_tests: bool, dry_run: bool) -> dict[str, Any]:
    started = utcnow()
    hf = huggingface.collect(org, out / "raw", functional=functional_tests, dry_run=dry_run)
    if dry_run:
        return {"dry_run": True, "listing": hf["listing"]}
    conf = conformance.run_all(hf, hf_token()[0]) if functional_tests else {"corpora": [], "state": NOT_TESTED}
    anon = anon_public_counts(org, out / "raw")
    state = {"hf": hf, "conformance": conf, "public_counts": anon}
    save(out, "hf", state)
    receipt(out, "hf-audit", {"org": org, "artifacts": len(hf["artifacts"]), "inputs_sha256": sha256_json(sorted(a["id"] for a in hf["artifacts"])), "state_sha256": sha256_json([a.get("sha") for a in hf["artifacts"]])}, started, "PASS" if all(v["denominator_state"] == "OBSERVED" for v in hf["listing"].values()) else "ABSTAIN", ["Functional tests are minimal read-only probes; they do not establish model quality."])
    return state


def anon_public_counts(org: str, cache: Path) -> dict[str, Any]:
    """Replicates the profile's `hf-public-author-membership/v1` predicate: anonymous listing."""
    from ..adapters.http import paginate

    c = CachedClient(cache, surface="hf-anon", min_interval=0.1)
    counts: dict[str, Any] = {}
    for kind in ("models", "datasets", "spaces"):
        items, meta = paginate(c, f"https://huggingface.co/api/{kind}", {"author": org, "limit": 100})
        counts[kind] = len(items) if meta["denominator_state"] == "OBSERVED" else UNAVAILABLE
    c.close()
    return {"counts": counts, "observed_at": utcnow(), "method": "anonymous paginated /api/{models,datasets,spaces}?author=SZLHOLDINGS"}


# ------------------------------------------------------------------ claims (github + hf text)
def run_claims(gh_state: dict[str, Any], hf_state: dict[str, Any], out: Path) -> dict[str, Any]:
    gh = gh_state["gh"]
    claims: list[claims_extract.Claim] = []
    root = Path(gh.get("clone_root") or github.tmp_clone_root())
    prof = root / ".github" / "profile" / "README.md"
    if prof.exists():
        claims += claims_extract.extract(prof.read_text(encoding="utf-8", errors="replace"), "github:szl-holdings/.github/profile/README.md", "https://github.com/szl-holdings")
    for name, f in gh_state["files"].items():
        if f.get("readme_text"):
            priv = bool(next((r.get("private") for r in gh["repos"] if r["name"] == name), False))
            claims += claims_extract.extract(f["readme_text"], f"github:szl-holdings/{name}/{f['presence'].get('README') or 'README.md'}", f"https://github.com/szl-holdings/{name}", private=priv)
    for a in hf_state["hf"]["artifacts"]:
        if a.get("readme_text"):
            prefix = {"model": "", "dataset": "datasets/", "space": "spaces/"}[a["kind"]]
            claims += claims_extract.extract(a["readme_text"], f"hf:{a['kind']}:{a['id']}/README.md", f"https://huggingface.co/{prefix}{a['id']}", private=bool(a.get("private")))
    pc = (hf_state.get("public_counts") or {}).get("counts", {})
    public_repos = sum(1 for r in gh["repos"] if not r.get("private"))
    lean = gh_state.get("lean") or {}
    dois = sorted({c.value.rstrip(".").lower() for c in claims if c.claim_type == "doi"})
    doi_status = check_dois(dois, out / "raw")
    facts = {
        "public_counts": {"spaces": pc.get("spaces"), "models": pc.get("models"), "datasets": pc.get("datasets"), "repos": public_repos},
        "public_counts_at": (hf_state.get("public_counts") or {}).get("observed_at"),
        "auth_counts": {"spaces": hf_state["hf"]["listing"].get("space", {}).get("count"), "models": hf_state["hf"]["listing"].get("model", {}).get("count"), "datasets": hf_state["hf"]["listing"].get("dataset", {}).get("count"), "repos": len(gh["repos"])},
        "public_counts_method": "anonymous HF listing; GitHub public repo count from org listing",
        "repos_counted_at": gh.get("completed_at"),
        "lean": {"head": lean.get("head"), "pinned": lean.get("pinned"), "head_sha": lean.get("head_sha"), "pinned_sha": lean.get("pinned_sha"), "pinned_date": lean.get("pinned_date")},
        "doi_status": doi_status,
    }
    claims = claims_extract.verify_claims(claims, facts, utcnow())
    data = {"claims": [c.to_dict() for c in claims], "consistency": claims_extract.consistency(claims), "facts": facts}
    save(out, "claims", data)
    return data


def check_dois(dois: list[str], cache: Path) -> dict[str, str]:
    c = CachedClient(cache, surface="doi", min_interval=0.2)
    out = {}
    for d in dois[:80]:
        r = c.get(f"https://doi.org/api/handles/{d}")
        if r.unavailable:
            out[d] = "SOURCE_UNAVAILABLE"
        elif r.status == 200:
            out[d] = "FOUND"
        elif r.status == 404:
            out[d] = "NOT_FOUND"
        else:
            out[d] = f"HTTP_{r.status}"
    c.close()
    return out


# ------------------------------------------------------------------ reconcile / zoomout
def run_reconcile(out: Path) -> dict[str, Any]:
    started = utcnow()
    g = load(out, "github")
    h = load(out, "hf")
    if g is None or h is None:
        return {"state": "ABSTAIN", "reason": "github and hf audit state required; run `szl-audit github` and `szl-audit hf` first"}
    root = Path(g["gh"].get("clone_root") or github.tmp_clone_root())
    rec = reconcile.reconcile(g["gh"], h["hf"], g["files"], root)
    cl = run_claims(g, h, out)
    rec["inventory_drift"] = [c for c in cl["claims"] if c["claim_type"] == "inventory_count" and c["verdict"] in ("STALE", "CONTRADICTED")]
    save(out, "reconcile", rec)
    receipt(out, "reconcile", {"inputs_sha256": sha256_json([len(g["gh"]["repos"]), len(h["hf"]["artifacts"])]), "orphans": len(rec["orphaned_hf"])}, started, "PASS", ["Link-based reconciliation cannot see relationships that are not written down."])
    return rec


def verifier_impls(files: dict[str, Any], root: Path) -> list[str]:
    if all("verifier_impl_paths" in f for f in files.values()):
        return sorted(f"{n}/{p}" for n, f in files.items() for p in f["verifier_impl_paths"])
    out = []
    for name in files:
        base = root / name
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            rel = p.relative_to(base).as_posix()
            if any(x in rel for x in ("node_modules", ".venv", "/tests/", "test_")):
                continue
            if re.search(r"(^|/)(verify|verifier|verify_receipt|receipt_verify|verify_chain|dsse_verify)\.py$", rel):
                out.append(f"{name}/{rel}")
    return sorted(out)


def copied_grep_gates(root: Path, files: dict[str, Any]) -> list[str]:
    import hashlib

    digests: dict[str, list[str]] = {}
    if all("secret_grep_gates" in f for f in files.values()):
        for n, f in files.items():
            for path, dg in f["secret_grep_gates"].items():
                digests.setdefault(dg, []).append(f"{n}/{path}")
        return sorted(max(digests.values(), key=len)) if digests else []
    for name in files:
        wf = root / name / ".github" / "workflows"
        if not wf.is_dir():
            continue
        for p in wf.glob("*.y*ml"):
            t = p.read_text(encoding="utf-8", errors="replace")
            if "grep" in t and ("ghp_" in t or "PRIVATE KEY" in t):
                digests.setdefault(hashlib.sha256(t.encode()).hexdigest()[:12], []).append(f"{name}/.github/workflows/{p.name}")
    return sorted(max(digests.values(), key=len)) if digests else []


def adjudicate(findings_: list[dict[str, Any]], adj: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply adversarial-verification outcomes (state/adjudication.json).

    Each entry matches findings by artifact + title prefix. REFUTED findings are removed (and
    listed under `refuted` with the reviewers' reason); CONFIRMED findings take the reviewed
    severity, title, root cause and structural fix. Matching is by content, not by id, because
    ids are reassigned on every run."""
    out = []
    refuted = adj.setdefault("_applied_refuted", [])
    resolved = adj.setdefault("_applied_resolved", [])
    for f in findings_:
        rule = next((e for e in adj.get("entries", []) if e["artifact"] == f["artifact"] and f["title"].startswith(e["title_prefix"])), None)
        if rule is None:
            out.append(f)
            continue
        if rule["outcome"] == "RESOLVED":
            resolved.append({"artifact": f["artifact"], "title": f["title"], "severity_at_audit": f["severity"], "reason": rule.get("reason", "")})
            continue
        if rule["outcome"] == "REFUTED":
            refuted.append({"artifact": f["artifact"], "title": f["title"], "reason": rule.get("reason", "")})
            continue
        g = dict(f)
        for k in ("severity", "title", "root_cause", "structural_fix", "effort", "blocks", "surface", "confidence"):
            if rule.get(k):
                g[k] = rule[k]
        if rule.get("evidence_append"):
            g["evidence"] = f"{f['evidence']} | Verified by two independent reviewers: {rule['evidence_append']}"
        g["verification"] = rule.get("verification", "CONFIRMED")
        out.append(g)
    return out


def run_zoomout(out: Path) -> dict[str, Any]:
    started = utcnow()
    g, h, rec, cl = load(out, "github"), load(out, "hf"), load(out, "reconcile"), load(out, "claims")
    if None in (g, h, rec, cl):
        return {"state": "ABSTAIN", "reason": "requires github, hf and reconcile state"}
    root = Path(g["gh"].get("clone_root") or github.tmp_clone_root())
    gs, hs, xs = FindingSink("github"), FindingSink("huggingface"), FindingSink("cross-surface")
    findings.github_findings(gs, g["gh"], g["files"], g["smoke"], g["scores"])
    findings.hf_findings(hs, h["hf"], h["conformance"])
    now = utcnow()
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for c in cl["claims"]:
        if c["verdict"] in ("CONTRADICTED", "STALE") and c["claim_type"] in ("inventory_count", "lean_count", "doi"):
            groups.setdefault((c["verdict"], c["claim_type"], c["unit"], str(c["value"])), []).append(c)
    sev = {("CONTRADICTED", "lean_count"): "MEDIUM", ("CONTRADICTED", "inventory_count"): "MEDIUM", ("CONTRADICTED", "doi"): "MEDIUM"}  # counting methods differ across sources: erodes trust, does not block
    for (verdict, ctype, unit, value), cs in sorted(groups.items()):
        c0 = cs[0]
        locs = sorted({c["location"].rsplit(":", 1)[0] for c in cs})
        artifact = locs[0].split(":", 1)[1].rsplit("/README", 1)[0] if len(locs) == 1 else f"{len(locs)} documents"
        label = f"{value} {unit}".strip()
        if verdict == "CONTRADICTED":
            xs.add(sev.get((verdict, ctype), "MEDIUM"), artifact, f"Published {ctype.replace('_', ' ')} '{label}' contradicted by measurement", f"{c0['evidence']} | e.g. {c0['text'][:140]} | locations: {', '.join(locs[:12])}{' …' if len(locs) > 12 else ''}", c0["source_url"], c0["confidence"], "claim-accuracy", "Numbers copied by hand into prose and card footers", "Template every number from one generated, dated JSON with a CI drift check", "S", observed_at=now)
        else:
            xs.add("MEDIUM" if ctype == "lean_count" else "LOW", artifact, f"Dated {ctype.replace('_', ' ')} '{label}' has drifted (STALE, not false)", f"{c0['evidence']} | locations: {', '.join(locs[:12])}{' …' if len(locs) > 12 else ''}", c0["source_url"], c0["confidence"], "stale-claim", "Dated snapshot not regenerated", "Scheduled regeneration + drift check", "S", observed_at=now)
    for c in cl.get("consistency", []):
        xs.add("MEDIUM", "estate", f"Same fact stated with different values ({c['claim_type']} {c['unit']})", json.dumps(c["values"])[:400], "multiple", "MEDIUM", "contradiction", "No single source of truth for the figure", "One generated JSON + templating", "S", observed_at=now)
    for o in rec["orphaned_hf"]:
        if not o.get("private"):
            xs.add("LOW" if o["state"] == "NO_SOURCE_LINK" else "MEDIUM", o["artifact"], f"HF artifact orphaned from source ({o['state']})", f"source links: {o['source_links'] or 'none'}", f"https://huggingface.co/{o['artifact']}", "HIGH", "orphan", "Card has no canonical source field", "Card YAML `source_repo` + reconciliation check on publish", "S", observed_at=now)
    for o in rec["orphaned_repo_claims"]:
        xs.add("MEDIUM", o["repo"], "README links a Hugging Face target that does not exist", f"missing: {o['missing_targets']}", f"https://github.com/szl-holdings/{o['repo']}", "HIGH", "broken-link", "Links hand-written", "Link check in CI against live inventory", "S", observed_at=now)
    for d in rec["version_drift"]:
        xs.add("MEDIUM", d["artifact"], "Published artifact pins a source commit that is no longer HEAD", f"{d['repo']} pinned {d['pinned']} vs HEAD {d['source_head']}", f"https://huggingface.co/{d['artifact']}", "HIGH", "version-drift", "Mirror is a manual snapshot", "Publish from source CI with source SHA recorded; drift alert", "M", observed_at=now)
    impls = verifier_impls(g["files"], root)
    lean = g.get("lean") or {}
    if lean.get("independent_head") and lean.get("head") and lean["independent_head"]["declarations"] != lean["head"]["declarations"]:
        xs.add("MEDIUM", "szl-holdings/lutar-lean", "Published Lean declaration counts depend on a regex definition that excludes attributed/protected declarations", f"org counter HEAD={lean['head']['declarations']} vs independent parser HEAD={lean['independent_head']['declarations']} (sha {str(lean.get('head_sha'))[:8]})", "https://github.com/szl-holdings/.github/blob/main/.github/scripts/lean_numbers.py", "MEDIUM", "defective-verification", "Counting by line regex instead of by the Lean environment", "Enumerate declarations from the elaborated environment in CI", "M", observed_at=now)
    org_ax = set((lean.get("head") or {}).get("axiom_names") or [])
    ind_ax = set((lean.get("independent_head") or {}).get("axiom_names") or [])
    from_comments = sorted(org_ax - ind_ax)
    if org_ax and ind_ax and from_comments:
        xs.add("MEDIUM", "szl-holdings/.github", "Org Lean counter counts axiom-like text inside comments as axioms", f"names reported by .github/scripts/lean_numbers.py at lutar-lean {str(lean.get('head_sha'))[:8]} but absent from a comment-aware parse: {from_comments} (e.g. 'axiom is visible exactly where it is used. -/' in Lutar/Unify/GovernanceSubstrate.lean)", "https://github.com/szl-holdings/.github/blob/main/.github/scripts/lean_numbers.py", "HIGH", "defective-verification", "Line regex without comment state", "Count axioms from the elaborated environment (`#print axioms` / Environment.constants), not by regex", "S", observed_at=now)
    pub = lean.get("published") or {}
    pin = lean.get("pinned") or {}
    for k in ("sorries_noncomment",):
        if pub.get(k) is not None and pin.get(k) is not None and pub[k] != pin[k]:
            xs.add("MEDIUM", "szl-holdings/.github", f"Published {k} not reproducible at its own pinned revision", f"published {pub[k]} at {lean.get('published_sha')} ({lean.get('published_at')}); org counter today at that revision = {pin[k]}", "https://github.com/szl-holdings/.github/blob/main/.github/data/lean_numbers.json", "HIGH", "reproducibility", "Counter script changed after measurement without re-measuring or versioning the method", "Version the counting method and store method hash with each measurement", "S", observed_at=now)
    skipped = [f.evidence for f in hs.items if "skipped" in f.title]
    all_f = gs.to_list() + hs.to_list() + xs.to_list()
    # de-duplicate identical title+artifact pairs (e.g. same verifier defect seen at two revisions)
    seen: set[tuple[str, str]] = set()
    dedup = []
    for f in all_f:
        k = (f["artifact"], f["title"])
        if k in seen:
            continue
        seen.add(k)
        dedup.append(f)
    adj = load(out, "adjudication") or {}
    dedup = adjudicate(dedup, adj)
    for i, f in enumerate(dedup, 1):
        f["id"] = f"F-{i:04d}"
    gh_repos = g["gh"]["repos"]
    spof = []
    top_contribs: dict[str, int] = {}
    for r in gh_repos:
        c = r["detail"].get("contributors")
        if isinstance(c, list):
            for x in c:
                if x.get("type") != "Bot" and not str(x.get("login", "")).endswith("[bot]"):
                    top_contribs[x["login"]] = top_contribs.get(x["login"], 0) + x["contributions"]
    if top_contribs:
        tot = sum(top_contribs.values())
        lead, n = max(top_contribs.items(), key=lambda kv: kv[1])
        spof.append({"type": "maintainer concentration", "evidence": f"top human contributor accounts for {n}/{tot} ({100 * n / tot:.0f}%) of contributions across {len(gh_repos)} repos", "contributors_total": len(top_contribs)})
    bf = {r["name"]: findings.bus_factor(r) for r in gh_repos if r["name"] in findings.FLAGSHIPS}
    spof.append({"type": "bus factor per flagship (min contributors for 50% of commits)", "evidence": bf})
    ev = {
        "claims": cl["claims"],
        "consistency": cl.get("consistency", []),
        "conformance": h["conformance"],
        "reconcile": rec,
        "verifier_implementations": impls,
        "copied_secret_grep_workflows": copied_grep_gates(root, g["files"]),
        "skipped_sig_pass": skipped[0] if skipped else None,
        "spof": spof,
        "boundary_violations": [f for f in dedup if f["category"] in ("vacuous-pass",)],
    }
    bandaids = zoomout.detect_bandaids(ev)
    sysg = zoomout.systemic(ev)
    table = zoomout.remediation_table(zoomout.evaluate_fixes(dedup))
    z = {"refuted": adj.get("_applied_refuted", []), "resolved": adj.get("_applied_resolved", []), "findings": dedup, "bandaids": bandaids, "systemic": sysg, "remediation": table, "verifier_implementations": impls, "spof": spof, "bus_factor": bf}
    save(out, "zoomout", z)
    receipt(out, "zoomout", {"inputs_sha256": sha256_json([len(dedup)]), "findings": len(dedup)}, started, "PASS", ["Severity assignment is rule-based; see findings.py for rules."])
    return z
