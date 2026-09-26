"""Engine orchestration: discover -> run every required check -> ledger -> receipt -> invariants."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters.citations import CitationResolver, OfflineResolver
from .checks import CHECKS_BY_NAME, Context, applicable_checks
from .discovery import discover
from .invariants import aggregate, check_invariants, pass_block
from .ledger import Ledger
from .manifest import ManifestError, load_manifest
from .models import CheckResult, Failure, Reason, Status, sha256_json, utcnow
from .receipts import RECEIPT_STATEMENT, seal, tool_block

POPULATION_CHECKS = {"snapshot_rows", "claim_value", "population_closure", "reviewer_protocol", "output_determinism", "source_identity", "timestamp_consistency"}

LIMITATIONS = [
    RECEIPT_STATEMENT,
    "Offline citation resolution is only as complete as the declared registry snapshot.",
    "Recipes are declarative aggregates; arbitrary analysis code is not replayed.",
]


def _severity_reason(results: list[CheckResult], status: Status) -> Reason:
    for r in results:
        if r.status == status:
            return r.reason
    return Reason.VERIFIED


def verify(
    manifest_path: str | Path,
    resolver: CitationResolver | None = None,
    skip_checks: set[str] | None = None,
    parent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the evidence gate. Returns a sealed receipt dict (status + exit_code inside)."""
    started = utcnow()
    try:
        m = load_manifest(manifest_path)
    except ManifestError as e:
        return _error_receipt(str(manifest_path), started, f"manifest error: {e}")
    run_id = sha256_json([m.sha256, started])[:16]
    ledger = Ledger(run_id)
    disc = discover(m)
    ctx = Context(m, disc, resolver or OfflineResolver())
    try:
        checks = applicable_checks(m)
    except KeyError as e:
        return _error_receipt(str(manifest_path), started, str(e))

    required: list[str] = []
    plan: list[tuple[Any, list[str]]] = []
    for c in checks:
        subjects = c.subjects(ctx) if c.subjects else None
        keys = [f"{c.name}:{s}" for s in subjects] if subjects else [c.name]
        required += keys
        plan.append((c, keys))

    results: list[CheckResult] = []
    for c, keys in plan:
        if skip_checks and c.name in skip_checks:
            continue  # simulates a verifier that silently skips a checker
        if c.name in (m.sections.get("deferred_checks") or []):
            for k in keys:
                res = CheckResult(Status.ABSTAIN, Reason.NOT_TESTED, [{"deferred_by_manifest": True}], [], "check declared deferred by the manifest; not run")
                ledger.record(k, c.version, [], {}, res, utcnow())
                results.append(res)
            continue
        t0 = utcnow()
        input_ids = [i for i in c.inputs(ctx) if i]
        hashes = {i: disc.hashes[i] for i in input_ids if i in disc.hashes}
        # Conservative: population-level checks may join any table, so any partial table blocks them.
        partial = sorted(i for i in disc.rows_parsed if disc.rows_examined.get(i, 0) < disc.rows_parsed[i])
        if c.name in POPULATION_CHECKS and partial:
            # A population-level verdict drawn from a subset would be an artifact of the subset.
            res_p = CheckResult(Status.ABSTAIN, Reason.INSUFFICIENT_EVIDENCE, [{"partially_examined_inputs": partial}], [Failure.PARTIAL_EXECUTION], "population check not decidable on a partial view")
            out = {(k.split(":", 1)[1] if ":" in k else ""): res_p for k in keys}
        else:
            out = None
        try:
            if out is None:
                out = c.run(ctx)
        except Exception as e:  # noqa: BLE001 - a crashing check is a verifier ERROR, never a PASS
            out = {k.split(":", 1)[1] if ":" in k else "": CheckResult(Status.ERROR, Reason.PROTOCOL_BROKEN, [{"exception": e.__class__.__name__, "message": str(e)[:300]}], detail="check crashed") for k in keys}
        for k in keys:
            sub = k.split(":", 1)[1] if ":" in k else ""
            res = out.get(sub)
            if res is None and len(keys) == 1 and len(out) == 1:
                res = next(iter(out.values()))
            if res is None:
                res = CheckResult(Status.ERROR, Reason.PROTOCOL_BROKEN, [{"missing_subject": k}], detail="check produced no result for a required subject")
            sub_hashes = dict(hashes)
            if sub and sub in disc.hashes:
                sub_hashes[sub] = disc.hashes[sub]
            ledger.record(k, c.version, list(sub_hashes) or input_ids, sub_hashes, res, t0)
            results.append(res)

    acct = disc.accounting()
    acct["claims_checked"] = sum(1 for k in required if k.startswith("claim_value:"))
    acct["checks_expected"] = len(required)
    acct["checks_executed"] = len(ledger.invocations)
    evidence_manifest = [
        {"input_id": i, "sha256": disc.hashes[i], "bytes": disc.sizes.get(i), "rows_parsed": disc.rows_parsed.get(i), "rows_examined": disc.rows_examined.get(i)}
        for i in sorted(disc.hashes)
    ]
    statuses = [i["result"]["status"] for i in ledger.invocations]
    status_s = aggregate(statuses)
    if acct["rows_examined"] == 0 and status_s == "PASS":
        status_s = "ABSTAIN"
    status = Status(status_s)
    failures = sorted({f.value for r in results for f in r.failures})
    if acct["rows_examined"] == 0 and "VACUOUS_PASS" not in failures:
        failures.append("VACUOUS_PASS")
    dep_ev = next((i["result"]["evidence"] for i in ledger.invocations if i["check"] == "dependency_validity"), None)
    review_ev = next((i["result"] for i in ledger.invocations if i["check"] == "reviewer_protocol"), None)

    receipt: dict[str, Any] = {
        "run_id": run_id,
        "parent_sha256": parent["receipt_sha256"] if parent else None,
        "tool": tool_block(),
        "manifest": {"name": m.name, "version": m.version, "sha256": m.sha256, "access": m.access},
        "started_at": started,
        "completed_at": utcnow(),
        "expected_inputs": disc.expected,
        "observed_inputs": {i: {"sha256": disc.hashes[i], "bytes": disc.sizes.get(i)} for i in sorted(disc.hashes)},
        "evidence_manifest": evidence_manifest,
        "evidence_manifest_sha256": sha256_json(evidence_manifest),
        "accounting": acct,
        "required_checks": required,
        "invocations": ledger.invocations,
        "verdicts": ledger.verdicts,
        "invocation_count": len(ledger.invocations),
        "ledger_head_sha256": ledger.head,
        "status": status.value,
        "exit_code": status.exit_code,
        "reason_codes": sorted({r.reason.value for r in results if r.status != Status.PASS}) or ["VERIFIED"],
        "primary_reason": _severity_reason(results, status).value,
        "failures": failures,
        "dependency_impact": dep_ev[0] if dep_ev else "NOT_TESTED",
        "human_review_state": (review_ev["reason"] if review_ev else "NOT_TESTED"),
        "output_hashes": {},
        "limitations": LIMITATIONS,
        "pass_evidence": None,
        "invariant_violations": [],
    }
    if status == Status.PASS:
        receipt["pass_evidence"] = pass_block(receipt)
    violations = check_invariants(receipt, check_hash=False)
    if violations:
        receipt["invariant_violations"] = violations
        receipt["status"] = Status.ERROR.value
        receipt["exit_code"] = Status.ERROR.exit_code
        receipt["primary_reason"] = Reason.PROTOCOL_BROKEN.value
        receipt["pass_evidence"] = None
    return seal(receipt)


def _error_receipt(path: str, started: str, msg: str) -> dict[str, Any]:
    r = {
        "run_id": sha256_json([path, started])[:16],
        "parent_sha256": None,
        "tool": tool_block(),
        "manifest": {"path": Path(path).name},
        "started_at": started,
        "completed_at": utcnow(),
        "status": "ERROR",
        "exit_code": 3,
        "primary_reason": "PROTOCOL_BROKEN",
        "reason_codes": ["PROTOCOL_BROKEN"],
        "error": msg,
        "invocations": [],
        "verdicts": [],
        "required_checks": [],
        "invocation_count": 0,
        "limitations": LIMITATIONS,
        "pass_evidence": None,
        "invariant_violations": [{"invariant": "verifier_error", "detail": msg}],
    }
    return seal(r)


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Independently re-check a receipt produced elsewhere (or tampered with)."""
    v = check_invariants(receipt)
    return {"valid": not v, "violations": v, "status_claimed": receipt.get("status")}


__all__ = ["verify", "verify_receipt", "CHECKS_BY_NAME"]
