"""Corpus packaging. ``open`` corpora copy inputs; ``controlled-local`` corpora copy only
hashes and the receipt, never the protected inputs themselves."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .manifest import load_manifest
from .models import sha256_file
from .receipts import write_receipt
from .safety import UnsafeInput, contained, safe_walk
from .verifier import verify


def package(manifest_path: str | Path, output: str | Path) -> dict[str, Any]:
    m = load_manifest(manifest_path)
    out = Path(output)
    if out.exists() and any(out.iterdir()):
        raise UnsafeInput(f"refusing to package into non-empty directory {out}")
    if m.root in out.resolve().parents or out.resolve() == m.root:
        raise UnsafeInput("package output must not be inside the corpus being packaged")
    out.mkdir(parents=True, exist_ok=True)
    receipt = verify(m.path)
    write_receipt(receipt, out / "receipt.json")
    shutil.copy2(m.path, out / "manifest.yaml")
    files: list[dict[str, Any]] = []
    copied = 0
    for f in safe_walk(m.root):
        rel = f.relative_to(m.root).as_posix()
        if rel in ("manifest.yaml",):
            continue
        entry = {"path": rel, "sha256": sha256_file(f), "bytes": f.stat().st_size}
        if m.access == "open":
            dest = contained(out / "corpus", rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            entry["copied"] = True
            copied += 1
        else:
            entry["copied"] = False
        files.append(entry)
    index = {
        "access": m.access,
        "license": "NOASSERTION",
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "files": files,
        "files_copied": copied,
        "note": "controlled-local: inputs are referenced by hash only" if m.access != "open" else "open corpus: inputs copied",
    }
    import json

    (out / "package-index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return index
