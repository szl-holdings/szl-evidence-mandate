"""Claim registry, numeric parsing and comparison, and declarative recipe replay.

Numbers are never compared as strings. Every published value is parsed to a Decimal
with its stated precision, thousands separators are handled explicitly, and equality
between two measured quantities is decided on the unrounded values with a declared
tolerance so rounding cannot manufacture agreement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from typing import Any

REGISTRY_CHAIN = [
    "recipe",
    "code_version",
    "environment",
    "input_manifest_sha256",
    "stored_output",
    "output_sha256",
    "review_state",
    "publication",
]

_GROUPED = re.compile(r"^[+-]?\d{1,3}(,\d{3})+(\.\d+)?$")
_PLAIN = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
_THIN = re.compile(r"^[+-]?\d{1,3}([   _]\d{3})+(\.\d+)?$")


class NumberParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedNumber:
    raw: str
    value: Decimal
    decimals: int  # stated precision (digits after the point)
    had_separator: bool


def parse_number(raw: Any) -> ParsedNumber:
    """Parse a published number. Grouped thousands ("12,480") are accepted only when
    the grouping is well-formed; an ambiguous comma ("1,5") is rejected, never guessed."""
    if isinstance(raw, bool):
        raise NumberParseError("boolean is not a number")
    if isinstance(raw, int):
        return ParsedNumber(str(raw), Decimal(raw), 0, False)
    if isinstance(raw, float):
        s = repr(raw)
    else:
        s = str(raw).strip()
    s = s.rstrip("%") if s.endswith("%") else s
    had_sep = False
    if _GROUPED.match(s):
        had_sep = True
        s_clean = s.replace(",", "")
    elif _THIN.match(s):
        had_sep = True
        s_clean = re.sub(r"[   _]", "", s)
    elif _PLAIN.match(s):
        s_clean = s
    else:
        raise NumberParseError(f"unparseable or ambiguous number: {raw!r}")
    try:
        d = Decimal(s_clean)
    except InvalidOperation as e:  # pragma: no cover - guarded by regexes
        raise NumberParseError(str(e)) from e
    decimals = len(s_clean.split(".", 1)[1]) if "." in s_clean and "e" not in s_clean.lower() else 0
    return ParsedNumber(str(raw), d, decimals, had_sep)


def round_to(value: Decimal, decimals: int) -> Decimal:
    q = Decimal(1).scaleb(-decimals)
    return value.quantize(q, rounding=ROUND_HALF_EVEN)


def value_matches(published: Any, measured: Any) -> tuple[bool, dict[str, Any]]:
    """Does a published value agree with the stored measurement at the published precision?"""
    p = parse_number(published)
    m = parse_number(measured)
    rounded = round_to(m.value, p.decimals)
    ok = rounded == p.value
    return ok, {
        "published": p.raw,
        "published_value": str(p.value),
        "published_decimals": p.decimals,
        "measured": m.raw,
        "measured_rounded": str(rounded),
        "numeric_comparison": True,
        "string_equal": str(published).strip() == str(measured).strip(),
    }


def quantities_equal(a: Any, b: Any, tolerance: Any) -> tuple[bool, dict[str, Any]]:
    """Equality of two measured quantities on unrounded values under an explicit tolerance."""
    pa, pb, tol = parse_number(a), parse_number(b), parse_number(tolerance)
    diff = abs(pa.value - pb.value)
    return diff <= tol.value, {"a": str(pa.value), "b": str(pb.value), "abs_diff": str(diff), "tolerance": str(tol.value)}


# ---------------------------------------------------------------- recipes
SAFE_OPS = {"count", "sum", "mean", "min", "max", "count_distinct"}
RECIPE_INTERPRETER = "szl_evidence.claims.run_recipe/1"


class RecipeOutOfScope(ValueError):
    """The recipe asks for an operation this interpreter does not implement (OUT_OF_SCOPE)."""


def recipe_tables(recipes: list[dict[str, Any]]) -> list[str]:
    return sorted({str(r.get("table")) for r in recipes})


def input_manifest_sha256(recipes: list[dict[str, Any]], hashes: dict[str, str]) -> str:
    """Binds a registered claim to the exact bytes of the tables its recipe reads."""
    from .models import sha256_json

    return sha256_json({t: hashes.get(t, "MISSING") for t in recipe_tables(recipes)})


def run_recipe(recipe: dict[str, Any], tables: dict[str, list[dict[str, str]]]) -> Decimal:
    """Replay a declarative recipe. Only whitelisted aggregate ops; no code execution."""
    op = recipe.get("op")
    if op not in SAFE_OPS:
        raise RecipeOutOfScope(f"recipe op not implemented by {RECIPE_INTERPRETER}: {op!r}")
    table = recipe.get("table")
    if table not in tables:
        raise KeyError(f"recipe table missing: {table!r}")
    rows = tables[table]
    where = recipe.get("where") or {}
    rows = [r for r in rows if all(str(r.get(k)) == str(v) for k, v in where.items())]
    if op == "count":
        return Decimal(len(rows))
    field = recipe.get("field")
    if op == "count_distinct":
        return Decimal(len({r.get(field) for r in rows}))
    vals = [parse_number(r[field]).value for r in rows]
    if not vals:
        raise ValueError("recipe over zero rows is undefined")
    if op == "sum":
        return sum(vals, Decimal(0))
    if op == "mean":
        return sum(vals, Decimal(0)) / Decimal(len(vals))
    if op == "min":
        return min(vals)
    return max(vals)


def missing_chain_links(entry: dict[str, Any] | None) -> list[str]:
    if not entry:
        return list(REGISTRY_CHAIN)
    return [k for k in REGISTRY_CHAIN if entry.get(k) in (None, "", [], {})]
