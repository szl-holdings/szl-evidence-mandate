"""Engine verification stage: fixtures, mutation testing, dependency demos, determinism."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .dependencies import DependencyGraph
from .fixturegen import VARIANTS, build_fixture
from .models import sha256_file, utcnow  # noqa: F401
from .mutations import run_mutations
from .verifier import verify


def evidence_tokens(r: dict[str, Any]) -> set[str]:
    """The only places required evidence may be found: non-PASS check names, failure taxonomy,
    reason codes, the PASS evidence block, and dependency validity states."""
    toks = {i["check"] for i in r.get("invocations", []) if i["result"]["status"] != "PASS"}
    toks |= set(r.get("failures", [])) | set(r.get("reason_codes", [])) | {r.get("primary_reason", "")}
    if r.get("pass_evidence"):
        toks.add("pass_evidence")
    dep = r.get("dependency_impact")
    if isinstance(dep, dict):
        toks |= set((dep.get("states") or {}).values())
    return toks


def run_fixtures(fixtures_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for name in VARIANTS:
        d = fixtures_dir / name
        exp = yaml.safe_load((d / "expected.yaml").read_text(encoding="utf-8"))
        r = verify(d)
        toks = evidence_tokens(r)
        ev_ok = all(e in toks for e in exp["required_evidence"])
        rows.append(
            {
                "fixture": name,
                "expected_status": exp["expected_status"],
                "observed_status": r["status"],
                "expected_exit": exp["expected_exit_code"],
                "observed_exit": r["exit_code"],
                "required_evidence_present": ev_ok,
                "match": r["status"] == exp["expected_status"] and r["exit_code"] == exp["expected_exit_code"] and ev_ok,
                "primary_reason": r["primary_reason"],
                "failures": r.get("failures", []),
                "non_pass_checks": [i["check"] for i in r["invocations"] if i["result"]["status"] != "PASS"],
                "claim_not_established": exp["claim_not_established"],
                "receipt_sha256": r["receipt_sha256"],
                "signature_state": r["signature_state"],
            }
        )
    return rows


def dependency_demo(fixtures_dir: Path) -> dict[str, Any]:
    """Impact of an upstream design change, then both revalidation outcomes."""
    root = fixtures_dir / "valid"
    dag = yaml.safe_load((root / "inputs/dag.yaml").read_text(encoding="utf-8"))
    impact = DependencyGraph.load(copy.deepcopy(dag), root).impact("design")
    changed = copy.deepcopy(dag)
    for n in changed["nodes"]:
        if n["id"] == "design":
            n["version"] = "3"
    g = DependencyGraph.load(copy.deepcopy(changed), root)
    evaluation = g.evaluate()
    prior = "sha256-of-admitted-evidence-output"
    g.nodes["admitted-evidence"].output_sha256 = prior
    unchanged = g.revalidate("admitted-evidence", prior)
    g2 = DependencyGraph.load(copy.deepcopy(changed), root)
    g2.evaluate()
    g2.nodes["admitted-evidence"].output_sha256 = prior
    changed_res = g2.revalidate("admitted-evidence", "sha256-of-a-different-output")
    return {"impact_of_design_change": impact, "evaluation_after_change": evaluation, "revalidate_unchanged": unchanged, "revalidate_changed": changed_res}


def determinism_check(fixture: Path) -> dict[str, Any]:
    """Run the CLI under different hash seeds with a fixed clock; receipts must be byte-identical."""
    outs = []
    for seed in ("0", "1", "12345"):
        tmp = Path(tempfile.mkdtemp(prefix="szl-det-")) / "r.json"
        env = {**os.environ, "PYTHONHASHSEED": seed, "SOURCE_DATE_EPOCH": "1767225600"}
        p = subprocess.run([sys.executable, "-m", "szl_evidence.cli", "engine", "verify", str(fixture), "--receipt", str(tmp), "--quiet"], env=env, capture_output=True, timeout=300, check=False)  # noqa: S603
        outs.append({"seed": seed, "exit": p.returncode, "receipt_sha256_of_file": sha256_file(tmp) if tmp.exists() else "MISSING"})
    identical = len({o["receipt_sha256_of_file"] for o in outs}) == 1 and "MISSING" not in {o["receipt_sha256_of_file"] for o in outs}
    return {"runs": outs, "byte_identical": identical}


def run_engine_stage(fixtures_dir: Path, rebuild: bool = False) -> dict[str, Any]:
    started = utcnow()
    if rebuild or not (fixtures_dir / "valid" / "manifest.yaml").exists():
        for name in VARIANTS:
            build_fixture(fixtures_dir / name, name)
    fx = run_fixtures(fixtures_dir)
    muts = run_mutations(fixtures_dir / "valid")
    dep = dependency_demo(fixtures_dir)
    det = determinism_check(fixtures_dir / "valid")
    return {"started_at": started, "completed_at": utcnow(), "fixtures": fx, "mutations": muts, "dependencies": dep, "determinism": det}
