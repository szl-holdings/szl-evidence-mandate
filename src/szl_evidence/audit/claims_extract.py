"""Claim extraction and verification (2.4, 3.4).

Verdicts: VERIFIED | CONTRADICTED | UNVERIFIABLE | STALE.
A dated observation that has drifted is STALE (not a lie), never CONTRADICTED.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
NUM = r"(\d{1,3}(?:,\d{3})+(?!\d)|\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
DATE = re.compile(r"\b(20\d\d-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?)\b")
PIN = re.compile(r"\b(?:sha|commit|@|at)\s*`?([0-9a-f]{7,40})`?\b", re.I)

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("inventory_count", re.compile(rf"(?i)\b{NUM}\s+(?:public\s+)?(spaces|models|datasets|repos|repositories)\b")),
    ("lean_count", re.compile(rf"(?i)\b{NUM}\s+(declarations|axioms|sorries|sorrys|theorems|experimental theorems)\b")),
    ("doctrine_version", re.compile(r"(?i)\bdoctrine\s+v(\d+)\b")),
    ("locked_marker", re.compile(r"\bLOCKED\b")),
    ("trust_ceiling", re.compile(r"(?i)trust[ -]ceiling[^0-9\n]{0,25}(\d?\.\d+)")),
    ("formula_count", re.compile(rf"(?i)\b{NUM}\s+(?:locked\s+)?formulas\b")),
    ("topology_label", re.compile(rf"(?i)\b{NUM}\s+(inference flagships?|commercial flagships?|public domain bodies|internal engines|portfolio spaces|inventory-only spaces?)\b")),
    ("doi", re.compile(r"\b(10\.\d{4,9}/[A-Za-z0-9._;()/:-]+?[A-Za-z0-9])(?:\.(?:svg|png|jpe?g|gif|pdf))?(?=$|[\s)\]>\"'`,;]|\.\s|\.$)")),
    ("dated_observation", re.compile(r"(?i)\b(observed|as of|measured|snapshot(?:ted)?|last verified)\b[^\n]{0,40}?\b(20\d\d-\d\d-\d\d(?:T[\d:]+Z?)?)")),
]
INVENTORY_CONTEXT = re.compile(r"(?i)(public|hugging ?face|huggingface|SZLHOLDINGS|estate|organi[sz]ation|org\b|github|portfolio|inventory)")
LEAN_CONTEXT = re.compile(r"(?i)(lean|lutar|sorr(y|ies)|axiom|theorem|mathlib|formal)")
SCOPE_QUALIFIER = re.compile(r"(?i)\b(experimental|separately|subset|module|excluding|only the)\b")
CORPUS_LEVEL = re.compile(r"(?i)on `?main`?|whole corpus|entire corpus|at HEAD")
SUBSET_AFTER = re.compile(r"(?i)^\W{0,3}(still need|need|carry|carrying|contain(ing)? sorry|with sorry|missing|lack|pending|remaining|left|blocked|to (go|fix|close)|staged)")
HISTORICAL = re.compile(r"(?i)\b(historical|prior|previous(ly)?|formerly|was|were|legacy|retained only)\b")


@dataclass
class Claim:
    text: str
    location: str
    claim_type: str
    value: str
    unit: str = ""
    verification_method: str = ""
    observed_value: str = "UNKNOWN"
    verdict: str = "UNVERIFIABLE"
    evidence: str = ""
    dated: str | None = None
    source_url: str = ""
    observed_at: str = ""
    confidence: str = "MEDIUM"
    source_private: bool = False
    scope_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _num(s: str) -> int | None:
    s = s.lower().replace(",", "")
    if s in WORDNUM:
        return WORDNUM[s]
    return int(s) if s.isdigit() else None


def extract(text: str, location: str, source_url: str = "", private: bool = False) -> list[Claim]:
    out: list[Claim] = []
    seen: set[tuple[str, str, str, str]] = set()
    lines = text.splitlines()
    in_code = False
    section_date: str | None = None
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.lstrip().startswith("#"):
            hd = DATE.findall(line)
            section_date = hd[0] if hd else None  # a dated heading dates every claim in its section
        ctx = " ".join(lines[max(0, i - 2) : i + 3])
        dates = DATE.findall(ctx) or ([section_date] if section_date else [])
        for ctype, rx in PATTERNS:
            for m in rx.finditer(line):
                g = m.groups() or (m.group(0),)
                value = g[0] if ctype not in ("dated_observation",) else g[1]
                unit = g[1].lower() if len(g) > 1 and ctype not in ("dated_observation",) else ""
                if ctype in ("inventory_count", "lean_count", "formula_count", "topology_label") and _num(value) is None:
                    continue
                if m.start() > 0 and line[m.start() - 1] == "-" and not value[0].isdigit():
                    continue  # hyphenated number word ("twenty-one") is not "one"
                note = ""
                if ctype in ("inventory_count", "lean_count", "formula_count") and SUBSET_AFTER.search(line[m.end() : m.end() + 40]):
                    note = f"subset count ({SUBSET_AFTER.search(line[m.end() : m.end() + 40]).group(0).strip()!r} follows)"
                if ctype == "lean_count" and unit == "axioms" and re.search(r"^\s*\(\s*\d+\s+unique", line[m.end() : m.end() + 20]):
                    unit = "axioms_raw"
                key = (f"{location}:{i + 1}", ctype, value, unit)
                if key in seen:
                    continue  # e.g. a DOI in both the badge image URL and the link URL
                seen.add(key)
                if ctype == "lean_count" and (not LEAN_CONTEXT.search(ctx) or (_num(value) or 0) < 5):
                    continue
                snippet = line.strip()
                if len(snippet) > 220:
                    a = max(0, m.start() - 90)
                    snippet = "…" + line[a : a + 200].strip() + "…"
                out.append(Claim(text=snippet, location=f"{location}:{i + 1}", claim_type=ctype, value=value, unit=unit, dated=dates[0] if dates else None, source_url=source_url, source_private=private, scope_note=note))
    return out


def verify_claims(claims: list[Claim], facts: dict[str, Any], now: str) -> list[Claim]:
    """facts: {public_counts: {spaces, models, datasets, repos}, public_counts_at,
    lean: {head: {...}, pinned: {...}|None, head_sha, pinned_sha}, doi_status: {doi: state}}"""
    pc = facts.get("public_counts") or {}
    lean = facts.get("lean") or {}
    doctrine_versions: dict[str, list[str]] = {}
    for c in claims:
        c.observed_at = now
        if c.claim_type == "doctrine_version":
            doctrine_versions.setdefault(c.value, []).append(c.location)
    for c in claims:
        t = c.claim_type
        if c.scope_note and t in ("inventory_count", "lean_count", "formula_count"):
            c.verification_method = "not a whole-estate/corpus figure"
            c.verdict = "UNVERIFIABLE"
            c.evidence = c.scope_note
            c.confidence = "MEDIUM"
            continue
        if t == "inventory_count":
            unit = {"repositories": "repos"}.get(c.unit, c.unit)
            n = _num(c.value)
            hist = bool(HISTORICAL.search(c.text))
            if not INVENTORY_CONTEXT.search(c.text) and (n or 0) < 10:
                c.verification_method = "not an estate inventory statement (context-dependent count)"
                c.verdict = "UNVERIFIABLE"
                c.confidence = "LOW"
                continue
            live = pc.get(unit)
            auth = (facts.get("auth_counts") or {}).get(unit)
            at = facts.get("repos_counted_at") if unit == "repos" else facts.get("public_counts_at")
            how = "GitHub org listing (authenticated; public = non-private)" if unit == "repos" else "anonymous HF listing"
            if c.source_private and auth is not None:
                live = auth  # a private card is read by insiders: compare with the authenticated total
                how += "; private source compared with authenticated total"
            c.verification_method = f"{how} at {at}; authenticated total {auth}"
            if live is None:
                c.verdict = "UNVERIFIABLE"
                c.evidence = "live count unavailable"
                continue
            c.observed_value = str(live)
            if hist:
                c.verdict = "UNVERIFIABLE"
                c.evidence = f"explicitly historical figure {n}; live {live}; a historical snapshot cannot be re-observed"
                continue
            if n == live:
                c.verdict = "VERIFIED"
                c.evidence = f"claimed {n} == live public {live}"
            elif auth is not None and n == auth:
                c.verdict = "VERIFIED"
                c.evidence = f"claimed {n} == authenticated total {auth} (includes private); public {live}"
            elif c.dated:
                c.verdict = "STALE"
                c.evidence = f"claimed {n} observed {c.dated}; live {live} observed {at}; drift {live - (n or 0):+d}"
            else:
                c.verdict = "CONTRADICTED"
                c.evidence = f"undated claim {n} != live public {live} (authenticated total {auth})"
            c.confidence = "HIGH" if INVENTORY_CONTEXT.search(c.text) else "MEDIUM"
        elif t == "lean_count":
            key = {"declarations": "declarations", "axioms": "axioms_unique", "axioms_raw": "axioms_raw", "sorries": "sorries_raw", "sorrys": "sorries_raw"}.get(c.unit)
            n = _num(c.value)
            head = lean.get("head") or {}
            pinned = lean.get("pinned") or {}
            if not key or not head:
                c.verification_method = "no recomputable Lean quantity for this unit" if not key else "Lean corpus unavailable"
                c.verdict = "UNVERIFIABLE"
                continue
            c.verification_method = f"recomputed by parsing lutar-lean .lean sources (HEAD {str(lean.get('head_sha'))[:8]}; pinned {str(lean.get('pinned_sha'))[:8]})"
            hv = head.get(key)
            pv = pinned.get(key) if pinned else None
            alt = head.get("sorries_live") if key == "sorries_raw" else (head.get("axioms_raw") if key == "axioms_unique" else None)
            c.observed_value = f"HEAD={hv}" + (f", pinned={pv}" if pv is not None else "")
            palt = (pinned.get("sorries_noncomment") if key == "sorries_raw" else (pinned.get("axioms_raw") if key == "axioms_unique" else None)) if pinned else None
            sq = SCOPE_QUALIFIER.search(c.text)
            if sq and CORPUS_LEVEL.search(c.text):
                sq = None  # e.g. "the experimental library on `main`" is the corpus at HEAD
            if sq and n not in (hv, alt, pv, palt):
                c.verdict = "UNVERIFIABLE"
                c.evidence = f"scope-qualified claim ({sq.group(0)!r}); whole-corpus recount HEAD={hv}, pinned={pv}; subset not machine-resolvable"
                c.confidence = "MEDIUM"
                continue
            if n in (hv, alt):
                c.verdict = "VERIFIED"
                c.evidence = f"claimed {n} matches HEAD recomputation"
            elif pv is not None and n in (pv, palt):
                c.verdict = "STALE"
                c.evidence = f"claimed {n} matches pinned revision {str(lean.get('pinned_sha'))[:8]} ({lean.get('pinned_date')}) but HEAD {str(lean.get('head_sha'))[:8]} has {hv}"
            elif c.dated or PIN.search(c.text):
                c.verdict = "STALE"
                c.evidence = f"dated/pinned claim {n}; HEAD recomputation {hv}"
            else:
                c.verdict = "CONTRADICTED"
                c.evidence = f"undated claim {n}; HEAD recomputation {hv}" + (f"; pinned {pv}" if pv is not None else "")
            c.confidence = "HIGH"
        elif t == "doi":
            st = (facts.get("doi_status") or {}).get(c.value.rstrip(".").lower(), "NOT_TESTED")
            c.verification_method = "doi.org handle resolution (existence only, not content)"
            c.observed_value = st
            c.verdict = {"FOUND": "VERIFIED", "NOT_FOUND": "CONTRADICTED"}.get(st, "UNVERIFIABLE")
            c.evidence = f"handle state {st}; existence does not verify the content attributed to it"
        elif t == "doctrine_version":
            versions = sorted(doctrine_versions, key=lambda v: int(v))
            c.verification_method = "listed with every other doctrine version referenced (see consistency section); no machine-checkable doctrine definition"
            c.observed_value = f"versions referenced across estate: {versions}"
            c.verdict = "UNVERIFIABLE"
            c.evidence = "doctrine content/lock state has no machine check; consistency only"
        elif t in ("locked_marker", "trust_ceiling", "formula_count", "topology_label"):
            c.verification_method = "no machine-checkable definition; recorded for consistency analysis"
            c.verdict = "UNVERIFIABLE"
        elif t == "dated_observation":
            c.verification_method = "recorded timestamp; drift assessed on the associated counts"
            c.verdict = "UNVERIFIABLE"
            c.observed_value = f"observation date {c.value}; today {now}"
    return claims


def consistency(claims: list[Claim]) -> list[dict[str, Any]]:
    """Same fact stated differently in two places (e.g. trust ceiling 0.97 vs 0.95)."""
    groups: dict[tuple[str, str, str], dict[str, list[str]]] = {}
    for c in claims:
        if c.scope_note or (c.verdict == "UNVERIFIABLE" and c.claim_type == "lean_count"):
            continue
        pin = PIN.search(c.text)
        basis = f"pinned@{pin.group(1)[:8]}" if pin else (f"dated {c.dated[:10]}" if c.dated else "undated")
        if c.claim_type in ("trust_ceiling",):
            key = (c.claim_type, "", "any")
        elif c.claim_type in ("lean_count",) and not HISTORICAL.search(c.text):
            key = (c.claim_type, c.unit, basis)
        elif c.claim_type in ("formula_count", "topology_label") and not HISTORICAL.search(c.text):
            key = (c.claim_type, c.unit, "any")
        else:
            continue
        groups.setdefault(key, {}).setdefault(str(_num(c.value) if c.claim_type != "trust_ceiling" else c.value), []).append(c.location)
    out = []
    for (t, u, b), vals in sorted(groups.items()):
        if len(vals) > 1:
            out.append({"claim_type": t, "unit": u, "basis": b, "values": {k: v for k, v in sorted(vals.items())}, "locations_total": sum(len(v) for v in vals.values())})
    versions: dict[str, list[str]] = {}
    for c in claims:
        if c.claim_type == "doctrine_version":
            versions.setdefault(c.value, []).append(c.location)
    if len(versions) > 1:
        out.append({"claim_type": "doctrine_version", "unit": "", "basis": "any (current and historical uses mixed)", "values": {f"v{k}": v for k, v in sorted(versions.items(), key=lambda kv: int(kv[0]))}, "locations_total": sum(len(v) for v in versions.values())})
    return out
