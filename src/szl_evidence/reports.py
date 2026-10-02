"""Report rendering. Every report opens with the mandatory header block, and every audit
report carries coverage accounting."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any, Callable, Iterable

from .models import canonical_json, sha256_bytes
from .safety import ensure_within, redact

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


def scrub_json_output(obj: Any, scrub: Callable[[str], str] = redact) -> Any:
    """Sanitize a JSON-compatible copy, never a receipt or encoded JSON syntax.

    Normalize using the existing default=str policy, then scrub keys and values.
    Reject colliding names rather than silently dropping evidence. Error messages
    must not include the unsanitized keys or values.
    """
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("output key collision")
            result[key] = value
        return result

    normalized = json.loads(json.dumps(obj, default=str, ensure_ascii=False), object_pairs_hook=unique_object)

    def visit(value: Any) -> Any:
        if isinstance(value, str):
            return scrub(value)
        if isinstance(value, list):
            return [visit(item) for item in value]
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for key, item in value.items():
                name = scrub(key)
                if name in result:
                    raise ValueError("output key collision")
                result[name] = visit(item)
            return result
        return value

    return visit(normalized)


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
        text = redact_host_paths(redact(text))
        return self._names.sub("<private>", text) if self._names else text

    def _path(self, name: str) -> Path:
        p = self.out / name
        ensure_within(self.out, p)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _write(self, name: str, data: bytes) -> Path:
        """Write already sanitized bytes and bind the hash to exactly those bytes."""
        p = self._path(name)
        p.write_bytes(data)
        self.hashes[name] = sha256_bytes(data)
        return p

    def text(self, name: str, content: str) -> Path:
        return self._write(name, self._scrub(content).encode("utf-8"))

    def json(self, name: str, obj: Any) -> Path:
        clean = scrub_json_output(obj, self._scrub)
        data = json.dumps(clean, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"
        return self._write(name, data)

    def csv(self, name: str, headers: list[str], rows: list[list[Any]]) -> Path:
        def cell(value: Any) -> str:
            return self._scrub("" if value is None else str(value))

        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow([cell(value) for value in headers])
        w.writerows([cell(value) for value in row] for row in rows)
        return self._write(name, buf.getvalue().encode("utf-8"))


def report(title: str, header: dict[str, Any], body: str, coverage: dict[str, Any] | None = None) -> str:
    parts = [f"# {title}", "", header_block(header), ""]
    if coverage is not None:
        parts += ["## Coverage accounting", "", coverage_block(coverage), ""]
    parts.append(body.rstrip() + "\n")
    return "\n".join(parts)


def digest(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj))
