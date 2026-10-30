#!/usr/bin/env python3
"""Build a CycloneDX SBOM from the one wheel the release gate accepted.

The release gate leaves its staging copy under dist/stage-<package>/.
Only a wheel outside those directories is eligible. Zero or several
eligible wheels is a hard failure. This file is not the release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.parse
import urllib.request
import zipfile
from email.parser import HeaderParser
from pathlib import Path

SCHEMA_HOSTS = {"cyclonedx.org", "www.cyclonedx.org"}
INSTALLER_NAMES = {"pip", "setuptools", "wheel"}
EXCLUSIONS = [
    "Optional extras are not installed, so their dependencies are absent.",
    "The isolated build environment is not the SBOM venv.",
    "Wheels under a stage-* directory are release-gate staging copies and are not installed.",
    "pip, setuptools, and wheel are recorded when the SBOM venv contains the installer. They are not project dependencies.",
    "The component count is the number of distributions cyclonedx-py recorded in that venv. It is not proof of complete dependency coverage.",
    "cyclonedx-py environment edges can differ from Requires-Dist. Differences are listed on the receipt and are not coverage proof.",
]


class SbomWheelSelectionError(Exception):
    def __init__(self, eligible: list[Path], excluded: list[Path], dist: Path) -> None:
        self.eligible = eligible
        self.excluded = excluded
        eligible_names = ", ".join(_rel(dist, path) for path in eligible) or "<none>"
        excluded_names = ", ".join(_rel(dist, path) for path in excluded) or "<none>"
        super().__init__(
            "expected exactly one gated wheel, "
            f"found {len(eligible)} eligible ({eligible_names}) "
            f"and {len(excluded)} stage-* excluded ({excluded_names})"
        )


class SbomVerificationError(Exception):
    pass


def _rel(dist: Path, wheel: Path) -> str:
    return wheel.relative_to(dist).as_posix()


def _is_stage_wheel(dist: Path, wheel: Path) -> bool:
    return any(part.startswith("stage-") for part in wheel.relative_to(dist).parts[:-1])


def select_gated_wheel(dist: Path) -> Path:
    """Return the single eligible wheel. Never choose among several."""
    eligible: list[Path] = []
    excluded: list[Path] = []
    for wheel in sorted(dist.rglob("*.whl")):
        if _is_stage_wheel(dist, wheel):
            excluded.append(wheel)
        else:
            eligible.append(wheel)
    if len(eligible) != 1:
        raise SbomWheelSelectionError(eligible, excluded, dist)
    return eligible[0]


def _dependency_name(spec: str) -> str:
    base = spec.split("[", 1)[0]
    for separator in ("=", "<", ">", "!", "~", ";", " "):
        base = base.split(separator, 1)[0]
    return base.strip().replace("_", "-").lower()


def _ref_name(ref: str) -> str:
    return ref.split("==", 1)[0].replace("_", "-").lower()


def _wheel_identity(wheel: Path) -> tuple[str, str]:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        message = HeaderParser().parsestr(archive.read(metadata_name).decode("utf-8", "replace"))
    name = message["Name"]
    version = message["Version"]
    if not name or not version:
        raise SbomVerificationError(f"{wheel.name} METADATA has no Name or Version")
    return name, version


def _venv_python(venv: Path) -> Path:
    folder = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return venv / folder / executable


def _installed_requires(python: Path) -> dict[str, dict]:
    probe = (
        "import importlib.metadata, json; "
        "out = {};\n"
        "for dist in importlib.metadata.distributions():\n"
        "    out[dist.metadata['Name']] = {'version': dist.version, 'requires': dist.requires or []}\n"
        "print(json.dumps(out))"
    )
    # The probe is one module invocation. Keep it as an argument list, not a shell.
    completed = subprocess.run(
        [str(python), "-I", "-c", probe],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def _marked_requires(requires: list[str]) -> set[str]:
    from packaging.requirements import Requirement

    names: set[str] = set()
    for raw in requires:
        requirement = Requirement(raw)
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        names.add(_dependency_name(requirement.name))
    return names


def validate_declared_schema(bom: dict) -> str:
    declared = bom.get("$schema")
    if not isinstance(declared, str) or not declared.endswith("/bom-1.6.schema.json"):
        raise SbomVerificationError(f"SBOM schema is not bom-1.6: {declared!r}")
    if bom.get("specVersion") != "1.6" or bom.get("bomFormat") != "CycloneDX":
        raise SbomVerificationError(
            f"SBOM identity is {bom.get('bomFormat')} {bom.get('specVersion')}, expected CycloneDX 1.6"
        )
    parsed = urllib.parse.urlparse(declared)
    if parsed.hostname not in SCHEMA_HOSTS:
        raise SbomVerificationError(f"refusing SBOM schema host {parsed.hostname!r}")
    secure = urllib.parse.urlunparse(parsed._replace(scheme="https"))
    request = urllib.request.Request(secure, headers={"User-Agent": "szl-pypi-sbom/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        schema = json.load(response)
    import jsonschema

    jsonschema.validators.validator_for(schema)(schema).validate(bom)
    return secure


def _reject_private_material(text: str, wheel: Path) -> None:
    forbidden = (
        "RUNNER_TEMP",
        "/home/runner",
        "/Users/",
        "\\Users\\",
        "AppData",
        "BEGIN PRIVATE",
        "BEGIN RSA",
        str(wheel),
        str(wheel.parent),
    )
    for needle in forbidden:
        if needle and needle in text:
            raise SbomVerificationError(f"SBOM contains forbidden material matching {needle!r}")
    for pattern in (r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"pypi-[A-Za-z0-9]{16,}"):
        if re.search(pattern, text):
            raise SbomVerificationError(f"SBOM contains a credential-shaped value matching {pattern}")


def _edge_differences(bom: dict, installed: dict[str, dict]) -> list[dict]:
    by_name = {_dependency_name(name): value for name, value in installed.items()}
    differences = []
    for edge in bom.get("dependencies") or []:
        ref = edge.get("ref")
        if ref == "root-component":
            continue
        name = _ref_name(str(ref))
        recorded = by_name.get(name)
        if recorded is None:
            differences.append({"component": name, "missing_from_venv": True})
            continue
        expected = _marked_requires(recorded.get("requires") or [])
        actual = {_ref_name(item) for item in edge.get("dependsOn") or []}
        sbom_only = sorted(actual - expected)
        requires_only = sorted(expected - actual)
        if sbom_only or requires_only:
            differences.append(
                {"component": name, "sbom_only": sbom_only, "requires_dist_only": requires_only}
            )
    return differences


def generate(dist: Path, pyproject: Path, outdir: Path, venv: Path) -> dict:
    wheel = select_gated_wheel(dist)
    wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    wheel_name, wheel_version = _wheel_identity(wheel)
    with pyproject.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    package = project["name"]
    version = project["version"]
    if (wheel_name, wheel_version) != (package, version):
        raise SbomVerificationError(
            f"wheel METADATA {wheel_name}=={wheel_version} does not match pyproject {package}=={version}"
        )

    if venv.exists():
        shutil.rmtree(venv)
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    python = _venv_python(venv)
    subprocess.run(
        [str(python), "-I", "-m", "pip", "install", "--disable-pip-version-check", "-q", str(wheel)],
        check=True,
    )
    outdir.mkdir(parents=True, exist_ok=True)
    sbom_path = outdir / f"{package}.cdx.json"
    subprocess.run(
        [
            sys.executable, "-m", "cyclonedx_py", "environment", str(venv),
            "--mc-type", "library",
            "--pyproject", str(pyproject),
            "--output-reproducible",
            "--of", "JSON",
            "--output-file", str(sbom_path),
            "--validate",
        ],
        check=True,
    )
    bom = json.loads(sbom_path.read_text(encoding="utf-8"))
    component = bom["metadata"]["component"]
    if component.get("name") != package or component.get("version") != version:
        raise SbomVerificationError(
            f"SBOM component {component.get('name')}=={component.get('version')} "
            f"does not match wheel {package}=={version}"
        )
    if component.get("type") != "library":
        raise SbomVerificationError(f"SBOM component type is {component.get('type')!r}, expected library")
    component["hashes"] = [{"alg": "SHA-256", "content": wheel_sha}]
    properties = [item for item in component.get("properties") or [] if item.get("name") != "szl:gated-wheel-filename"]
    properties.append({"name": "szl:gated-wheel-filename", "value": wheel.name})
    component["properties"] = properties
    for item in bom.get("components") or []:
        if not item.get("name") or not item.get("version"):
            raise SbomVerificationError(f"component is missing name or version: {item.get('bom-ref')!r}")
    schema_url = validate_declared_schema(bom)

    text = json.dumps(bom, indent=2) + "\n"
    _reject_private_material(text, wheel)
    sbom_path.write_text(text, encoding="utf-8", newline="\n")
    sbom_sha = hashlib.sha256(sbom_path.read_bytes()).hexdigest()

    installed = _installed_requires(python)
    direct = sorted({_dependency_name(spec) for spec in project.get("dependencies") or []})
    root_edge = next((edge for edge in bom.get("dependencies") or [] if edge.get("ref") == "root-component"), None)
    if root_edge is None:
        raise SbomVerificationError("SBOM dependency graph has no root-component edge")
    root_names = sorted({_ref_name(item) for item in root_edge.get("dependsOn") or []})
    missing_direct = sorted(set(direct) - set(root_names))
    if missing_direct:
        raise SbomVerificationError(f"root SBOM dependencies omit declared dependencies {missing_direct}")
    known_refs = {item.get("bom-ref") for item in bom.get("components") or []} | {"root-component"}
    for edge in bom.get("dependencies") or []:
        if edge.get("ref") not in known_refs:
            raise SbomVerificationError(f"dangling dependency ref {edge.get('ref')!r}")
        for child in edge.get("dependsOn") or []:
            if child not in known_refs:
                raise SbomVerificationError(f"dangling dependency target {child!r}")

    installed_names = {_dependency_name(name) for name in installed}
    component_names = {_dependency_name(item["name"]) for item in bom.get("components") or []}
    installers = sorted(component_names & INSTALLER_NAMES)
    receipt = {
        "receipt_schema": "szl.cyclonedx-sbom-receipt/v1",
        "package": package,
        "version": version,
        "wheel_filename": wheel.name,
        "wheel_sha256": wheel_sha,
        "sbom_filename": sbom_path.name,
        "sbom_sha256": sbom_sha,
        "bom_format": "CycloneDX",
        "spec_version": "1.6",
        "schema_url": schema_url,
        "component_count": len(bom.get("components") or []),
        "declared_direct_dependencies": direct,
        "root_dependency_names": root_names,
        "installer_components": installers,
        "installed_not_in_sbom": sorted(installed_names - component_names - {_dependency_name(package)}),
        "requires_dist_edge_differences": _edge_differences(bom, installed),
        "exclusions": EXCLUSIONS,
        "github_sha": os.environ.get("GITHUB_SHA"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_ref": os.environ.get("GITHUB_REF"),
    }
    receipt_path = outdir / f"{package}.sbom-receipt.json"
    receipt_text = json.dumps(receipt, indent=2) + "\n"
    _reject_private_material(receipt_text, wheel)
    receipt_path.write_text(receipt_text, encoding="utf-8", newline="\n")
    print(json.dumps({"wheel_sha256": wheel_sha, "sbom_sha256": sbom_sha, "wheel_filename": wheel.name}))
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select-wheel")
    select.add_argument("--dist", type=Path, required=True)
    build = commands.add_parser("generate")
    build.add_argument("--dist", type=Path, required=True)
    build.add_argument("--pyproject", type=Path, required=True)
    build.add_argument("--outdir", type=Path, required=True)
    build.add_argument("--venv", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "select-wheel":
            print(select_gated_wheel(args.dist))
        else:
            generate(args.dist, args.pyproject, args.outdir, args.venv)
    except SbomWheelSelectionError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2
    except SbomVerificationError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
