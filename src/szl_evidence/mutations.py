"""Verifier mutation testing (1.9).

Each mutation perturbs either the inputs (the engine must stop reporting PASS), the
emitted receipt (independent receipt verification must reject it), or the engine itself
(a skipped checker must be caught by ledger invariants).

An undetected mutation that should have been detected is a BLIND_SPOT. A detected
mutation that is semantically neutral is a FALSE_POSITIVE. Neither is ever suppressed.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .fixturegen import _edit_csv, _edit_yaml, build_valid
from .ledger import GENESIS
from .models import sha256_json
from .receipts import receipt_hash
from .verifier import verify, verify_receipt


@dataclass
class Mutation:
    id: str
    name: str
    target: str  # input | receipt | engine
    expected_detection: bool
    expected_detectors: list[str]
    apply: Callable[..., Any]
    note: str = ""


def _reseal(r: dict[str, Any]) -> dict[str, Any]:
    r["receipt_sha256"] = receipt_hash(r)
    return r


def _rechain(r: dict[str, Any]) -> dict[str, Any]:
    """What a capable forger does: recompute the whole chain, head, count and receipt hash."""
    prev = GENESIS
    for i, inv in enumerate(r["invocations"]):
        inv["seq"] = i
        inv["prev_sha256"] = prev
        inv["entry_sha256"] = sha256_json({k: v for k, v in inv.items() if k != "entry_sha256"})
        prev = inv["entry_sha256"]
    r["invocation_count"] = len(r["invocations"])
    r["ledger_head_sha256"] = prev
    return _reseal(r)


# ---------------------------------------------------------------- input mutations
def m_remove_all_inputs(root: Path) -> None:
    for f in (root / "inputs").iterdir():
        f.unlink()


def m_delete_table(root: Path) -> None:
    (root / "inputs/citations.csv").unlink()


def m_delete_row(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: [r for r in rows if r["record_id"] != "R2"])


def m_duplicate_row(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: rows + [dict(rows[0])])


def m_remove_reviewer(root: Path) -> None:
    _edit_csv(root, "inputs/reviews.csv", lambda rows: [r for r in rows if r["reviewer"] != "rev-beta"])


def m_change_author(root: Path) -> None:
    _edit_csv(root, "inputs/citations.csv", lambda rows: [{**r, "authors": "Huamani"} if r["citation_id"] == "K2" else r for r in rows])


def m_replace_doi(root: Path) -> None:
    _edit_csv(root, "inputs/citations.csv", lambda rows: [{**r, "doi": "10.5555/szl.fixture.0002"} if r["citation_id"] == "K1" else r for r in rows])


def m_change_number(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: [{**r, "n": "1908"} if r["record_id"] == "R3" else r for r in rows])


def m_add_thousands_sep(root: Path) -> None:
    _edit_yaml(root, "inputs/claims.yaml", lambda c: {"claims": [{**x, "value": "12,480"} if x["id"] == "C1" else x for x in c["claims"]]})


def m_add_thousands_sep_and_change(root: Path) -> None:
    _edit_yaml(root, "inputs/claims.yaml", lambda c: {"claims": [{**x, "value": "12,481"} if x["id"] == "C1" else x for x in c["claims"]]})


def m_shift_timestamp(root: Path) -> None:
    _edit_csv(root, "inputs/sources.csv", lambda rows: [{**r, "retrieved_at": r["retrieved_at"].replace("Z", "+01:00")} if r["source_id"] == "S1" else r for r in rows])


def m_inject_pass_summary(root: Path) -> None:
    _edit_yaml(root, "inputs/attestation.yaml", lambda a: {**a, "claimed_status": "PASS", "checks_claimed": []})


def m_bump_design(root: Path) -> None:
    _edit_yaml(root, "inputs/dag.yaml", lambda d: {"nodes": [{**n, "version": "3"} if n["id"] == "design" else n for n in d["nodes"]]})


def m_replace_stored_output(root: Path) -> None:
    p = root / "outputs/summary.csv"
    p.write_text(p.read_text(encoding="utf-8").replace("mean_effect,0.42", "mean_effect,0.43"), encoding="utf-8", newline="")


def m_substitute_reviewer(root: Path) -> None:
    _edit_csv(root, "inputs/reviews.csv", lambda rows: [{**r, "reviewer": "rev-unauthorized"} if r["reviewer"] == "rev-beta" else r for r in rows])


def m_forge_producer_invocation(root: Path) -> None:
    _edit_yaml(root, "inputs/attestation.yaml", lambda a: {**a, "checks_claimed": a["checks_claimed"] + ["human_review"]})
    p = root / "inputs/producer_invocations.jsonl"
    p.write_text(p.read_text(encoding="utf-8") + json.dumps({"invocation_id": "p-forged", "check": "human_review", "result": "PASS"}, sort_keys=True) + "\n", encoding="utf-8", newline="")


def m_duplicate_record_modified(root: Path) -> None:
    """Duplicate an entity under a new key with a trivially altered title (near-duplicate)."""
    _edit_csv(root, "inputs/records.csv", lambda rows: rows + [{**rows[0], "record_id": "R1b", "title": rows[0]["title"] + " "}])


# ---------------------------------------------------------------- receipt mutations
def r_duplicate_verdict(r: dict[str, Any]) -> dict[str, Any]:
    r["verdicts"].append(copy.deepcopy(r["verdicts"][0]))
    return _reseal(r)


def r_change_hash(r: dict[str, Any]) -> dict[str, Any]:
    k = sorted(r["observed_inputs"])[0]
    r["observed_inputs"][k]["sha256"] = "f" * 64
    return _reseal(r)


def r_remove_invocation(r: dict[str, Any]) -> dict[str, Any]:
    del r["invocations"][3]
    return _reseal(r)


def r_truncate_ledger(r: dict[str, Any]) -> dict[str, Any]:
    cut = len(r["invocations"]) - 3
    kept = {i["invocation_id"] for i in r["invocations"][:cut]}
    r["invocations"] = r["invocations"][:cut]
    r["verdicts"] = [v for v in r["verdicts"] if v["invocation_id"] in kept]
    return _rechain(r)


def r_reorder(r: dict[str, Any]) -> dict[str, Any]:
    inv = r["invocations"]
    inv[1], inv[2] = inv[2], inv[1]
    return _reseal(r)


def r_fully_resealed_evidence_edit(r: dict[str, Any]) -> dict[str, Any]:
    """Edit evidence inside an invocation and recompute every hash. Without a signature,
    integrity hashes cannot distinguish this from an honest receipt."""
    r["invocations"][0]["result"]["evidence"] = [{"forged": True}]
    return _rechain(r)


MUTATIONS: list[Mutation] = [
    Mutation("M01", "remove all inputs", "input", True, ["inputs_present", "inputs_nonempty"], m_remove_all_inputs),
    Mutation("M02", "delete a table", "input", True, ["inputs_present", "citation_metadata"], m_delete_table),
    Mutation("M03", "delete a row", "input", True, ["snapshot_rows"], m_delete_row),
    Mutation("M04", "duplicate a row", "input", True, ["duplicate_records:records"], m_duplicate_row),
    Mutation("M05", "duplicate a verdict", "receipt", True, ["verdicts_unique_per_invocation"], r_duplicate_verdict),
    Mutation("M06", "remove a reviewer", "input", True, ["reviewer_protocol"], m_remove_reviewer),
    Mutation("M07", "change a hash (resealed)", "receipt", True, ["invocation_input_hashes_match_observed"], r_change_hash),
    Mutation("M08", "change an author", "input", True, ["citation_metadata"], m_change_author),
    Mutation("M09", "replace a DOI", "input", True, ["citation_metadata"], m_replace_doi),
    Mutation("M10", "change a number", "input", True, ["claim_value:C1", "snapshot_rows"], m_change_number),
    Mutation("M11", "add a thousands separator (semantically neutral)", "input", False, [], m_add_thousands_sep, "12480 -> 12,480 is the same number; detection would be a false positive"),
    Mutation("M11b", "add a thousands separator and change the number", "input", True, ["claim_value:C1"], m_add_thousands_sep_and_change),
    Mutation("M12", "shift a timestamp by an offset", "input", True, ["timestamp_consistency"], m_shift_timestamp),
    Mutation("M13", "remove an invocation record", "receipt", True, ["ledger_chain_intact"], r_remove_invocation),
    Mutation("M14", "inject a PASS summary with no evidence", "input", True, ["attested_invocations"], m_inject_pass_summary),
    Mutation("M15", "skip a required checker", "engine", True, ["every_required_check_has_terminal_state"], "citation_metadata"),
    Mutation("M16", "truncate the ledger (re-chained)", "receipt", True, ["every_required_check_has_terminal_state"], r_truncate_ledger),
    Mutation("M17", "reorder chained records", "receipt", True, ["ledger_chain_intact"], r_reorder),
    Mutation("M18", "bump an upstream design version", "input", True, ["dependency_validity"], m_bump_design),
    Mutation("M19", "replace a stored output", "input", True, ["claim_value:C2"], m_replace_stored_output),
    # Probes beyond the mandated list, chosen because they target suspected blind spots.
    Mutation("P01", "substitute an unauthorised reviewer identity", "input", True, ["reviewer_protocol"], m_substitute_reviewer, "protocol does not declare an authorised reviewer roster"),
    Mutation("P02", "forge a producer invocation record", "input", True, ["attested_invocations"], m_forge_producer_invocation, "producer invocation records are unauthenticated"),
    Mutation("P03", "edit evidence and fully reseal an UNSIGNED receipt", "receipt", True, ["receipt_hash_binds_content"], r_fully_resealed_evidence_edit, "hash binding without a signature cannot authenticate the sealer"),
    Mutation("P04", "near-duplicate record under a new key", "input", True, ["duplicate_records:records"], m_duplicate_record_modified, "duplicate detection is exact-match on key/row"),
]


def _detectors_from_receipt(r: dict[str, Any]) -> list[str]:
    d = [i["check"] for i in r.get("invocations", []) if i["result"]["status"] != "PASS"]
    d += [v["invariant"] for v in r.get("invariant_violations", [])]
    return sorted(set(d))


def run_mutations(base: Path | None = None) -> dict[str, Any]:
    tmp = Path(tempfile.mkdtemp(prefix="szl-mut-"))
    try:
        valid = tmp / "valid"
        if base is not None:
            shutil.copytree(base, valid)
        else:
            build_valid(valid)
        baseline = verify(valid)
        if baseline["status"] != "PASS":
            return {"error": "baseline fixture does not PASS; mutation testing is meaningless", "baseline_status": baseline["status"]}
        rows = []
        for m in MUTATIONS:
            if m.target == "input":
                work = tmp / m.id
                shutil.copytree(valid, work)
                m.apply(work)
                r = verify(work)
                detected = r["status"] != "PASS"
                detectors = _detectors_from_receipt(r)
                observed = r["status"]
            elif m.target == "receipt":
                r = m.apply(copy.deepcopy(baseline))
                res = verify_receipt(r)
                detected = not res["valid"]
                detectors = sorted({v["invariant"] for v in res["violations"]})
                observed = "REJECTED" if detected else "ACCEPTED"
            else:
                r = verify(valid, skip_checks={m.apply})
                detected = r["status"] != "PASS"
                detectors = _detectors_from_receipt(r)
                observed = r["status"]
            if m.expected_detection:
                intended = any(x in detectors for x in m.expected_detectors)
                status = ("DETECTED" if intended else "DETECTED_INCIDENTALLY") if detected else "BLIND_SPOT"
            else:
                status = "CORRECTLY_IGNORED" if not detected else "FALSE_POSITIVE"
            rows.append(
                {
                    "id": m.id,
                    "mutation": m.name,
                    "target": m.target,
                    "expected_detection": m.expected_detection,
                    "actual_detection": detected,
                    "observed": observed,
                    "status": status,
                    "detecting_invariants": detectors,
                    "missed_invariants": [x for x in m.expected_detectors if x not in detectors],
                    "note": m.note,
                }
            )
        summary = {
            "mutations": len(rows),
            "detected": sum(r["status"] == "DETECTED" for r in rows),
            "detected_incidentally": [r["id"] for r in rows if r["status"] == "DETECTED_INCIDENTALLY"],
            "correctly_ignored": sum(r["status"] == "CORRECTLY_IGNORED" for r in rows),
            "blind_spots": [r["id"] for r in rows if r["status"] == "BLIND_SPOT"],
            "false_positives": [r["id"] for r in rows if r["status"] == "FALSE_POSITIVE"],
        }
        return {"baseline_status": baseline["status"], "summary": summary, "results": rows}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

