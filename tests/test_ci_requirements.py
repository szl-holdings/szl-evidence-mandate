"""The hash-locked CI install stays in step with pyproject.toml.

test.yml installs every distribution from requirements/ci/test.txt with --require-hashes and then
installs the package with --no-deps, so pip never compares the lock with what pyproject.toml
declares. These tests do: test.in repeats the pyproject specifiers, every pin in the compiled lock is
hashed and inside them, the lock was compiled the documented way, the workflow installs nothing
unhashed, and the advertised Python classifiers are the versions CI actually tests.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import yaml
from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / "requirements" / "ci"
WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
LOCK_EXTRAS = ("dev", "sign", "openislet")  # the extras test.yml needs (lint, signing, OpenIslet tests)
_PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)")


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _squash(spec: str) -> str:
    return re.sub(r"\s+", "", spec)


def _flatten(command: str) -> str:
    """A shell command as one line: comment markers and backslash continuations removed."""
    return " ".join(command.replace("\\", " ").replace("#", " ").split())


def _in_requirements() -> list[str]:
    lines = ((CI / "test.in").read_text(encoding="utf-8")).splitlines()
    return [x for x in (line.split("#", 1)[0].strip() for line in lines) if x]


def _pins() -> dict[str, list[tuple[str, int]]]:
    """Normalized distribution -> [(pinned version, number of sha256 hashes)] (a universal lock may fork)."""
    pins: dict[str, list[tuple[str, int]]] = {}
    for block in re.split(r"\n(?=\S)", (CI / "test.txt").read_text(encoding="utf-8")):
        m = _PIN.match(block)
        if m:
            pins.setdefault(_norm(m.group(1)), []).append((m.group(2), block.count("--hash=sha256:")))
    return pins


def test_in_file_repeats_the_pyproject_specifiers():
    project = _pyproject()
    declared = list(project["project"]["dependencies"])
    for extra in LOCK_EXTRAS:
        declared += project["project"]["optional-dependencies"][extra]
    declared += project["build-system"]["requires"]
    assert sorted(map(_squash, _in_requirements())) == sorted(set(map(_squash, declared)))


def test_every_pin_is_hashed_and_satisfies_its_specifier():
    pins = _pins()
    assert pins, "test.txt pins nothing"
    for dist, entries in pins.items():
        for version, hashes in entries:
            assert hashes > 0, f"test.txt pins {dist}=={version} without a hash"
    for line in _in_requirements():
        req = Requirement(line)
        entries = pins.get(_norm(req.name))
        assert entries, f"test.txt does not pin {req.name}; recompile it (command in test.in)"
        for version, _ in entries:
            assert req.specifier.contains(Version(version), prereleases=True), f"test.txt pins {req.name}=={version}, outside {line!r}"


def test_lock_was_compiled_with_the_documented_command():
    documented = re.search(r"#\s+(uv pip compile .*?-o requirements/ci/test\.txt)", (CI / "test.in").read_text(encoding="utf-8"), re.S)
    recorded = re.search(r"#\s+(uv pip compile .*?-o requirements/ci/test\.txt)", (CI / "test.txt").read_text(encoding="utf-8"))
    assert documented and recorded
    assert _flatten(documented.group(1)) == _flatten(recorded.group(1))
    assert "--universal" in recorded.group(1) and "--generate-hashes" in recorded.group(1)  # Windows + every matrix Python


def test_workflow_installs_only_from_the_hashed_lock():
    text = WORKFLOW.read_text(encoding="utf-8")
    installs = re.findall(r"pip\s+install\b[^\n]*", text)
    assert any("--require-hashes" in c and "-r requirements/ci/test.txt" in c for c in installs)
    for command in installs:
        assert "--require-hashes" in command or "--no-deps" in command, command


def test_classifiers_match_the_tested_python_versions():
    matrix = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["test"]["strategy"]["matrix"]["python"]
    classified = [c.rsplit("::", 1)[1].strip() for c in _pyproject()["project"]["classifiers"] if re.fullmatch(r"Programming Language :: Python :: 3\.\d+", c)]
    assert sorted(matrix) == sorted(classified)


def test_test_extra_is_pytest_plus_the_sign_and_openislet_extras():
    extras = _pyproject()["project"]["optional-dependencies"]
    pytest_spec = [r for r in extras["dev"] if Requirement(r).name == "pytest"]
    assert sorted(extras["test"]) == sorted(pytest_spec + extras["sign"] + extras["openislet"])
