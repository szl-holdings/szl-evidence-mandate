"""Report rendering. Every report opens with the mandatory header block, and every audit
report carries coverage accounting."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .models import canonical_json, sha256_bytes
from .safety import ensure_within

HEADER_FIELDS = [
    "STATUS",
    "WHAT WAS EXPECTED",
    "WHAT WAS EXAMINED",
    "WHAT ACTUALLY RAN",
    "WHAT PASSED",
    "WHAT FAILED",
    "WHAT ABSTAINED",
    "WHAT REMAINS UNRESOLVED",
    "WHAT THIS RESULT DOES NOT PROVE",
]
COVERAGE_FIELDS = [
    "artifacts_expected",
    "artifacts_discovered",
    "artifacts_examined",
    "artifacts_functionally_tested",
    "artifacts_not_tested",
    "denominator_state",
]


def header_block(values: dict[str, Any]) -> str:
    missing = [f for f in HEADER_FIELDS if f not in values]
    if missing:
        raise ValueError(f"header block missing fields: {missing}")
    lines = ["```text"]
    for f in HEADER_FIELDS:
        v = values[f]
        if isinstance(v, (list, tuple)):
            v = "; ".join(str(x) for x in v) if v else "none"
        lines.append(f"{f}: {v}")
    lines.append("```")
    return "\n".join(lines)


def coverage_block(cov: dict[str, Any]) -> str:
    missing = [f for f in COVERAGE_FIELDS if f not in cov]
    if missing:
        raise ValueError(f"coverage block missing fields: {missing}")
    lines = ["```text"]
    for f in COVERAGE_FIELDS:
        lines.append(f"{f}: {cov[f]}")
    reasons = cov.get("not_tested_reasons") or {}
    if reasons:
        lines.append("# not tested (artifact: reason)")
        for k in sorted(reasons):
            lines.append(f"#   {k}: {reasons[k]}")
    lines.append("```")
    return "\n".join(lines)


def md_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def cell(x: Any) -> str:
        s = "" if x is None else str(x)
        s = " ".join(s.replace("\r", " ").split())  # CR/LF/tabs inside a cell break markdown tables
        return s.replace("|", "\\|")

    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(x) for x in r) + " |")
    return "\n".join(out)


_SEP = r"(?:\\\\|\\|/)"
_HOST_PATHS = [
    (re.compile(rf"(?i)\b[A-Z]:{_SEP}Users{_SEP}[^\\/\s\"']+{_SEP}AppData{_SEP}Local{_SEP}Temp"), "<tmp>"),
    (re.compile(rf"(?i)\b[A-Z]:{_SEP}Users{_SEP}[^\\/\s\"']+"), "<home>"),
    (re.compile(r"(?i)/(?:mnt/)?c/Users/[^/\s\"']+"), "<home>"),
]


def redact_host_paths(text: str) -> str:
    """Reports are shareable: never disclose the audit host's user profile or temp paths."""
    for rx, rep in _HOST_PATHS:
        text = rx.sub(rep, text)
    return text


class ReportWriter:
    """Writes reports only inside the configured output directory and records their hashes."""

    def __init__(self, out_dir: Path, redact_names: list[str] | None = None):
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.hashes: dict[str, str] = {}
        # Public copies: every private repo/artifact name is replaced wherever it appears.
        names = sorted({n for n in (redact_names or []) if n}, key=len, reverse=True)
        self._names = re.compile(r"(?<![\w.-])(" + "|".join(re.escape(n) for n in names) + r")(?![\w-])", re.I) if names else None

    def _scrub(self, text: str) -> str:
        text = redact_host_paths(text)
        return self._names.sub("<private>", text) if self._names else text

    def _path(self, name: str) -> Path:
        p = self.out / name
        ensure_within(self.out, p)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def text(self, name: str, content: str) -> Path:
        p = self._path(name)
        data = self._scrub(content).encode("utf-8")
        p.write_bytes(data)
        self.hashes[name] = sha256_bytes(data)
        return p

    def json(self, name: str, obj: Any) -> Path:
        p = self._path(name)
        data = self._scrub(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, default=str)).encode("utf-8") + b"\n"
        p.write_bytes(data)
        self.hashes[name] = sha256_bytes(data)
        return p

    def csv(self, name: str, headers: list[str], rows: list[list[Any]]) -> Path:
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(headers)
        w.writerows(rows)
        return self.text(name, buf.getvalue())


def report(title: str, header: dict[str, Any], body: str, coverage: dict[str, Any] | None = None) -> str:
    parts = [f"# {title}", "", header_block(header), ""]
    if coverage is not None:
        parts += ["## Coverage accounting", "", coverage_block(coverage), ""]
    parts.append(body.rstrip() + "\n")
    return "\n".join(parts)


def digest(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj))
