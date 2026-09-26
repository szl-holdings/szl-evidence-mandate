"""GitHub organisation audit (Phase 2): collection, shallow clones, file analysis, scorecards."""

from __future__ import annotations

import re
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.http import CachedClient, Response, paginate
from ..models import NOT_TESTED, UNAVAILABLE, UNKNOWN, utcnow
from ..safety import redact, rmtree_force, run_argv, safe_walk
from .common import Axis, github_token
from .secrets_scan import scan_tree

API = "https://api.github.com"
DOC_FILES = {
    "README": r"^readme(\.(md|rst|txt))?$",
    "LICENSE": r"^(license|licence|copying)(\.(md|txt))?$|^license-.*",
    "CONTRIBUTING": r"^contributing(\.(md|rst|txt))?$",
    "SECURITY": r"^security(\.(md|txt))?$",
    "CHANGELOG": r"^(changelog|changes|history)(\.(md|rst|txt))?$",
    "CITATION.cff": r"^citation\.cff$",
    ".gitignore": r"^\.gitignore$",
    "CODEOWNERS": r"^codeowners$",
}
LOCKFILES = {"poetry.lock", "uv.lock", "Pipfile.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "go.sum", "requirements.lock", "bun.lockb", "lake-manifest.json", "pdm.lock"}
CONTAINERS = {"dockerfile", "containerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"}
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".lake", "dist", "build", ".next", "target"}

CODE_RISKS = [
    ("shell_true", re.compile(r"shell\s*=\s*True"), {".py"}),
    ("os_system", re.compile(r"\bos\.system\("), {".py"}),
    ("pickle_load", re.compile(r"\bpickle\.loads?\(|\bcloudpickle\.loads?\(|\bjoblib\.load\("), {".py"}),
    ("torch_load_unsafe", re.compile(r"\btorch\.load\((?![^)]*weights_only\s*=\s*True)"), {".py"}),
    ("yaml_unsafe_load", re.compile(r"\byaml\.load\((?![^)]*Loader\s*=\s*(yaml\.)?(Safe|CSafe)Loader)|\byaml\.unsafe_load\("), {".py"}),
    ("eval_exec", re.compile(r"(?<![\w.])(eval|exec)\s*\("), {".py"}),
    ("tar_extractall_unfiltered", re.compile(r"\.extractall\((?![^)]*filter\s*=)"), {".py"}),
    ("js_eval", re.compile(r"(?<![\w.])eval\s*\(|new Function\s*\("), {".js", ".ts", ".mjs", ".cjs", ".tsx"}),
    ("child_process_exec", re.compile(r"child_process[\s\S]{0,40}\bexec\(|\bexecSync\("), {".js", ".ts", ".mjs", ".cjs"}),
]
TRAVERSAL_DEFENSE = re.compile(r"is_relative_to\(|os\.path\.commonpath|\.resolve\(\)\.relative_to|realpath\(|path traversal|safe_join|secure_filename")
SCOPING = re.compile(r"(?i)(does not (prove|establish|claim|guarantee|certify)|not (a|an) (proof|guarantee)|what (this|it) (is not|does not)|non-?claims?|limitations|out of scope|not established|do(es)? not demonstrate)")
QUICKSTART = re.compile(r"(?im)^#+\s*(quick\s*start|getting started|install(ation)?|usage|run(ning)? locally|try it)\b")
INSTALL_CMD = re.compile(r"(pip install|uv (pip|sync|run)|npm (i|install|ci)|pnpm (i|install)|yarn( install)?|cargo (build|run)|lake build|docker (run|compose)|make |python -m|npx )")
MATURITY = re.compile(r"(?i)\b(alpha|beta|experimental|prototype|pre-?release|research|stable|production|deprecated|archived|v\d+\.\d+|preview|draft|wip|work in progress|pre-launch|simulated|reference implementation)\b")
BOUNDARY = {
    "integrity": re.compile(r"(?i)\bintegrity\b"),
    "performance": re.compile(r"(?i)\b(performance|accuracy|benchmark|latency|throughput)\b"),
    "validity": re.compile(r"(?i)\b(validity|valid(ated)? (for|in)|scientific(ally)? valid|external validity|fitness for (use|purpose))\b"),
}
CI_GATE = re.compile(r"(?i)\b(ci|test|tests|build|lint|check|verify|pytest|quality|conformance)\b")
URL = re.compile(r"https?://[^\s)\]>\"'`]+")


def _age_days(ts: str | None, now: datetime) -> int | str:
    if not ts:
        return UNKNOWN
    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (now - t).days


