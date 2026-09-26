"""Phase 4: systemic gaps, band-aids, frontier plan, prioritised remediation.

A recommendation that patches one instance, or relies on a human remembering, without
closing the class of defect is INSUFFICIENT and is replaced by a structural fix.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .common import SEVERITY_ORDER

EFFORT_ORDER = {"S": 0, "M": 1, "L": 2, "UNKNOWN": 3}


@dataclass
class Recommendation:
    text: str
    scope: str  # "instance" | "class"
    enforcement: str  # "manual" | "automated"
    verdict: str = ""
    replacement: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_recommendation(rec: Recommendation, structural_fix: str) -> Recommendation:
    if rec.scope == "class" and rec.enforcement == "automated":
        rec.verdict = "SUFFICIENT"
    else:
        rec.verdict = "INSUFFICIENT"
        rec.replacement = structural_fix
    return rec


def detect_bandaids(ev: dict[str, Any]) -> list[dict[str, Any]]:
    """Each rule fires only when its evidence is present in the collected data."""
    out: list[dict[str, Any]] = []

    def add(name: str, evidence: str, symptom_fix: str, root: str, fix: str) -> None:
        rec = evaluate_recommendation(Recommendation(symptom_fix, "instance", "manual"), fix)
        out.append({"band_aid": name, "evidence": evidence, "root_cause": root, "symptom_only_recommendation": rec.to_dict(), "structural_fix": fix})

    stale_inv = [c for c in ev.get("claims", []) if c["claim_type"] == "inventory_count" and c["verdict"] == "STALE"]
    if stale_inv:
        add(
            "Hand-published dated inventory counts",
            f"{len(stale_inv)} dated inventory claims have drifted, e.g. {stale_inv[0]['location']}: {stale_inv[0]['evidence']}",
            "Edit the README numbers to today's values",
            "Counts are embedded as static prose, regenerated only when someone runs the snapshot workflow",
            "Render counts from a scheduled live-API inventory job that commits the JSON and fails CI when any README/card count disagrees",
        )
    stale_lean = [c for c in ev.get("claims", []) if c["claim_type"] == "lean_count" and c["verdict"] == "STALE"]
    if stale_lean:
        add(
            "Pinned Lean counts copied into prose",
            f"{len(stale_lean)} Lean-count claims match the pinned revision but not HEAD, e.g. {stale_lean[0]['location']}: {stale_lean[0]['evidence']}",
            "Update 749/14/163 to the new numbers",
            "Numbers are measured once with a regex counter and copied into many cards and READMEs",
            "Count via the Lean environment (enumerate constants, `#print axioms`, sorry detection by elaboration) in lutar-lean CI; publish one JSON; all surfaces template from it with a drift check",
        )
    for c in ev.get("conformance", {}).get("corpora", []):
        runs = c.get("runs", [])
        pinned_ok = any("pinned" in r.get("verifier", "") and not r.get("mismatched") for r in runs)
        head_bad = any("HEAD" in r.get("verifier", "") and r.get("mismatched") for r in runs)
        if pinned_ok and head_bad:
            add(
                "Conformance corpus pinned to an old verifier commit",
                f"{c['dataset']}: all fixtures match at pinned {c['card_pinned_commit'][:12]}, but current default branch mismatches {[r['mismatched'] for r in runs if r.get('mismatched')]}",
                "Update the pin in the card to the newest commit",
                "The verifier evolves without running the corpus; pinning hides the break instead of detecting it",
                "Required CI job in the verifier repo that replays every corpus fixture; corpus expected outcomes versioned per verifier release with an explicit changelog of semantic changes",
            )
    dup = ev.get("verifier_implementations", [])
    if len(dup) > 2:
        add(
            "Per-repo receipt verifiers",
            f"{len(dup)} separate verifier implementations: {dup[:10]}",
            "Fix the bug in whichever verifier failed",
            "No shared receipt library; each component re-implements parsing and checks",
            "One canonical receipt schema + one shared verifier library consumed by all components; a conformance suite in that library gates every consumer's CI",
        )
    grep_gates = ev.get("copied_secret_grep_workflows", [])
    if len(grep_gates) > 1:
        add(
            "Copy-pasted grep secret gates",
            f"identical grep-based secret gate in {grep_gates}",
            "Add another token pattern to the grep",
            "Secret detection implemented per repo as a workflow step",
            "Org-level GitHub secret scanning + push protection and a required reusable workflow (gitleaks) from .github",
        )
    if ev.get("skipped_sig_pass"):
        add(
            "Skipped signature check reported as PASS",
            ev["skipped_sig_pass"],
            "Always pass --verify-key in the documented command",
            "Verifier collapses NOT_TESTED into PASS",
            "Verifier emits NOT_TESTED for skipped checks and an ABSTAIN overall; conformance fixtures include a no-key case expecting ABSTAIN",
        )
    return out


def systemic(ev: dict[str, Any]) -> dict[str, Any]:
    claims = ev.get("claims", [])
    rec = ev.get("reconcile", {})
    return {
        "contradictions": ev.get("consistency", []) + [c for c in claims if c["verdict"] == "CONTRADICTED"][:40],
        "orphans": {"hf_without_living_source": rec.get("orphaned_hf", [])[:60], "repos_claiming_missing_targets": rec.get("orphaned_repo_claims", [])},
        "duplicates": ev.get("verifier_implementations", []),
        "unenforced_doctrine": [c for c in claims if c["claim_type"] in ("doctrine_version", "locked_marker", "trust_ceiling")][:30],
        "unverified_claims": [c for c in claims if c["verdict"] == "UNVERIFIABLE" and c["claim_type"] in ("formula_count", "topology_label", "trust_ceiling", "locked_marker")][:30],
        "single_points_of_failure": ev.get("spof", []),
        "schema_skew": rec.get("schema_version_skew", []),
        "evidence_boundary_violations": ev.get("boundary_violations", []),
    }


AUTOMATED = ("ci", "required check", "required status", "workflow", "gate", "ruleset", "org-level", "template", "lint", "schedule", "scheduled", "automat", "pre-publish", "reusable", "generated", "templat")
INSTANCE = ("update ", "edit ", "rename ", "fix the ", "replace the ", "re-run", "manual", "inspect ")


def classify_fix(text: str) -> Recommendation:
    """Scope/enforcement of a proposed fix, inferred from its wording (documented heuristic)."""
    t = text.lower()
    automated = any(k in t for k in AUTOMATED)
    instance_only = any(k in t for k in INSTANCE) and not automated
    return Recommendation(text, "instance" if instance_only else "class", "automated" if automated else "manual")


def evaluate_fixes(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mark each finding's structural fix SUFFICIENT or INSUFFICIENT; INSUFFICIENT fixes get the
    category's class-closing replacement."""
    replacement = "Close the class with an automated gate (CI/required check, org ruleset, publish gate or scheduled job) that fails when this defect recurs anywhere in the estate"
    for f in findings:
        rec = evaluate_recommendation(classify_fix(f.get("structural_fix") or ""), replacement)
        f["fix_verdict"] = rec.verdict
        if rec.verdict == "INSUFFICIENT":
            f["structural_fix"] = f"{f.get('structural_fix') or 'none given'} → INSUFFICIENT alone; add: {replacement}"
    return findings


def remediation_table(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = sorted(findings, key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), EFFORT_ORDER.get(f.get("effort") or "UNKNOWN", 3), f["surface"], f["artifact"]))
    return [r for r in rows if r["severity"] != "INFO"]
