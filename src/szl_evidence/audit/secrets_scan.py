"""Secret scanning: known token patterns plus high-entropy assignments.

Reports location (path, line) and type only. The matched value is never returned,
logged or written; only a short fingerprint (sha256 prefix) is kept so duplicates can be
correlated without disclosure.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from ..models import sha256_bytes
from ..safety import CREDENTIAL_PATTERNS, safe_walk

# Backwards-compatible scanner export; regexes and classification are unchanged.
PATTERNS = CREDENTIAL_PATTERNS

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".lake", ".next", "target"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".tar", ".whl", ".npz", ".npy", ".safetensors", ".bin", ".gguf", ".pt", ".onnx", ".woff", ".woff2", ".ttf", ".mp4", ".webp", ".lock", ".svg", ".parquet", ".arrow"}
PLACEHOLDER = re.compile(r"(?i)(x{6,}|example|placeholder|dummy|your[_-]?|changeme|redacted|<[^>]+>|\*{4,}|test|fake|sample|0{10,}|1234567)")
MAX_BYTES = 2_000_000


@dataclass
class SecretHit:
    path: str
    line: int
    type: str
    confidence: str
    fingerprint: str  # sha256(value)[:12] - correlation only, not reversible
    likely_live: bool
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return dict(self.__dict__)


def entropy(s: str) -> float:
    if not s:
        return 0.0
    c = Counter(s)
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())


CONTEXT_BENIGN = re.compile(r"(?i)(sentinel|fake|dummy|fixture|example|redact|placeholder|regex|pattern|grep|gitleaks|detect)")
B64_BODY = re.compile(r"^[A-Za-z0-9+/=]{40,}$")


def scan_text(text: str, rel: str) -> list[SecretHit]:
    hits: list[SecretHit] = []
    is_test_path = bool(re.search(r"(?i)(^|/)(tests?|fixtures?|examples?|docs?)(/|$)|(^|/)test_[^/]*$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$", rel))
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        if len(line) > 5000:
            line = line[:5000]
        for typ, pat, conf in PATTERNS:
            for m in pat.finditer(line):
                val = m.group(1)
                if typ == "private_key_block":
                    fp = sha256_bytes((rel + str(lineno)).encode())[:12]
                    nxt = lines[lineno].strip() if lineno < len(lines) else ""
                    # A real key block has a base64 body on the following line.
                    placeholder = not B64_BODY.match(nxt)
                else:
                    fp = sha256_bytes(val.encode())[:12]
                    placeholder = bool(PLACEHOLDER.search(val))
                if typ == "generic_secret_assignment":
                    if placeholder or entropy(val) < 3.5:
                        continue
                if placeholder and typ != "private_key_block":
                    continue
                benign_ctx = bool(CONTEXT_BENIGN.search(line))
                notes = [n for n, c in (("in test/fixture/example path", is_test_path), ("benign context (pattern/sentinel/fixture)", benign_ctx), ("key header without key body", typ == "private_key_block" and placeholder)) if c]
                likely_live = conf == "HIGH" and not (is_test_path or benign_ctx or (typ == "private_key_block" and placeholder))
                hits.append(SecretHit(rel, lineno, typ, conf if likely_live else "LOW", fp, likely_live, "; ".join(notes)))
    return hits


def scan_tree(root: Path, rel_prefix: str = "") -> dict[str, object]:
    files_scanned = 0
    skipped = 0
    hits: list[SecretHit] = []
    for f in safe_walk(root, max_files=200_000):
        rel = f.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in Path(rel).parts) or f.suffix.lower() in SKIP_SUFFIX:
            skipped += 1
            continue
        try:
            if f.stat().st_size > MAX_BYTES:
                skipped += 1
                continue
            data = f.read_bytes()
        except OSError:
            skipped += 1
            continue
        if b"\x00" in data[:4096]:
            skipped += 1
            continue
        files_scanned += 1
        hits.extend(scan_text(data.decode("utf-8", "replace"), f"{rel_prefix}{rel}"))
    return {"files_scanned": files_scanned, "files_skipped": skipped, "hits": [h.to_dict() for h in hits]}