class GitHubCollector:
    def __init__(self, client: CachedClient, org: str, authenticated: bool):
        self.c = client
        self.org = org
        self.auth = authenticated

    def org_meta(self) -> Response:
        return self.c.get(f"{API}/orgs/{self.org}")

    def list_repos(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return paginate(self.c, f"{API}/orgs/{self.org}/repos", {"per_page": 100, "type": "all", "sort": "full_name"})

    def _get(self, path: str, **params: Any) -> Response:
        return self.c.get(f"{API}{path}", params=params or None)

    @staticmethod
    def _val(r: Response, fn: Any = None) -> Any:
        if r.unavailable:
            return {"state": "SOURCE_UNAVAILABLE", "detail": r.detail}
        if r.status in (403, 404) and not r.ok:
            try:
                msg = (r.json() or {}).get("message", "")
            except ValueError:
                msg = ""
            return {"state": UNAVAILABLE, "http": r.status, "message": str(msg)[:120]}
        if not r.ok:
            return {"state": UNAVAILABLE, "http": r.status}
        data = r.json()
        return fn(data) if fn else data

    def repo_detail(self, repo: dict[str, Any]) -> dict[str, Any]:
        full = repo["full_name"]
        name = repo["name"]
        d: dict[str, Any] = {"retrieved_at": utcnow()}
        d["repo"] = self._val(self._get(f"/repos/{full}"), lambda x: {"subscribers_count": x.get("subscribers_count"), "network_count": x.get("network_count")})
        d["languages"] = self._val(self._get(f"/repos/{full}/languages"))
        d["releases"] = self._val(self._get(f"/repos/{full}/releases", per_page=100), lambda xs: [
            {
                "tag": x.get("tag_name"),
                "name": x.get("name"),
                "published_at": x.get("published_at"),
                "draft": x.get("draft"),
                "prerelease": x.get("prerelease"),
                "body_len": len(x.get("body") or ""),
                "assets": [{"name": a.get("name"), "size": a.get("size"), "digest": a.get("digest") or UNAVAILABLE, "downloads": a.get("download_count")} for a in x.get("assets", [])],
            }
            for x in xs
        ])
        d["tags"] = self._val(self._get(f"/repos/{full}/tags", per_page=100), lambda xs: [{"name": t["name"], "sha": t["commit"]["sha"]} for t in xs])
        head = self._get(f"/repos/{full}/commits/{repo.get('default_branch') or 'HEAD'}")
        d["head"] = self._val(head, lambda x: {"sha": x.get("sha"), "date": ((x.get("commit") or {}).get("committer") or {}).get("date"), "author": ((x.get("author") or {}) or {}).get("login"), "verified": ((x.get("commit") or {}).get("verification") or {}).get("verified")})
        d["branch_protection"] = self._val(self._get(f"/repos/{full}/branches/{repo.get('default_branch')}/protection"), lambda x: {"enabled": True, "required_reviews": (x.get("required_pull_request_reviews") or {}).get("required_approving_review_count"), "required_status_checks": bool(x.get("required_status_checks")), "enforce_admins": (x.get("enforce_admins") or {}).get("enabled")})
        rules = self._get(f"/repos/{full}/rules/branches/{repo.get('default_branch')}")
        d["rulesets"] = self._val(rules, lambda xs: [r.get("type") for r in xs])
        d["workflows"] = self._val(self._get(f"/repos/{full}/actions/workflows", per_page=100), lambda x: [{"name": w.get("name"), "path": w.get("path"), "state": w.get("state"), "id": w.get("id"), "total_count": x.get("total_count")} for w in x.get("workflows", [])])
        d["latest_runs"] = self._val(self._get(f"/repos/{full}/actions/runs", per_page=60, branch=repo.get("default_branch")), lambda x: [{"name": r.get("name"), "conclusion": r.get("conclusion"), "status": r.get("status"), "created_at": r.get("created_at"), "event": r.get("event"), "html_url": r.get("html_url"), "workflow_id": r.get("workflow_id"), "path": r.get("path")} for r in x.get("workflow_runs", [])])
        d["dependabot_alerts"] = self._val(self._get(f"/repos/{full}/dependabot/alerts", state="open", per_page=100), lambda xs: {"open": len(xs), "lower_bound": len(xs) >= 100, "by_severity": _count([(a.get("security_advisory") or {}).get("severity") for a in xs])})
        d["code_scanning_alerts"] = self._val(self._get(f"/repos/{full}/code-scanning/alerts", state="open", per_page=100), lambda xs: {"open": len(xs), "lower_bound": len(xs) >= 100})
        d["secret_scanning_alerts"] = self._val(self._get(f"/repos/{full}/secret-scanning/alerts", state="open", per_page=100), lambda xs: {"open": len(xs), "lower_bound": len(xs) >= 100, "types": sorted({a.get("secret_type") for a in xs})})
        d["contributors"] = self._val(self._get(f"/repos/{full}/contributors", per_page=100, anon="1"), lambda xs: [{"login": x.get("login") or x.get("name") or "anonymous", "type": x.get("type"), "contributions": x.get("contributions")} for x in xs])
        d["open_issues"] = self._val(self._get(f"/repos/{full}/issues", state="open", per_page=100, sort="created", direction="asc"), lambda xs: [{"number": i.get("number"), "created_at": i.get("created_at"), "is_pr": "pull_request" in i} for i in xs])
        d["branches"] = self._branches(full) if self.auth else {"state": UNAVAILABLE, "detail": "GraphQL requires authentication"}
        d["latest_tag_signature"] = self._tag_signature(full, d)
        d["_name"] = name
        return d

    def _branches(self, full: str) -> Any:
        owner, name = full.split("/")
        q = """query($o:String!,$n:String!){repository(owner:$o,name:$n){refs(refPrefix:"refs/heads/",first:100){totalCount nodes{name target{... on Commit{committedDate}}}}}}"""
        r = self.c.request("POST", f"{API}/graphql", json_body={"query": q, "variables": {"o": owner, "n": name}})
        if not r.ok:
            return {"state": "SOURCE_UNAVAILABLE" if r.unavailable else UNAVAILABLE, "http": r.status}
        data = r.json()
        refs = (((data.get("data") or {}).get("repository") or {}).get("refs")) or {}
        return {"total": refs.get("totalCount"), "branches": [{"name": n["name"], "committed": (n.get("target") or {}).get("committedDate")} for n in refs.get("nodes", [])]}

    def _tag_signature(self, full: str, d: dict[str, Any]) -> Any:
        rel = d.get("releases")
        if not isinstance(rel, list) or not rel:
            return {"state": "NO_RELEASE"}
        tag = rel[0]["tag"]
        r = self._get(f"/repos/{full}/git/ref/tags/{tag}")
        if not r.ok:
            return {"state": UNAVAILABLE, "http": r.status}
        obj = r.json().get("object", {})
        if obj.get("type") != "tag":
            return {"tag": tag, "annotated": False, "verified": False, "reason": "lightweight tag (cannot carry a signature)"}
        t = self._get(f"/repos/{full}/git/tags/{obj.get('sha')}")
        if not t.ok:
            return {"tag": tag, "annotated": True, "verified": UNAVAILABLE}
        v = t.json().get("verification") or {}
        return {"tag": tag, "annotated": True, "verified": v.get("verified"), "reason": v.get("reason")}


def _count(xs: list[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in xs:
        out[str(x)] = out.get(str(x), 0) + 1
    return out


# ------------------------------------------------------------------ cloning
def clone_repo(full: str, dest: Path, timeout: int = 900) -> dict[str, Any]:
    if dest.exists() and not rmtree_force(dest):
        return {"ok": False, "exit_code": "CLEANUP_FAILED", "output": f"could not remove stale clone at {dest}"}
    gh = shutil.which("gh")
    git = shutil.which("git") or "git"
    # core.autocrlf=false: byte-exact checkout (hash/manifest tests); blobs > 2 MB are still omitted
    base = ["--depth", "1", "--filter=blob:limit=2m", "--no-tags", "-c", "core.longpaths=true", "-c", "core.symlinks=false", "-c", "core.autocrlf=false", "-c", "core.eol=lf"]
    if gh:
        argv = [gh, "repo", "clone", full, str(dest), "--", *base]
    else:
        argv = [git, "clone", *base, f"https://github.com/{full}.git", str(dest)]
    res = run_argv(argv, timeout=timeout, max_output=1500)
    res["argv"] = [redact(a) for a in res["argv"]]
    res["ok"] = res["exit_code"] == 0 and dest.exists()
    if res["ok"]:
        # Partial clone may leave large blobs unfetched; record which were skipped.
        r = run_argv([git, "-C", str(dest), "rev-parse", "HEAD"], timeout=30)
        res["head"] = r["output"].strip()[:40]
    return res


# ------------------------------------------------------------------ file analysis
def detect_license_text(text: str) -> str:
    t = text.lower()
    if "apache license" in t and "version 2.0" in t:
        return "Apache-2.0"
    if "permission is hereby granted, free of charge" in t:
        return "MIT"
    if "gnu affero general public license" in t:
        return "AGPL-3.0"
    if "gnu lesser general public license" in t:
        return "LGPL"
    if "gnu general public license" in t:
        return "GPL-3.0" if "version 3" in t else "GPL"
    if "mozilla public license" in t:
        return "MPL-2.0"
    if "redistribution and use in source and binary forms" in t:
        return "BSD-3-Clause" if "neither the name" in t else "BSD-2-Clause"
    if "creative commons" in t and "attribution 4.0" in t:
        return "CC-BY-4.0"
    if "business source license" in t:
        return "BUSL-1.1"
    if "all rights reserved" in t or "proprietary" in t:
        return "PROPRIETARY"
    if "unlicense" in t or "this is free and unencumbered" in t:
        return "Unlicense"
    return "UNRECOGNISED"


def declared_package_licenses(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    pp = root / "pyproject.toml"
    if pp.exists():
        import tomllib

        try:
            d = tomllib.loads(pp.read_text(encoding="utf-8"))
            lic = (d.get("project") or {}).get("license")
            if isinstance(lic, dict):
                lic = lic.get("text") or lic.get("file")
            if lic:
                out["pyproject.toml"] = str(lic)[:80]
        except (tomllib.TOMLDecodeError, UnicodeDecodeError):
            out["pyproject.toml"] = "UNPARSEABLE"
    pj = root / "package.json"
    if pj.exists():
        import json

        try:
            lic = json.loads(pj.read_text(encoding="utf-8")).get("license")
            if lic:
                out["package.json"] = str(lic)[:80]
        except (ValueError, UnicodeDecodeError):
            out["package.json"] = "UNPARSEABLE"
    return out


def analyze_clone(root: Path) -> dict[str, Any]:
    files = [f for f in safe_walk(root, max_files=200_000) if not any(p in SKIP for p in f.relative_to(root).parts)]
    rels = [f.relative_to(root).as_posix() for f in files]
    top = {Path(r).name.lower(): r for r in rels if "/" not in r or r.startswith((".github/", "docs/"))}
    presence: dict[str, str | None] = {}
    for key, pat in DOC_FILES.items():
        rx = re.compile(pat, re.I)
        hit = next((r for n, r in sorted(top.items()) if rx.match(n)), None)
        presence[key] = hit
    ci = [r for r in rels if r.startswith(".github/workflows/") and r.endswith((".yml", ".yaml"))]
    ci += [r for r in rels if Path(r).name in {".gitlab-ci.yml", "azure-pipelines.yml", ".travis.yml"} or r.startswith(".circleci/")]
    tests_dirs = sorted({r.split("/")[0] for r in rels if re.match(r"^(tests?|__tests__|spec)/", r)} | {"/".join(r.split("/")[:2]) for r in rels if re.match(r"^[^/]+/(tests?|__tests__)/", r)})
    test_files = [r for r in rels if re.search(r"(^|/)(test_[^/]+\.py|[^/]+_test\.py|[^/]+\.(test|spec)\.(js|ts|tsx|mjs))$", r)]
    test_count = 0
    for r in test_files[:3000]:
        try:
            txt = (root / r).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        test_count += len(re.findall(r"(?m)^\s*(async\s+)?def test_\w+", txt)) + len(re.findall(r"(?m)^\s*(it|test)\(\s*['\"`]", txt))
    locks = sorted(r for r in rels if Path(r).name in LOCKFILES)
    containers = sorted(r for r in rels if Path(r).name.lower() in CONTAINERS)
    manifests = {k: (root / k).exists() for k in ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "package.json", "Cargo.toml", "go.mod", "lakefile.lean", "lakefile.toml", "Makefile"]}
    pinned = _pin_state(root)
    lean_files = [r for r in rels if r.endswith(".lean")]
    risks: dict[str, list[str]] = {}
    defense = False
    for r in rels:
        suf = Path(r).suffix.lower()
        if suf not in {".py", ".js", ".ts", ".mjs", ".cjs", ".tsx"}:
            continue
        p = root / r
        try:
            if p.stat().st_size > 1_000_000:
                continue
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if TRAVERSAL_DEFENSE.search(txt):
            defense = True
        for name, rx, sufs in CODE_RISKS:
            if suf in sufs:
                for m in rx.finditer(txt):
                    line = txt.count("\n", 0, m.start()) + 1
                    risks.setdefault(name, []).append(f"{r}:{line}")
    readme = ""
    if presence.get("README"):
        try:
            readme = (root / presence["README"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            readme = ""
    license_text_kind = None
    if presence.get("LICENSE"):
        try:
            license_text_kind = detect_license_text((root / presence["LICENSE"]).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            license_text_kind = UNKNOWN
    secrets = scan_tree(root)
    from .reconcile import scan_receipt_schemas

    schema_ids = scan_receipt_schemas(root)
    verifier_paths = sorted(r for r in rels if r.endswith(".py") and not re.search(r"(^|/)(tests?/|test_)", r) and re.search(r"(^|/)(verify|verifier|verify_receipt|receipt_verify|verify_chain|dsse_verify)\.py$", r))
    grep_gates: dict[str, str] = {}
    for r in ci:
        try:
            t = (root / r).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "grep" in t and ("ghp_" in t or "PRIVATE KEY" in t):
            import hashlib

            grep_gates[r] = hashlib.sha256(t.encode()).hexdigest()[:12]
    return {
        "receipt_schema_ids": schema_ids,
        "verifier_impl_paths": verifier_paths,
        "secret_grep_gates": grep_gates,
        "file_count": len(rels),
        "presence": presence,
        "ci_configs": ci,
        "tests_dirs": tests_dirs,
        "test_files": len(test_files),
        "test_functions_static": test_count,
        "lockfiles": locks,
        "containers": containers,
        "manifests": {k: v for k, v in manifests.items() if v},
        "dependency_pinning": pinned,
        "lean_files": len(lean_files),
        "code_risks": {k: {"count": len(v), "locations": v[:25]} for k, v in sorted(risks.items())},
        "path_traversal_defense_seen": defense,
        "readme_text": readme,
        "readme_len": len(readme),
        "license_file_kind": license_text_kind,
        "declared_package_licenses": declared_package_licenses(root),
        "secrets": secrets,
        "extensions": _count([Path(r).suffix.lower() or "<none>" for r in rels]),
    }


def _pin_state(root: Path) -> dict[str, Any]:
    req = root / "requirements.txt"
    out: dict[str, Any] = {}
    if req.exists():
        lines = [line.strip() for line in req.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.strip().startswith(("#", "-"))]
        out["requirements_total"] = len(lines)
        out["requirements_pinned_eq"] = sum("==" in line for line in lines)
    pp = root / "pyproject.toml"
    if pp.exists():
        import tomllib

        try:
            deps = (tomllib.loads(pp.read_text(encoding="utf-8")).get("project") or {}).get("dependencies") or []
            out["pyproject_deps"] = len(deps)
            out["pyproject_deps_pinned_eq"] = sum("==" in d for d in deps)
        except (tomllib.TOMLDecodeError, UnicodeDecodeError):
            out["pyproject_deps"] = "UNPARSEABLE"
    return out


# ------------------------------------------------------------------ scorecard
def ci_axis(wfs: list[Any], runs: list[dict[str, Any]], now: datetime) -> Axis:
    """Grade the merge-gate workflows (push/PR-triggered test/build/lint); report failing monitors separately."""
    by_path = {w.get("path"): w.get("name") for w in wfs if isinstance(w, dict) and w.get("path")}
    by_id = {w.get("id"): w.get("name") for w in wfs if isinstance(w, dict) and w.get("id")}

    def wf_key(run: dict[str, Any]) -> str:
        if run.get("workflow_id") in by_id:
            return by_id[run["workflow_id"]]
        if run.get("path") in by_path:
            return by_path[run["path"]]
        name = run.get("name") or "?"
        return by_path.get(name, name)  # stale startup failures are named after the workflow file

    latest: dict[str, dict[str, Any]] = {}
    for run in runs:  # newest first
        latest.setdefault(wf_key(run), run)
    gate = {k: r for k, r in latest.items() if CI_GATE.search(k) and r.get("event") in ("push", "pull_request", "merge_group", "workflow_dispatch")}
    monitors_failing = sorted(k for k, r in latest.items() if k not in gate and r.get("conclusion") == "failure")
    if not gate:
        return Axis("PARTIAL", f"{len(wfs)} workflows; no push/PR-triggered test/build run among the last {len(runs)} default-branch runs; failing non-gate workflows: {monitors_failing or 'none'}", "MEDIUM")
    bad = sorted(k for k, r in gate.items() if r.get("conclusion") not in ("success", "skipped", "neutral"))
    newest = max(gate.values(), key=lambda r: r.get("created_at") or "")
    age = _age_days(newest.get("created_at"), now)
    summary = ", ".join(f"{k}={r.get('conclusion')}" for k, r in sorted(gate.items()))[:300]
    state = "FAIL" if bad else ("PASS" if isinstance(age, int) and age <= 30 else "PARTIAL")
    count = f">={len(wfs)} (first page only)" if len(wfs) >= 100 else str(len(wfs))
    return Axis(state, f"{count} workflows; gate workflows latest (grouped by workflow): {summary}; newest gate run {age}d ago; failing non-gate workflows: {monitors_failing or 'none'}")



def scorecard(repo: dict[str, Any], det: dict[str, Any], files: dict[str, Any] | None, smoke: dict[str, Any] | None, links: dict[str, Any] | None, now: datetime) -> dict[str, dict[str, str]]:
    ax: dict[str, Axis] = {}
    desc = (repo.get("description") or "").strip()
    readme = (files or {}).get("readme_text", "")
    # Identity
    if not desc:
        ax["identity"] = Axis("FAIL", "no repository description")
    else:
        has_mat = bool(MATURITY.search(desc) or MATURITY.search(readme[:3000]))
        has_non = bool(SCOPING.search(desc) or SCOPING.search(readme))
        st = "PASS" if (has_mat and has_non) else "PARTIAL"
        ax["identity"] = Axis(st, f"description present ({len(desc)} chars); maturity stated={has_mat}; non-claims stated={has_non}", "MEDIUM")
    # License
    api_lic = ((repo.get("license") or {}) or {}).get("spdx_id")
    if files is None:
        ax["license"] = Axis("PARTIAL", f"metadata license={api_lic}; LICENSE file NOT_TESTED (not cloned)", "MEDIUM") if api_lic else Axis("NOT_TESTED", "metadata: none; LICENSE file NOT_TESTED (not cloned)", "MEDIUM")
    else:
        lf = files["presence"].get("LICENSE")
        pk = files.get("declared_package_licenses", {})
        kind = files.get("license_file_kind")
        mism = []
        if api_lic and api_lic not in ("NOASSERTION",) and kind not in (None, "UNRECOGNISED") and kind.split("-")[0].upper() != api_lic.split("-")[0].upper():
            mism.append(f"metadata {api_lic} vs LICENSE text {kind}")
        for src, v in pk.items():
            if kind and kind not in ("UNRECOGNISED", "PROPRIETARY") and v.split("-")[0].upper() not in kind.upper() and "SEE LICENSE" not in v.upper():
                mism.append(f"{src} declares {v} vs LICENSE text {kind}")
        if not lf and (api_lic or pk):
            ax["license"] = Axis("FAIL", f"license declared (metadata={api_lic}, packages={pk}) but no LICENSE file - CONTRADICTED")
        elif not lf:
            ax["license"] = Axis("FAIL", "no LICENSE file and no license metadata")
        elif mism:
            ax["license"] = Axis("FAIL", "; ".join(mism))
        elif api_lic in (None, "NOASSERTION") and kind in ("UNRECOGNISED", "PROPRIETARY"):
            ax["license"] = Axis("PARTIAL", f"LICENSE file present ({lf}) but not a recognised SPDX licence (text kind={kind}); metadata={api_lic}")
        else:
            ax["license"] = Axis("PASS", f"LICENSE {lf} ({kind}); metadata {api_lic}")
    # Provenance
    if files is None:
        ax["provenance"] = Axis("NOT_TESTED", "not cloned")
    else:
        locks = files["lockfiles"]
        pin = files["dependency_pinning"]
        has_manifest = bool(files["manifests"])
        if not has_manifest:
            ax["provenance"] = Axis("NOT_TESTED", "no package manifest (not a buildable package)", "MEDIUM")
        elif locks and (files["containers"] or "Makefile" in files["manifests"]):
            ax["provenance"] = Axis("PASS", f"lockfiles={locks[:3]}; build path={files['containers'][:2] or ['Makefile']}")
        elif locks or (pin.get("requirements_total") and pin.get("requirements_pinned_eq") == pin.get("requirements_total")):
            ax["provenance"] = Axis("PARTIAL", f"lockfiles={locks[:3]}; pinning={pin}; no reproducible build definition")
        else:
            ax["provenance"] = Axis("FAIL", f"no lockfile; pinning={pin}")
    # Tests
    if files is None:
        ax["tests"] = Axis("NOT_TESTED", "not cloned")
    else:
        stat = f"test files={files['test_files']}, static test functions={files['test_functions_static']}, dirs={files['tests_dirs'][:3]}"
        t = (smoke or {}).get("tests") or {}
        if t.get("state") == "PASSED":
            ax["tests"] = Axis("PASS", f"{stat}; executed: {t.get('summary')}")
        elif t.get("state") in ("FAILED", "ERROR"):
            conf = "HIGH" if t.get("attribution") == "REPO_DEFECT" else "MEDIUM"
            ax["tests"] = Axis("FAIL", f"{stat}; executed: {t.get('summary')}; attribution {t.get('attribution', 'UNKNOWN')}: {t.get('reason', '')}", conf)
        elif t.get("state") in ("HOST_LIMITED", "UNRESOLVED"):
            ax["tests"] = Axis("PARTIAL", f"{stat}; executed: {t.get('summary')}; {t['state']}: {t.get('reason')}", "LOW")
        elif files["test_files"]:
            ax["tests"] = Axis("PARTIAL", f"{stat}; execution NOT_TESTED in this run", "MEDIUM")
        else:
            ax["tests"] = Axis("FAIL", "no test files found")
    # CI
    wfs = det.get("workflows")
    runs = det.get("latest_runs")
    if isinstance(wfs, dict):
        ax["ci"] = Axis("NOT_TESTED", f"workflows {wfs.get('state')}")
    elif not wfs:
        ax["ci"] = Axis("FAIL", "no GitHub Actions workflows")
    elif isinstance(runs, list) and runs:
        ax["ci"] = ci_axis(wfs, runs, now)
    else:
        ax["ci"] = Axis("PARTIAL", f"{len(wfs)} workflows, no runs on default branch visible")
    # Release integrity
    rel = det.get("releases")
    sig = det.get("latest_tag_signature") or {}
    if isinstance(rel, dict):
        ax["release_integrity"] = Axis("NOT_TESTED", f"releases {rel.get('state')}")
    elif not rel:
        ax["release_integrity"] = Axis("FAIL", "no releases published")
    else:
        latest = rel[0]
        assets = latest["assets"]
        hashed = [a for a in assets if a["digest"] != UNAVAILABLE] or [a for a in assets if re.search(r"(?i)(sha256|checksums|\.sig|\.intoto|\.sigstore)", a["name"] or "")]
        parts = [f"latest={latest['tag']}", f"notes={latest['body_len']} chars", f"assets={len(assets)} hashed={len(hashed)}", f"tag signed={sig.get('verified')}"]
        if latest["body_len"] > 0 and (sig.get("verified") is True or (assets and len(hashed) == len(assets))):
            ax["release_integrity"] = Axis("PASS", "; ".join(parts))
        else:
            ax["release_integrity"] = Axis("PARTIAL", "; ".join(parts))
    # Security posture
    if files is None:
        ax["security_posture"] = Axis("NOT_TESTED", "not cloned")
    else:
        live = [h for h in files["secrets"]["hits"] if h["likely_live"]]
        risks = files["code_risks"]
        sec_md = files["presence"].get("SECURITY")
        serious = {k: v["count"] for k, v in risks.items() if k in ("shell_true", "pickle_load", "yaml_unsafe_load", "torch_load_unsafe", "os_system", "tar_extractall_unfiltered")}
        ssa = det.get("secret_scanning_alerts")
        platform_secrets = ssa.get("open", 0) if isinstance(ssa, dict) and "open" in ssa else None
        ev = f"SECURITY.md={'yes' if sec_md else 'no'}; likely-live secret hits={len(live)}; open secret-scanning alerts={platform_secrets if platform_secrets is not None else 'UNAVAILABLE'}{' ' + str(ssa.get('types')) if platform_secrets else ''}; risky patterns={serious or 'none'}; traversal-defense seen={files['path_traversal_defense_seen']}"
        if live or platform_secrets:
            ax["security_posture"] = Axis("FAIL", ev)
        elif sec_md and not serious:
            ax["security_posture"] = Axis("PASS", ev, "MEDIUM")
        else:
            ax["security_posture"] = Axis("PARTIAL", ev, "MEDIUM")
    # Docs
    if files is None:
        ax["docs"] = Axis("NOT_TESTED", "not cloned")
    elif not readme:
        ax["docs"] = Axis("FAIL", "no README")
    else:
        qs = bool(QUICKSTART.search(readme))
        cmd = bool(INSTALL_CMD.search(readme))
        measured = smoke.get("time_to_first_run_s") if smoke else None
        extra = f"; measured time-to-first-run={measured}s" if measured is not None else ""
        if qs and cmd:
            qs_ok = smoke.get("quickstart_ok") if smoke else None
            state = "PARTIAL" if qs_ok is False and smoke.get("harness_revision") == "fix2" else "PASS"
            ax["docs"] = Axis(state, f"quick-start section and install command present{extra}", "MEDIUM")
        elif cmd or qs:
            ax["docs"] = Axis("PARTIAL", f"quickstart heading={qs}, install command={cmd}{extra}", "MEDIUM")
        else:
            ax["docs"] = Axis("FAIL", f"README ({len(readme)} chars) has no quick start or install command")
    # Honest scoping
    if files is None:
        ax["honest_scoping"] = Axis("NOT_TESTED", "not cloned")
    else:
        m = SCOPING.search(readme)
        ax["honest_scoping"] = Axis("PASS" if m else "FAIL", f"scoping statement: {m.group(0)!r}" if m else "no explicit statement of what is not proven", "MEDIUM")
    # Evidence boundary
    if files is None:
        ax["evidence_boundary"] = Axis("NOT_TESTED", "not cloned")
    else:
        found = [k for k, rx in BOUNDARY.items() if rx.search(readme)]
        st = "PASS" if len(found) == 3 else ("PARTIAL" if found else "FAIL")
        ax["evidence_boundary"] = Axis(st, f"boundary categories named: {found or 'none'}", "LOW")
    # Cross-links
    if links is None:
        ax["cross_links"] = Axis("NOT_TESTED", "links not resolved")
    else:
        broken = links.get("broken", [])
        total = links.get("checked", 0)
        if total == 0:
            ax["cross_links"] = Axis("PARTIAL", "no source/HF/product/proof links in README", "MEDIUM")
        else:
            ax["cross_links"] = Axis("PASS" if not broken else "FAIL", f"{total} links checked; broken={broken[:5]}")
    # Maintenance
    age = _age_days(repo.get("pushed_at"), now)
    issues = det.get("open_issues")
    oldest = UNKNOWN
    if isinstance(issues, list):
        real = [i for i in issues if not i["is_pr"]]
        oldest = f"{_age_days(real[0]['created_at'], now)}d" if real else "none open"
    br = det.get("branches")
    abandoned: Any = UNKNOWN
    if isinstance(br, dict) and "branches" in br:
        abandoned = sum(1 for b in br["branches"] if b["name"] != repo.get("default_branch") and isinstance(_age_days(b["committed"], now), int) and _age_days(b["committed"], now) > 90)
    ev = f"last push {age}d ago; oldest open issue {oldest}; abandoned branches (>90d) {abandoned}"
    if repo.get("archived"):
        ax["maintenance"] = Axis("PARTIAL", "archived; " + ev)
    elif isinstance(age, int) and age <= 90 and (not isinstance(abandoned, int) or abandoned <= 5):
        ax["maintenance"] = Axis("PASS", ev)
    elif isinstance(age, int) and age <= 180:
        ax["maintenance"] = Axis("PARTIAL", ev)
    else:
        ax["maintenance"] = Axis("FAIL", ev)
    return {k: v.to_dict() for k, v in ax.items()}


def tmp_clone_root() -> Path:
    base = Path(tempfile.gettempdir()) / "szlc"
    base.mkdir(parents=True, exist_ok=True)
    return base


def collect(org: str, cache_dir: Path, clone: bool, clone_root: Path | None = None, workers: int = 4, dry_run: bool = False) -> dict[str, Any]:
    token, token_src = github_token()
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    client = CachedClient(cache_dir, headers=headers, surface="github", min_interval=0.05)
    col = GitHubCollector(client, org, bool(token))
    started = utcnow()
    orgr = col.org_meta()
    org_meta = orgr.json() if orgr.ok else {"state": orgr.status}
    repos, meta = col.list_repos()
    out: dict[str, Any] = {
        "org": org,
        "started_at": started,
        "auth": {"authenticated": bool(token), "source": token_src},
        "org_meta": {k: org_meta.get(k) for k in ("login", "description", "blog", "public_repos", "created_at", "is_verified", "two_factor_requirement_enabled", "members_can_create_public_repositories")} if isinstance(org_meta, dict) else org_meta,
        "listing": meta,
        "repos": [],
    }
    if dry_run:
        out["dry_run"] = True
        out["repos"] = [{"name": r["name"]} for r in repos]
        client.close()
        return out
    with ThreadPoolExecutor(max_workers=workers) as ex:
        details = list(ex.map(col.repo_detail, repos))
    root = clone_root or tmp_clone_root()
    clone_results: dict[str, Any] = {}
    if clone:
        targets = [r for r in repos if not r.get("archived")]

        head_by_name = {r["name"]: (d.get("head") or {}).get("sha") if isinstance(d.get("head"), dict) else None for r, d in zip(repos, details, strict=True)}

        def _do(r: dict[str, Any]) -> tuple[str, dict[str, Any]]:
            dest = root / r["name"]
            want = head_by_name.get(r["name"])
            if want and (dest / ".git").exists():
                git = shutil.which("git") or "git"
                have = run_argv([git, "-C", str(dest), "rev-parse", "HEAD"], timeout=30)["output"].strip()
                if have == want:
                    run_argv([git, "-C", str(dest), "clean", "-xdfq"], timeout=300)
                    return r["name"], {"ok": True, "head": have, "reused": True, "note": "existing shallow clone reused: local HEAD equals API HEAD sha; working tree cleaned"}
            return r["name"], clone_repo(r["full_name"], dest)

        with ThreadPoolExecutor(max_workers=4) as ex:
            for name, res in ex.map(_do, targets):
                clone_results[name] = res
    for r, d in zip(repos, details, strict=True):
        rec = {
            "name": r["name"],
            "full_name": r["full_name"],
            "description": r.get("description"),
            "visibility": r.get("visibility"),
            "private": r.get("private"),
            "default_branch": r.get("default_branch"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
            "pushed_at": r.get("pushed_at"),
            "size_kb": r.get("size"),
            "language": r.get("language"),
            "topics": r.get("topics", []),
            "stars": r.get("stargazers_count"),
            "forks": r.get("forks_count"),
            "watchers": (d.get("repo") or {}).get("subscribers_count", UNAVAILABLE) if isinstance(d.get("repo"), dict) else UNAVAILABLE,
            "open_issues_count": r.get("open_issues_count"),
            "archived": r.get("archived"),
            "fork": r.get("fork"),
            "license": r.get("license"),
            "homepage": r.get("homepage"),
            "html_url": r.get("html_url"),
            "detail": d,
            "clone": clone_results.get(r["name"], {"ok": False, "reason": "archived" if r.get("archived") else ("clone not requested" if not clone else NOT_TESTED)}),
        }
        out["repos"].append(rec)
    out["http"] = {"requests": client.requests, "unavailable": client.unavailable}
    out["clone_root"] = str(root)
    out["completed_at"] = utcnow()
    client.close()
    return out
