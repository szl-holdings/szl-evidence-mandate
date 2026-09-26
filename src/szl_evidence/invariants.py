"""Receipt/ledger invariants (1.3, 1.4, 1.5). Used both by the engine on its own output
(verifier failure -> ERROR) and by ``verify_receipt`` on receipts received from elsewhere.

The verifier's answer is not trusted to certify itself: these invariants recompute every
summary figure from the invocation ledger and reject any disagreement.
"""

from __future__ import annotations

from typing import Any

from .ledger import verify_chain
from .receipts import receipt_hash

TERMINAL = {"PASS", "FAIL", "ABSTAIN", "ERROR"}
INVARIANTS = [
    "receipt_hash_binds_content",
    "ledger_chain_intact",
    "ledger_head_and_count_bound",
    "every_verdict_has_invocation",
    "verdicts_unique_per_invocation",
    "every_invocation_has_result",
    "verdict_matches_invocation",
    "every_required_check_has_terminal_state",
    "checked_claims_le_verifier_invocations",
    "invocation_input_hashes_match_observed",
    "status_derived_from_ledger",
    "pass_requires_nonempty_evidence",
    "pass_requires_complete_required_inputs",
    "pass_requires_complete_required_checks",
    "pass_block_derived_from_ledger",
    "accounting_closes",
]


def aggregate(statuses: list[str]) -> str:
    if not statuses:
        return "ABSTAIN"
    for s in ("ERROR", "FAIL", "ABSTAIN"):
        if s in statuses:
            return s
    return "PASS"


def pass_block(r: dict[str, Any]) -> dict[str, Any]:
    """The PASS evidence contract, computed from the ledger and accounting only."""
    invs = r.get("invocations", [])
    acct = r.get("accounting", {})
    st = [i["result"]["status"] for i in invs if "result" in i]
    return {
        "status": "PASS",
        "run_id": r.get("run_id"),
        "manifest_version": (r.get("manifest") or {}).get("version"),
        "expected_inputs": acct.get("expected"),
        "inputs_discovered": acct.get("discovered"),
        "inputs_opened": acct.get("opened"),
        "rows_examined": acct.get("rows_examined"),
        "checks_expected": len(r.get("required_checks", [])),
        "checks_executed": len(invs),
        "checks_passed": st.count("PASS"),
        "checks_failed": st.count("FAIL"),
        "checks_abstained": st.count("ABSTAIN"),
        "evidence_manifest_sha256": r.get("evidence_manifest_sha256"),
        "receipt_sha256": "<see receipt_sha256>",
        "started_at": r.get("started_at"),
        "completed_at": r.get("completed_at"),
    }


def check_invariants(r: dict[str, Any], check_hash: bool = True) -> list[dict[str, str]]:
    v: list[dict[str, str]] = []

    def bad(name: str, detail: str) -> None:
        v.append({"invariant": name, "detail": detail})

    invs = r.get("invocations", []) or []
    verdicts = r.get("verdicts", []) or []
    if check_hash and r.get("receipt_sha256") != receipt_hash(r):
        bad("receipt_hash_binds_content", "receipt_sha256 does not match canonical content")
    for p in verify_chain(invs):
        bad("ledger_chain_intact", p)
    if r.get("invocation_count") != len(invs):
        bad("ledger_head_and_count_bound", f"invocation_count={r.get('invocation_count')} but {len(invs)} present")
    if invs and r.get("ledger_head_sha256") != invs[-1].get("entry_sha256"):
        bad("ledger_head_and_count_bound", "ledger head does not match last entry")
    inv_ids = [i.get("invocation_id") for i in invs]
    by_id = {i.get("invocation_id"): i for i in invs}
    seen = set()
    for vd in verdicts:
        iid = vd.get("invocation_id")
        if iid not in by_id:
            bad("every_verdict_has_invocation", f"verdict {vd.get('verdict_id')} references unknown invocation")
            continue
        if iid in seen:
            bad("verdicts_unique_per_invocation", f"invocation {iid} has more than one verdict")
        seen.add(iid)
        if vd.get("verdict") != by_id[iid].get("result", {}).get("status"):
            bad("verdict_matches_invocation", f"verdict {vd.get('verdict_id')} disagrees with invocation result")
    for iid in inv_ids:
        if iid not in seen:
            bad("verdicts_unique_per_invocation", f"invocation {iid} has no verdict")
    for i in invs:
        res = i.get("result") or {}
        if res.get("status") not in TERMINAL:
            bad("every_invocation_has_result", f"invocation {i.get('invocation_id')} lacks a terminal result")
    keys = {}
    for i in invs:
        keys.setdefault(i.get("check"), []).append(i)
    for req in r.get("required_checks", []):
        hit = keys.get(req, [])
        if not hit or not all((h.get("result") or {}).get("status") in TERMINAL for h in hit):
            bad("every_required_check_has_terminal_state", f"required check {req!r} has no terminal invocation")
    claims_checked = (r.get("accounting") or {}).get("claims_checked", 0)
    claim_invs = sum(1 for i in invs if str(i.get("check", "")).startswith("claim_value:"))
    if claims_checked > claim_invs:
        bad("checked_claims_le_verifier_invocations", f"claims_checked={claims_checked} > claim invocations={claim_invs}")
    observed = r.get("observed_inputs", {}) or {}
    for i in invs:
        for k, h in (i.get("input_hashes") or {}).items():
            if k in observed and observed[k].get("sha256") != h:
                bad("invocation_input_hashes_match_observed", f"invocation {i.get('seq')} input {k} hash differs from observed")
    statuses = [(i.get("result") or {}).get("status") for i in invs]
    derived = aggregate(statuses)
    if (r.get("accounting") or {}).get("rows_examined", 0) == 0 and derived == "PASS":
        derived = "ABSTAIN"
    status = r.get("status")
    if r.get("invariant_violations"):
        if status != "ERROR":
            bad("status_derived_from_ledger", "invariant violations present but status is not ERROR")
    elif status != derived:
        bad("status_derived_from_ledger", f"status {status} but ledger derives {derived}")
    if status == "PASS":
        empty_ev = [i.get("check") for i in invs if not (i.get("result") or {}).get("evidence")]
        if not invs or empty_ev or not r.get("evidence_manifest"):
            bad("pass_requires_nonempty_evidence", f"PASS with empty evidence: {empty_ev or 'no invocations/manifest'}")
        acct = r.get("accounting") or {}
        if acct.get("missing", 1) or acct.get("failed", 1) or acct.get("deferred", 1):
            bad("pass_requires_complete_required_inputs", "PASS with missing/failed/deferred inputs")
        if any(s != "PASS" for s in statuses) or len(invs) < len(r.get("required_checks", [])):
            bad("pass_requires_complete_required_checks", "PASS without every required check passing")
        if r.get("pass_evidence") != pass_block(r):
            bad("pass_block_derived_from_ledger", "PASS evidence block was not derived from the ledger")
    elif r.get("pass_evidence") is not None:
        bad("pass_block_derived_from_ledger", "non-PASS receipt carries a PASS evidence block")
    closure = ((r.get("accounting") or {}).get("input_closure") or {})
    if closure and not closure.get("closes") and (r.get("accounting") or {}).get("denominator_state") == "OBSERVED":
        bad("accounting_closes", "input accounting does not close but denominator_state=OBSERVED")
    return v
