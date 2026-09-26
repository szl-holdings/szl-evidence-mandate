"""Discover, open and parse declared inputs with full accounting.

Accounting identities (1.5):
    expected_inputs   = opened + missing + deferred + failed
    retrieved_records = admitted + excluded + unresolved   (computed by the population check)
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import Manifest
from .models import sha256_file
from .safety import UnsafeInput, check_size, contained, load_json, load_yaml, safe_walk


@dataclass
class Discovery:
    expected: list[str] = field(default_factory=list)
    discovered: list[str] = field(default_factory=list)  # relative paths found on disk
    undeclared: list[str] = field(default_factory=list)  # discovered but never entered the checked set
    excluded: list[str] = field(default_factory=list)  # explicitly excluded by manifest ignore rules
    opened: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    deferred: list[str] = field(default_factory=list)
    empty: list[str] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)
    sizes: dict[str, int] = field(default_factory=dict)
    tables: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    rows_parsed: dict[str, int] = field(default_factory=dict)
    rows_examined: dict[str, int] = field(default_factory=dict)
    inputs_dir_exists: bool = False

    def accounting(self) -> dict[str, Any]:
        expected = len(self.expected)
        closure_rhs = len(self.opened) + len(self.missing) + len(self.deferred) + len(self.failed)
        return {
            "expected": expected,
            "discovered": len(self.discovered),
            "opened": len(self.opened),
            "parsed": len(self.opened),
            "missing": len(self.missing),
            "deferred": len(self.deferred),
            "failed": len(self.failed),
            "empty": len(self.empty),
            "undeclared_discovered": len(self.undeclared),
            "excluded_by_rule": len(self.excluded),
            "rows_parsed": sum(self.rows_parsed.values()),
            "rows_examined": sum(self.rows_examined.values()),
            "input_closure": {
                "identity": "expected = opened + missing + deferred + failed",
                "lhs": expected,
                "rhs": closure_rhs,
                "closes": expected == closure_rhs,
            },
            "denominator_state": "OBSERVED" if self.inputs_dir_exists else "UNAVAILABLE",
        }


def _parse_csv(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), strict=True)
    rows = []
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise UnsafeInput(f"ragged CSV row in {path.name} at line {reader.line_num}")
        rows.append(dict(row))
    return rows


def discover(manifest: Manifest) -> Discovery:
    d = Discovery()
    root = manifest.root
    limits = manifest.sections.get("limits") or {}
    max_rows = limits.get("max_rows")
    inputs_dir = root / manifest.inputs_dir
    d.inputs_dir_exists = inputs_dir.is_dir()
    declared_paths = {Path(s.path).as_posix() for s in manifest.inputs}
    if d.inputs_dir_exists:
        for f in safe_walk(inputs_dir):
            rel = f.relative_to(root).as_posix()
            if any(Path(rel).match(g) for g in manifest.ignore):
                d.excluded.append(rel)
                continue
            d.discovered.append(rel)
            if rel not in declared_paths:
                d.undeclared.append(rel)

    for spec in manifest.inputs:
        d.expected.append(spec.id)
        try:
            p = contained(root, spec.path)
        except UnsafeInput as e:
            d.failed[spec.id] = str(e)
            continue
        if not p.exists():
            (d.missing if spec.required else d.deferred).append(spec.id)
            continue
        try:
            d.sizes[spec.id] = check_size(p)
            d.hashes[spec.id] = sha256_file(p)
            if spec.kind == "table":
                rows = _parse_csv(p)
                d.rows_parsed[spec.id] = len(rows)
                examined = rows if max_rows is None else rows[: int(max_rows)]
                d.rows_examined[spec.id] = len(examined)
                d.tables[spec.id] = examined
                if not rows:
                    d.empty.append(spec.id)
            elif spec.kind == "json":
                d.data[spec.id] = load_json(p)
            elif spec.kind == "yaml":
                d.data[spec.id] = load_yaml(p)
            elif spec.kind == "jsonl":
                d.data[spec.id] = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
            else:
                d.data[spec.id] = None
            if spec.kind != "table" and d.sizes[spec.id] == 0:
                d.empty.append(spec.id)
            d.opened.append(spec.id)
        except (UnsafeInput, UnicodeDecodeError, csv.Error, json.JSONDecodeError, OSError) as e:
            d.failed[spec.id] = f"{e.__class__.__name__}: {e}"
    return d
