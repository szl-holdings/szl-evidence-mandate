"""Attribute recorded test/install outcomes to the repository, the audit harness, or the host.

A failure is charged to the repository only when the recorded output rules out the known
harness/host causes. Everything else is NOT_TESTED or UNRESOLVED with the reason stated,
because "the verifier's own environment broke" is never evidence of a defect.

Known causes observed on this audit host (Windows 11, Python 3.12):
- git core.autocrlf=true rewrote line endings in clones used before harness 0.1.0-fix2, so
  byte/hash/manifest comparisons are not trustworthy for those runs;
- partial clones (--filter=blob:limit=2m) omit blobs > 2 MB;
- creating symlinks requires a privilege (WinError 1314) the audit user lacks;
- npm scripts relying on POSIX shell globbing do not expand under cmd.exe;
- the harness's own pytest install can fail when the host disk is full.
"""

from __future__ import annotations

import re
from typing import Any

from ..models import NOT_TESTED

HARNESS = [
    (re.compile(r"No module named pytest"), "harness: pytest could not be installed in the audit venv"),
    (re.compile(r"No space left on device|Errno 28|ENOSPC"), "host: disk full during the run"),
]
HOST = [
    (re.compile(r"WinError 1314|A required privilege is not held by the client"), "host: Windows symlink privilege (WinError 1314)"),
    (re.compile(r"Could not find '[^']*\*|Could not find '[^']+\.test\.[jt]s"), "host: POSIX glob in npm test script not expanded by cmd.exe"),
]
UNRESOLVED_CRLF = re.compile(r"(?i)(sha256|digest|hash|checksum|bytes|manifest|mirror_cards|assets_validate|byte-for-byte|matches_successor)")
UNRESOLVED_BLOB = re.compile(r"(?i)(is_file\(\)|FileNotFoundError|No such file|LFS|git-lfs)")
REPO_DEFECT = [
    (re.compile(r"starlette\.testclient module requires the httpx|The starlette\.testclient module"), "repo: test dependency httpx not declared (starlette TestClient)"),
    (re.compile(r"No module named '(torch|tensorflow|jax)'"), "repo: tests import {0} but it is not declared in the installed dependency set"),
    (re.compile(r"No module named '([A-Za-z0-9_]+)'"), "repo: tests import undeclared module '{0}'"),
]


def classify(res: dict[str, Any], crlf_risk: bool, partial_clone: bool) -> dict[str, Any]:
    """Return a copy of a smoke result whose test outcome carries an attribution."""
    out = dict(res)
    t = dict(out.get("tests") or {})
    if t.get("state") not in ("FAILED", "ERROR"):
        out["tests"] = t
        return out
    text = str(t.get("output_tail", "")) + "".join(str(s.get("output", "")) for s in out.get("steps", []) if s.get("step") in ("pytest", "npm test"))
    t["raw_state"] = t["state"]
    for rx, why in HARNESS:
        if rx.search(text):
            t.update(state=NOT_TESTED, attribution="AUDIT_HARNESS", reason=why)
            out["tests"] = t
            return out
    for rx, why in REPO_DEFECT:
        m = rx.search(text)
        if m:
            t.update(state=t["raw_state"], attribution="REPO_DEFECT", reason=why.format(*(m.groups() or ("",))))
            out["tests"] = t
            return out
    for rx, why in HOST:
        if rx.search(text):
            t.update(state="HOST_LIMITED", attribution="HOST_PLATFORM", reason=why + "; failing tests not attributed to the repository")
            out["tests"] = t
            return out
    if crlf_risk:
        # Interim harness (autocrlf clone, partial blobs, stripped env): without a recognised
        # repository cause, a failure there cannot be charged to the repository.
        detail = "byte/hash comparison on a core.autocrlf=true clone" if UNRESOLVED_CRLF.search(text) else "no repository cause recognised"
        t.update(state="UNRESOLVED", attribution="POSSIBLE_HARNESS", reason=f"failure recorded under the interim harness ({detail}); re-run under harness fix2 required")
    elif partial_clone and UNRESOLVED_BLOB.search(text):
        t.update(state="UNRESOLVED", attribution="POSSIBLE_HARNESS", reason="missing-file assertion on a partial clone (blobs > 2 MB omitted); re-run on a full clone required")
    else:
        t.update(attribution="REPO_DEFECT_UNCONFIRMED", reason="no harness/host cause recognised in recorded output; confirm on Linux CI")
    out["tests"] = t
    return out


def ttfr_from_passing_tests(res: dict[str, Any]) -> dict[str, Any]:
    """A passing test suite is a successful run. For recorded results that only counted
    import/--help/quickstart, reconstruct time-to-first-run from recorded step durations."""
    if res.get("time_to_first_run_s") == "NEVER_SUCCEEDED" and (res.get("tests") or {}).get("state") == "PASSED":
        total = 0.0
        for s in res.get("steps", []):
            if isinstance(s.get("duration_s"), (int, float)):
                total += s["duration_s"]
            if s.get("step") in ("pytest", "npm test"):
                break
        res = {**res, "time_to_first_run_s": round(total, 1), "time_to_first_run_basis": "sum of recorded step durations through the passing test suite"}
    return res


def normalise_probes(res: dict[str, Any]) -> dict[str, Any]:
    """Probe outcomes that the harness itself could not have produced fairly become NOT_TESTED."""
    res = dict(res)
    pre = res.get("harness_revision", "pre-fix2") == "pre-fix2"
    notes = []
    inst = next((s for s in res.get("steps", []) if s.get("step") == "install"), {})
    argv = " ".join(str(a) for a in inst.get("argv", []))
    if res.get("install_ok") is False and "EUNSUPPORTEDPROTOCOL" in str(inst.get("output", "")) and "catalog:" in str(inst.get("output", "")):
        res["install_ok"] = NOT_TESTED
        res["reason"] = "pnpm workspace ('catalog:' specifiers) installed with npm by the harness; not attributable to the repository"
        res["tests"] = {"state": NOT_TESTED, "reason": res["reason"]}
    if pre and res.get("quickstart_ok") is False:
        res["quickstart_ok"] = NOT_TESTED
        notes.append("quickstart: interim harness passed README comments/POSIX paths as argv")
    if res.get("imports_ok") is False and "-r" in argv and "requirements" in argv:
        res["imports_ok"] = NOT_TESTED
        notes.append("import: project not installed (requirements-only install); import from site-packages not meaningful")
    probes = [res.get("imports_ok"), res.get("help_ok"), res.get("quickstart_ok")]
    passed_tests = (res.get("tests") or {}).get("state") == "PASSED"
    if res.get("time_to_first_run_s") == "NEVER_SUCCEEDED" and not passed_tests and all(p in (NOT_TESTED, None) for p in probes):
        res["time_to_first_run_s"] = NOT_TESTED
        notes.append("time-to-first-run: no run probe was executed")
    if notes:
        res["normalisation_notes"] = notes
    return res


def classify_all(smoke: dict[str, Any]) -> dict[str, Any]:
    fixed = {}
    for name, res in smoke.items():
        if not isinstance(res, dict):
            fixed[name] = res
            continue
        res = ttfr_from_passing_tests(res)
        res = normalise_probes(res)
        harness_rev = res.get("harness_revision", "pre-fix2")
        fixed[name] = classify(res, crlf_risk=harness_rev == "pre-fix2", partial_clone=harness_rev == "pre-fix2")
    return fixed
