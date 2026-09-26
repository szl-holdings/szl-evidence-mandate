"""Functional testing: installability smoke tests, conformance-corpus replay, Lean counts.

Cloned code is executed only inside a fresh virtual environment, with an environment
stripped of credentials and with HOME/APPDATA/HF_HOME redirected to a throwaway directory.
Commands are argv lists (never a shell). This is process-level isolation, not a sandbox:
see SECURITY.md for the residual risk.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any

from ..models import NOT_TESTED, UNKNOWN, sha256_file, utcnow
from ..safety import contained, isolated_env, rmtree_force, run_argv

PY = shutil.which("py")
PY_ARGV = [PY, "-3.12"] if PY else [sys.executable]


def _venv(env_dir: Path, home: Path) -> tuple[dict[str, Any], Path]:
    r = run_argv([*PY_ARGV, "-m", "venv", str(env_dir)], env=isolated_env(home), timeout=180)
    py = env_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    return r, py


def _bin(env_dir: Path, name: str) -> Path:
    return env_dir / ("Scripts" if sys.platform == "win32" else "bin") / (name + (".exe" if sys.platform == "win32" else ""))


def _py_meta(repo: Path) -> dict[str, Any]:
    meta: dict[str, Any] = {"scripts": [], "packages": [], "extras": []}
    pp = repo / "pyproject.toml"
    if pp.exists():
        try:
            d = tomllib.loads(pp.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
            meta["error"] = f"pyproject unparseable: {e}"
            return meta
        proj = d.get("project") or {}
        meta["name"] = proj.get("name") or ((d.get("tool") or {}).get("poetry") or {}).get("name")
        meta["scripts"] = sorted((proj.get("scripts") or {}).keys()) or sorted((((d.get("tool") or {}).get("poetry") or {}).get("scripts") or {}).keys())
        meta["extras"] = sorted((proj.get("optional-dependencies") or {}).keys())
        meta["build_backend"] = (d.get("build-system") or {}).get("build-backend", UNKNOWN)
    for base in (repo / "src", repo):
        if base.is_dir():
            for c in sorted(base.iterdir()):
                if c.is_dir() and (c / "__init__.py").exists() and c.name not in {"tests", "test", "docs", "examples", "scripts"}:
                    meta["packages"].append(c.name)
    return meta


def _pytest_summary(out: str) -> dict[str, Any]:
    m = re.findall(r"(\d+) (passed|failed|errors?|skipped|xfailed|xpassed)", out)
    counts: dict[str, int] = {}
    for n, k in m:
        counts[k.rstrip("s") if k.startswith("error") else k] = counts.get(k, 0) + int(n)
    return counts


def quickstart_commands(readme: str, scripts: list[str], limit: int = 4) -> list[list[str]]:
    """Extract runnable, local, non-destructive commands from the README quick-start block."""
    m = re.search(r"(?ims)^#+\s*(quick\s*start|getting started|usage|try it)[^\n]*\n(.*?)(?=^#+\s|\Z)", readme)
    if not m:
        return []
    cmds = []
    for block in re.findall(r"```(?:bash|sh|shell|console|powershell)?\s*\n(.*?)```", m.group(2), re.S):
        for line in block.splitlines():
            line = line.strip().lstrip("$").strip()
            if not line or line.startswith("#") or any(t in line for t in ("|", ">", "<", "&&", ";", "`", "$(", "sudo", "curl", "wget", "rm ", "git push", "docker")):
                continue
            try:
                argv = shlex.split(line, comments=True)
            except ValueError:
                continue
            if any(a.startswith("/") or a.startswith("~") for a in argv[1:]):
                continue  # POSIX-rooted paths are not meaningful on the audit host
            if argv and (argv[0] in {"python", "python3"} or argv[0] in scripts):
                cmds.append(argv)
            if len(cmds) >= limit:
                return cmds
    return cmds


def smoke_python(repo: Path, readme: str, workdir: Path, run_tests: bool = True) -> dict[str, Any]:
    home = workdir / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = isolated_env(home)
    steps: list[dict[str, Any]] = []
    meta = _py_meta(repo)
    t0 = time.monotonic()
    r, py = _venv(workdir / "env", home)
    steps.append({"step": "venv", **r})
    if r["exit_code"] != 0:
        return {"kind": "python", "install_ok": False, "steps": steps, "meta": meta}
    target = "."
    for ex in ("dev", "test", "tests"):
        if ex in meta["extras"]:
            target = f".[{ex}]"
            break
    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists():
        inst = run_argv([str(py), "-m", "pip", "install", "--disable-pip-version-check", "-q", target], cwd=repo, env=env, timeout=900)
        steps.append({"step": "install", **inst})
    elif (repo / "requirements.txt").exists():
        inst = run_argv([str(py), "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", "requirements.txt"], cwd=repo, env=env, timeout=900)
        steps.append({"step": "install", **inst})
    else:
        inst = {"exit_code": "NO_MANIFEST"}
    install_ok = inst["exit_code"] == 0
    first_ok_at = None
    imports = []
    installed_as_package = (repo / "pyproject.toml").exists() or (repo / "setup.py").exists()
    for pkg in meta["packages"][:3]:
        # requirements-only repos are not installed as a package: import from the checkout
        ienv = env if installed_as_package else {**env, "PYTHONPATH": str(repo)}
        ir = run_argv([str(py), "-c", f"import {pkg}"], cwd=workdir, env=ienv, timeout=120)
        imports.append({"package": pkg, **ir})
        steps.append({"step": f"import {pkg}", **ir})
        if ir["exit_code"] == 0 and first_ok_at is None:
            first_ok_at = time.monotonic()
    helps = []
    for s in meta["scripts"][:3]:
        exe = _bin(workdir / "env", s)
        hr = run_argv([str(exe), "--help"], cwd=repo, env=env, timeout=120)
        helps.append({"script": s, **hr})
        steps.append({"step": f"{s} --help", **hr})
        if hr["exit_code"] == 0 and first_ok_at is None:
            first_ok_at = time.monotonic()
    qs = []
    for argv in quickstart_commands(readme, meta["scripts"]):
        exe = argv[0]
        if exe in {"python", "python3"}:
            argv = [str(py), *argv[1:]]
        elif exe in meta["scripts"]:
            argv = [str(_bin(workdir / "env", exe)), *argv[1:]]
        if any(Path(a).is_absolute() for a in argv[1:]):
            continue
        qr = run_argv(argv, cwd=repo, env=env, timeout=180)
        qs.append(qr)
        steps.append({"step": "quickstart", **qr})
        if qr["exit_code"] == 0 and first_ok_at is None:
            first_ok_at = time.monotonic()
    tests: dict[str, Any] = {"state": NOT_TESTED, "reason": "no tests directory"}
    if run_tests and install_ok and any((repo / d).is_dir() for d in ("tests", "test")):
        pi = run_argv([str(py), "-m", "pip", "install", "-q", "pytest"], cwd=repo, env=env, timeout=300)
        if pi["exit_code"] != 0:
            tests = {"state": NOT_TESTED, "attribution": "AUDIT_HARNESS", "reason": f"harness could not install pytest (exit {pi['exit_code']})"}
            return {"kind": "python", "meta": meta, "install_ok": install_ok, "tests": tests, "steps": steps + [{"step": "pip install pytest", **pi}], "time_to_first_run_s": NOT_TESTED}
        tr = run_argv([str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", "--maxfail=50"], cwd=repo, env=env, timeout=900, max_output=6000)
        summ = _pytest_summary(tr["output"])
        state = "PASSED" if tr["exit_code"] == 0 else ("FAILED" if summ.get("failed") or summ.get("error") else "ERROR")
        if tr["exit_code"] == 5:
            state = "NO_TESTS_COLLECTED"
        tests = {"state": state, "exit_code": tr["exit_code"], "summary": summ, "duration_s": tr["duration_s"], "output_tail": tr["output"][-1500:]}
        if state == "PASSED" and first_ok_at is None:
            first_ok_at = time.monotonic()
        steps.append({"step": "pytest", **{k: tr[k] for k in ("argv", "exit_code", "duration_s")}, "output": tr["output"][-1500:]})
    return {
        "kind": "python",
        "meta": meta,
        "install_ok": install_ok,
        "imports_ok": all(i["exit_code"] == 0 for i in imports) if imports else NOT_TESTED,
        "help_ok": all(h["exit_code"] == 0 for h in helps) if helps else NOT_TESTED,
        "quickstart_ok": (all(q["exit_code"] == 0 for q in qs) if qs else NOT_TESTED),
        "time_to_first_run_s": round(first_ok_at - t0, 1) if first_ok_at else "NEVER_SUCCEEDED",
        "tests": tests,
        "steps": steps,
    }


def smoke_node(repo: Path, workdir: Path) -> dict[str, Any]:
    npm = shutil.which("npm")
    if not npm:
        return {"kind": "node", "install_ok": NOT_TESTED, "reason": "npm not available on audit host"}
    home = workdir / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = isolated_env(home)
    env["CI"] = "1"
    env["npm_config_cache"] = str(home / "npm-cache")
    t0 = time.monotonic()
    pnpm = shutil.which("pnpm")
    uses_pnpm = (repo / "pnpm-lock.yaml").exists() or (repo / "pnpm-workspace.yaml").exists() or '"catalog:' in (repo / "package.json").read_text(encoding="utf-8", errors="replace")
    if uses_pnpm and not pnpm:
        return {"kind": "node", "install_ok": NOT_TESTED, "reason": "pnpm workspace but pnpm not available on audit host"}
    lock = (repo / "package-lock.json").exists()
    if uses_pnpm:
        inst = run_argv([pnpm, "install", "--ignore-scripts", "--frozen-lockfile"], cwd=repo, env=env, timeout=900)
    else:
        inst = run_argv([npm, "ci" if lock else "install", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=repo, env=env, timeout=900)
    steps = [{"step": "install", **inst}]
    pkg = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    scripts = pkg.get("scripts") or {}
    first_ok = None
    build = None
    if inst["exit_code"] == 0 and "build" in scripts:
        build = run_argv([npm, "run", "build"], cwd=repo, env=env, timeout=900)
        steps.append({"step": "build", **build})
        if build["exit_code"] == 0:
            first_ok = time.monotonic()
    tests: dict[str, Any] = {"state": NOT_TESTED, "reason": "no test script"}
    if inst["exit_code"] == 0 and "test" in scripts and "no test specified" not in scripts["test"]:
        tr = run_argv([npm, "test", "--silent"], cwd=repo, env=env, timeout=900, max_output=6000)
        tests = {"state": "PASSED" if tr["exit_code"] == 0 else "FAILED", "exit_code": tr["exit_code"], "summary": {}, "duration_s": tr["duration_s"], "output_tail": tr["output"][-1500:]}
        steps.append({"step": "npm test", **tr})
        if tr["exit_code"] == 0 and first_ok is None:
            first_ok = time.monotonic()
    return {
        "kind": "node",
        "install_ok": inst["exit_code"] == 0,
        "build_ok": (build["exit_code"] == 0) if build else NOT_TESTED,
        "time_to_first_run_s": round(first_ok - t0, 1) if first_ok else "NEVER_SUCCEEDED",
        "tests": tests,
        "steps": steps,
    }


MIN_FREE_BYTES = int(1.5 * 1024**3)
HEAVY_FREE_BYTES = 12 * 1024**3
HEAVY_DEPS = re.compile(r"(?im)^\s*[\"']?(torch|tensorflow|jax|jaxlib|vllm|xformers|deepspeed|flash[-_]attn|bitsandbytes|triton)\b")


def heavy_dependencies(repo: Path) -> list[str]:
    found: set[str] = set()
    for name in ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"):
        p = repo / name
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="replace")
            found |= {m.group(1).lower() for m in HEAVY_DEPS.finditer(txt)}
    return sorted(found)
ENV_FAILURE = re.compile(r"No space left on device|Errno 28|ENOSPC|MemoryError|Read timed out|ConnectionResetError|Temporary failure in name resolution")


def classify_environment(res: dict[str, Any]) -> dict[str, Any]:
    """A failure caused by the audit host (disk, network, timeout) is NOT_TESTED, never a repo defect."""
    inst = next((s for s in res.get("steps", []) if s.get("step") == "install"), None)
    if inst and (inst.get("exit_code") == "TIMEOUT" or ENV_FAILURE.search(str(inst.get("output", "")))):
        res["install_ok"] = NOT_TESTED
        res["reason"] = "audit-host environment failure during install (" + ("timeout" if inst.get("exit_code") == "TIMEOUT" else ENV_FAILURE.search(str(inst.get("output", ""))).group(0)) + "); not attributed to the repository"
        res["tests"] = {"state": NOT_TESTED, "reason": res["reason"]}
    return res


def smoke_repo(repo: Path, readme: str) -> dict[str, Any]:
    free = shutil.disk_usage(tempfile.gettempdir()).free
    if free < MIN_FREE_BYTES:
        return {"kind": "unknown", "install_ok": NOT_TESTED, "reason": f"insufficient free disk on audit host ({free // 2**20} MB < {MIN_FREE_BYTES // 2**20} MB)", "started_at": utcnow(), "completed_at": utcnow()}
    heavy = heavy_dependencies(repo)
    if heavy and free < HEAVY_FREE_BYTES:
        return {"kind": "python", "install_ok": NOT_TESTED, "reason": f"heavy ML dependencies {heavy} exceed the audit-host disk budget ({free // 2**20} MB free < {HEAVY_FREE_BYTES // 2**20} MB)", "heavy_dependencies": heavy, "started_at": utcnow(), "completed_at": utcnow()}
    work = Path(tempfile.mkdtemp(prefix="szl-smoke-"))
    started = utcnow()
    try:
        if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists() or (repo / "requirements.txt").exists():
            res = smoke_python(repo, readme, work)
        elif (repo / "package.json").exists():
            res = smoke_node(repo, work)
        else:
            res = {"kind": "none", "install_ok": NOT_TESTED, "reason": "no Python or Node entry point"}
    finally:
        rmtree_force(work)
        # remove build artefacts / node_modules the run created inside the clone
        run_argv([shutil.which("git") or "git", "-C", str(repo), "clean", "-xdfq"], timeout=300)
    res = classify_environment(res)
    res["harness_revision"] = "fix2"  # byte-exact clone (core.autocrlf=false), absolute pip cache
    res["started_at"] = started
    res["completed_at"] = utcnow()
    return res


# ------------------------------------------------------------------ Lean counts (independent re-implementation)
DECL_RE = re.compile(r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*(theorem|lemma|def|abbrev|instance|structure|inductive|class)\b")
AXIOM_RE = re.compile(r"^(?:private\s+)?axiom\s+([A-Za-z_][A-Za-z0-9_'.]*)")
SORRY_RE = re.compile(r"\bsorry\b")


def lean_counts(root: Path) -> dict[str, Any]:
    decls = axioms_raw = sorries_raw = sorries_live = 0
    names: set[str] = set()
    files = 0
    for f in sorted(root.rglob("*.lean")):
        if any(p in {".lake", "lake-packages", "build"} for p in f.parts):
            continue
        files += 1
        depth = 0  # Lean block comments nest
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            sorries_raw += len(SORRY_RE.findall(line))
            # strip block comments (nesting-aware) and line comments; count only code
            code, i = [], 0
            while i < len(line):
                if line.startswith("/-", i):
                    depth += 1
                    i += 2
                elif depth and line.startswith("-/", i):
                    depth -= 1
                    i += 2
                elif not depth and line.startswith("--", i):
                    break
                else:
                    if not depth:
                        code.append(line[i])
                    i += 1
            s = "".join(code).strip()
            if DECL_RE.match(s):
                decls += 1
            m = AXIOM_RE.match(s)
            if m:
                axioms_raw += 1
                names.add(m.group(1))
            sorries_live += len(SORRY_RE.findall(s))
    return {"lean_files": files, "declarations": decls, "axioms_raw": axioms_raw, "axioms_unique": len(names), "axiom_names": sorted(names), "sorries_raw": sorries_raw, "sorries_live": sorries_live, "method": "szl_evidence.audit.functional.lean_counts (comment-aware, nesting block comments; line-initial keyword after @[attr]/modifiers)"}


# ------------------------------------------------------------------ conformance corpus replay
def run_paired_verifier(fixtures_dir: Path, bench_rows: list[dict[str, Any]], verifier_repo: Path, label: str) -> dict[str, Any]:
    """Run ``verify.py`` from ``verifier_repo`` against each fixture and compare to the declared outcome."""
    work = Path(tempfile.mkdtemp(prefix="szl-conf-"))
    home = work / "home"
    home.mkdir()
    env = isolated_env(home)
    try:
        r, py = _venv(work / "env", home)
        setup = [{"step": "venv", "exit_code": r["exit_code"]}]
        req = [p for p in ("requirements.txt", "requirements-verify.txt") if (verifier_repo / p).exists()]
        for p in req:
            ir = run_argv([str(py), "-m", "pip", "install", "-q", "-r", p], cwd=verifier_repo, env=env, timeout=900)
            setup.append({"step": f"pip install -r {p}", "exit_code": ir["exit_code"], "output": ir["output"][-600:]})
        if not req and (verifier_repo / "pyproject.toml").exists():
            ir = run_argv([str(py), "-m", "pip", "install", "-q", "."], cwd=verifier_repo, env=env, timeout=900)
            setup.append({"step": "pip install .", "exit_code": ir["exit_code"], "output": ir["output"][-600:]})
        rows = []
        for b in bench_rows:
            f = contained(fixtures_dir, b["file"])
            if not f.exists():
                rows.append({"file": b["file"], "declared": b.get("expected_result"), "observed": "FIXTURE_MISSING", "match": False})
                continue
            vr = run_argv([str(py), "verify.py", str(f)], cwd=verifier_repo, env=env, timeout=180, max_output=3000)
            m = re.search(r"OVERALL:\s*(PASS|FAIL)", vr["output"])
            observed = m.group(1) if m else ("ERROR" if vr["exit_code"] not in (0, 1) else ("PASS" if vr["exit_code"] == 0 else "FAIL"))
            exit_consistent = (observed == "PASS" and vr["exit_code"] == 0) or (observed == "FAIL" and vr["exit_code"] != 0)
            rows.append(
                {
                    "file": b["file"],
                    "fixture_sha256": sha256_file(f),
                    "declared": b.get("expected_result"),
                    "observed": observed,
                    "exit_code": vr["exit_code"],
                    "exit_consistent_with_verdict": exit_consistent,
                    "match": observed == b.get("expected_result"),
                    "output_tail": vr["output"][-700:],
                }
            )
        return {
            "verifier": label,
            "setup": setup,
            "fixtures": len(rows),
            "matched": sum(1 for x in rows if x["match"]),
            "mismatched": [x["file"] for x in rows if not x["match"]],
            "results": rows,
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)
