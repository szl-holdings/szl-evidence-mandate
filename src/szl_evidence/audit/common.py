"""Shared audit helpers: credentials (never printed), axis results, finding factory."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..models import Finding, utcnow

AXIS_STATES = {"PASS", "PARTIAL", "FAIL", "NOT_TESTED"}


@dataclass
class Axis:
    state: str
    evidence: str
    confidence: str = "HIGH"

    def __post_init__(self) -> None:
        if self.state not in AXIS_STATES:
            raise ValueError(self.state)

    def to_dict(self) -> dict[str, str]:
        return {"state": self.state, "evidence": self.evidence, "confidence": self.confidence}


def github_token() -> tuple[str | None, str]:
    """Return (token, source). Token value is never logged."""
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t, "env"
    gh = shutil.which("gh")
    if gh:
        try:
            p = subprocess.run([gh, "auth", "token"], capture_output=True, timeout=20, check=False)  # noqa: S603
            if p.returncode == 0 and p.stdout.strip():
                return p.stdout.decode().strip(), "gh-cli"
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None, "none"


def hf_token() -> tuple[str | None, str]:
    t = os.environ.get("HF_TOKEN")
    if t:
        return t, "env"
    p = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "token"
    if p.exists():
        v = p.read_text(encoding="utf-8").strip()
        if v:
            return v, "hf-cache"
    return None, "none"


@dataclass
class FindingSink:
    surface: str
    items: list[Finding] = field(default_factory=list)
    _n: int = 0

    def add(self, severity: str, artifact: str, title: str, evidence: str, source: str, confidence: str = "HIGH", category: str = "", root_cause: str = "", structural_fix: str = "", effort: str = "UNKNOWN", blocks: str = "", observed_at: str | None = None) -> Finding:
        self._n += 1
        f = Finding(
            id=f"{self.surface[:2].upper()}-{self._n:04d}",
            severity=severity,
            surface=self.surface,
            artifact=artifact,
            title=title,
            evidence=evidence,
            source=source,
            observed_at=observed_at or utcnow(),
            confidence=confidence,
            category=category,
            root_cause=root_cause,
            structural_fix=structural_fix,
            effort=effort,
            blocks=blocks,
        )
        self.items.append(f)
        return f

    def to_list(self) -> list[dict[str, Any]]:
        return [f.to_dict() for f in self.items]


SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
