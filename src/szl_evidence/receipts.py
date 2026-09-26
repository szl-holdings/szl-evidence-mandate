"""Canonical receipts with SHA-256 content binding and optional hash chaining.

A receipt supports integrity, provenance, and replayability. It does not establish scientific truth, accuracy, safety, or fitness for use.
"""

from __future__ import annotations

import base64
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import TOOL_NAME, __version__
from .models import UNKNOWN, canonical_json, sha256_json

SCHEMA_VERSION = "szl.evidence.receipt/v1"
RECEIPT_STATEMENT = (
    "A receipt supports integrity, provenance, and replayability. "
    "It does not establish scientific truth, accuracy, safety, or fitness for use."
)
HASH_EXCLUDED = ("receipt_sha256", "signature")


@lru_cache(maxsize=1)
def code_revision() -> str:
    """Git HEAD of the tool checkout, read from .git without running git; UNKNOWN otherwise."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        g = parent / ".git"
        if g.is_dir():
            head = (g / "HEAD").read_text().strip()
            if head.startswith("ref: "):
                ref = g / head[5:]
                if ref.exists():
                    return ref.read_text().strip()
                packed = g / "packed-refs"
                if packed.exists():
                    for line in packed.read_text().splitlines():
                        if line.endswith(head[5:]):
                            return line.split()[0]
                return UNKNOWN
            return head
    return UNKNOWN


def tool_block() -> dict[str, str]:
    return {"name": TOOL_NAME, "version": __version__, "code_revision": code_revision()}


def receipt_hash(receipt: dict[str, Any]) -> str:
    return sha256_json({k: v for k, v in receipt.items() if k not in HASH_EXCLUDED})


def seal(receipt: dict[str, Any]) -> dict[str, Any]:
    """Bind content hash and attach a signature only if a real key is configured."""
    receipt.setdefault("schema_version", SCHEMA_VERSION)
    receipt.setdefault("receipt_statement", RECEIPT_STATEMENT)
    key_path = os.environ.get("SZL_RECEIPT_ED25519_KEY")
    receipt["signature_state"] = "UNSIGNED"
    receipt.pop("signature", None)
    if key_path:
        receipt["signature_state"] = "SIGNING_PENDING"
    receipt["receipt_sha256"] = receipt_hash(receipt)
    if key_path:
        sig = _try_sign(Path(key_path), receipt["receipt_sha256"])
        if sig is None:
            # Key configured but unusable: remain honest.
            receipt["signature_state"] = "UNSIGNED"
            receipt["signature_note"] = "signing key configured but could not be used; receipt left UNSIGNED"
            receipt["receipt_sha256"] = receipt_hash(receipt)
        else:
            receipt["signature"] = sig
    return receipt


def _try_sign(key_path: Path, digest_hex: str) -> dict[str, str] | None:
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key  # type: ignore
    except ImportError:
        return None
    try:
        key = load_pem_private_key(key_path.read_bytes(), password=None)
        sig = key.sign(bytes.fromhex(digest_hex))  # type: ignore[call-arg]
    except Exception:  # noqa: BLE001 - any key failure means UNSIGNED, never a fake signature
        return None
    return {"alg": "ed25519", "over": "receipt_sha256", "value": base64.b64encode(sig).decode()}


def chain(receipt: dict[str, Any], parent: dict[str, Any] | None) -> dict[str, Any]:
    receipt["parent_sha256"] = parent["receipt_sha256"] if parent else None
    return receipt


def write_receipt(receipt: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(receipt) + b"\n")
    return path


def simple_receipt(kind: str, payload: dict[str, Any], started_at: str, completed_at: str, status: str, limitations: list[str]) -> dict[str, Any]:
    """Receipt for audit runs (github/hf/reconcile/zoomout)."""
    r = {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "run_id": sha256_json([kind, started_at, payload.get("inputs_sha256")])[:16],
        "tool": tool_block(),
        "started_at": started_at,
        "completed_at": completed_at,
        "status": status,
        "payload": payload,
        "limitations": limitations,
        "parent_sha256": None,
    }
    return seal(r)
