"""Append-only, hash-chained execution ledger.

Every check that runs becomes an invocation record. Verdicts reference invocations.
The PASS evidence block is computed from this ledger, never composed independently.
"""

from __future__ import annotations

from typing import Any

from .models import CheckResult, sha256_json, utcnow

GENESIS = "0" * 64


class Ledger:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.invocations: list[dict[str, Any]] = []
        self.verdicts: list[dict[str, Any]] = []

    @property
    def head(self) -> str:
        return self.invocations[-1]["entry_sha256"] if self.invocations else GENESIS

    def record(
        self,
        check: str,
        version: str,
        input_ids: list[str],
        input_hashes: dict[str, str],
        result: CheckResult,
        started_at: str,
    ) -> dict[str, Any]:
        seq = len(self.invocations)
        inv: dict[str, Any] = {
            "seq": seq,
            "invocation_id": sha256_json([self.run_id, seq, check, version])[:24],
            "check": check,
            "check_version": version,
            "input_ids": sorted(input_ids),
            "input_hashes": {k: input_hashes[k] for k in sorted(input_hashes)},
            "started_at": started_at,
            "completed_at": utcnow(),
            "result": result.to_dict(),
            "prev_sha256": self.head,
        }
        inv["entry_sha256"] = sha256_json(inv)
        self.invocations.append(inv)
        self.verdicts.append(
            {
                "verdict_id": f"v-{seq:04d}",
                "invocation_id": inv["invocation_id"],
                "check": check,
                "verdict": result.status.value,
                "reason_code": result.reason.value,
            }
        )
        return inv


def verify_chain(invocations: list[dict[str, Any]]) -> list[str]:
    """Return a list of chain violations (empty when intact)."""
    problems: list[str] = []
    prev = GENESIS
    for i, inv in enumerate(invocations):
        if inv.get("seq") != i:
            problems.append(f"sequence break at position {i} (seq={inv.get('seq')})")
        if inv.get("prev_sha256") != prev:
            problems.append(f"chain link broken at seq {inv.get('seq')}")
        body = {k: v for k, v in inv.items() if k != "entry_sha256"}
        if sha256_json(body) != inv.get("entry_sha256"):
            problems.append(f"entry hash mismatch at seq {inv.get('seq')}")
        prev = inv.get("entry_sha256", "")
    return problems
