"""Evidence manifest: what inputs are expected and which checks the protocol requires."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import sha256_file
from .safety import UnsafeInput, contained, load_yaml

SUPPORTED_VERSIONS = {"1.0"}
INPUT_KINDS = {"table", "json", "yaml", "jsonl", "blob"}


@dataclass
class InputSpec:
    id: str
    path: str
    kind: str = "table"
    required: bool = True
    key: str | None = None


@dataclass
class Manifest:
    root: Path
    path: Path
    version: str
    name: str
    access: str
    inputs: list[InputSpec]
    sections: dict[str, Any]
    required_checks: list[str] | None
    inputs_dir: str
    ignore: list[str] = field(default_factory=list)
    sha256: str = ""

    def input(self, input_id: str) -> InputSpec | None:
        return next((i for i in self.inputs if i.id == input_id), None)


class ManifestError(Exception):
    pass


def load_manifest(path: str | Path) -> Manifest:
    p = Path(path)
    if p.is_dir():
        p = p / "manifest.yaml"
    if not p.exists():
        raise ManifestError(f"manifest not found: {p}")
    try:
        raw = load_yaml(p)
    except UnsafeInput as e:
        raise ManifestError(str(e)) from e
    if not isinstance(raw, dict):
        raise ManifestError("manifest must be a mapping")
    version = str(raw.get("manifest_version", ""))
    if version not in SUPPORTED_VERSIONS:
        raise ManifestError(f"unsupported manifest_version {version!r}")
    root = p.parent.resolve()
    inputs: list[InputSpec] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for item in raw.get("inputs") or []:
        spec = InputSpec(
            id=str(item["id"]),
            path=str(item["path"]),
            kind=str(item.get("kind", "table")),
            required=bool(item.get("required", True)),
            key=item.get("key"),
        )
        if spec.kind not in INPUT_KINDS:
            raise ManifestError(f"input {spec.id}: unknown kind {spec.kind!r}")
        norm = str(Path(spec.path).as_posix()).lower()
        if spec.id in seen_ids:
            raise ManifestError(f"duplicate input id {spec.id!r}")
        if norm in seen_paths:
            raise ManifestError(f"duplicate manifest path {spec.path!r}")
        try:
            contained(root, spec.path)
        except UnsafeInput as e:
            raise ManifestError(f"input {spec.id}: {e}") from e
        seen_ids.add(spec.id)
        seen_paths.add(norm)
        inputs.append(spec)
    sections = {k: v for k, v in raw.items() if k not in {"manifest_version", "name", "inputs", "required_checks", "access", "inputs_dir", "ignore"}}
    access = str(raw.get("access", "open"))
    if access not in {"open", "controlled-local"}:
        raise ManifestError(f"unknown access class {access!r}")
    return Manifest(
        root=root,
        path=p.resolve(),
        version=version,
        name=str(raw.get("name", p.parent.name)),
        access=access,
        inputs=inputs,
        sections=sections,
        required_checks=raw.get("required_checks"),
        inputs_dir=str(raw.get("inputs_dir", "inputs")),
        ignore=[str(x) for x in raw.get("ignore", [])],
        sha256=sha256_file(p),
    )
