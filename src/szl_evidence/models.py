"""Core enumerations and data records shared by the engine and the audits."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ABSTAIN = "ABSTAIN"
    ERROR = "ERROR"

    @property
    def exit_code(self) -> int:
        return {"PASS": 0, "FAIL": 1, "ABSTAIN": 2, "ERROR": 3}[self.value]


class Reason(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_MISMATCH = "SOURCE_MISMATCH"
    PROTOCOL_BROKEN = "PROTOCOL_BROKEN"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    NOT_TESTED = "NOT_TESTED"


class Failure(str, Enum):
    """Failure taxonomy (1.2). Reported separately from the terminal status."""

    VACUOUS_PASS = "VACUOUS_PASS"
    NARRATED_VERIFICATION = "NARRATED_VERIFICATION"
    PARTIAL_EXECUTION = "PARTIAL_EXECUTION"
    DEFECTIVE_VERIFICATION = "DEFECTIVE_VERIFICATION"
    OMITTED_POPULATION = "OMITTED_POPULATION"
    SOURCE_MISMATCH = "SOURCE_MISMATCH"
    PROTOCOL_DRIFT = "PROTOCOL_DRIFT"
    EPHEMERAL_CLAIM = "EPHEMERAL_CLAIM"


class Validity(str, Enum):
    CURRENT = "CURRENT"
    STALE_PENDING_REVALIDATION = "STALE_PENDING_REVALIDATION"
    REVALIDATED_UNCHANGED = "REVALIDATED_UNCHANGED"
    REVALIDATED_CHANGED = "REVALIDATED_CHANGED"
    SUPERSEDED = "SUPERSEDED"
    INVALIDATED = "INVALIDATED"
    UNRESOLVED = "UNRESOLVED"


# Values used wherever something was not measured. Never 0 / False / omitted.
UNKNOWN = "UNKNOWN"
UNAVAILABLE = "UNAVAILABLE"
NOT_TESTED = "NOT_TESTED"


@dataclass
class CheckResult:
    """What a single check produced. Converted into an invocation by the ledger."""

    status: Status
    reason: Reason
    evidence: list[dict[str, Any]] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)
    detail: str = ""
    rows_examined: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["reason"] = self.reason.value
        d["failures"] = [f.value for f in self.failures]
        return d


@dataclass
class Finding:
    """An audit finding. Every finding carries evidence, source, timestamp and confidence."""

    id: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    surface: str  # github | huggingface | cross-surface | engine
    artifact: str
    title: str
    evidence: str
    source: str
    observed_at: str
    confidence: str  # HIGH | MEDIUM | LOW
    category: str = ""
    root_cause: str = ""
    structural_fix: str = ""
    effort: str = UNKNOWN
    blocks: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fixed_now() -> datetime | None:
    """Honour SOURCE_DATE_EPOCH so runs can be made byte-deterministic."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    return None


def utcnow() -> str:
    now = fixed_now() or datetime.now(timezone.utc)
    return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(obj: Any) -> bytes:
    """Canonical JSON: sorted keys, no insignificant whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode(
        "utf-8"
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj))


def sha256_file(path: os.PathLike | str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
