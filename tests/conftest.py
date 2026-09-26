from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from szl_evidence.fixturegen import build_fixture

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture()
def valid(tmp_path: Path) -> Path:
    d = tmp_path / "valid"
    build_fixture(d, "valid")
    return d


@pytest.fixture()
def fixture_copy(tmp_path: Path):
    def _make(name: str) -> Path:
        d = tmp_path / name
        build_fixture(d, name)
        return d

    return _make


@pytest.fixture()
def committed() -> Path:
    return FIXTURES


def copytree(src: Path, dst: Path) -> Path:
    shutil.copytree(src, dst)
    return dst
