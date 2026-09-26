"""Phase 7 hardening tests."""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import pytest
import yaml

from szl_evidence.manifest import ManifestError, load_manifest
from szl_evidence.reports import ReportWriter
from szl_evidence.safety import UnsafeInput, check_archive, check_size, contained, isolated_env, redact, run_argv, safe_walk
from szl_evidence.verifier import verify


def test_path_traversal_rejected(tmp_path):
    with pytest.raises(UnsafeInput):
        contained(tmp_path, "../etc/passwd")
    with pytest.raises(UnsafeInput):
        contained(tmp_path, "/abs/path")


def test_manifest_with_traversal_input_is_refused(valid):
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["inputs"][0]["path"] = "../../outside.csv"
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    r = verify(valid)
    assert r["status"] == "ERROR" and "escapes root" in r["error"]


def test_duplicate_manifest_paths_refused(valid):
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["inputs"].append({**m["inputs"][0], "id": "records_again"})
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    with pytest.raises(ManifestError, match="duplicate manifest path"):
        load_manifest(valid)


def test_malformed_yaml_is_error_not_pass(valid):
    (valid / "manifest.yaml").write_text("manifest_version: '1.0'\ninputs: [\n", encoding="utf-8")
    r = verify(valid)
    assert r["status"] == "ERROR" and r["exit_code"] == 3


def test_malformed_json_input_is_not_pass(valid):
    (valid / "inputs/doi_registry.json").write_text("{not json", encoding="utf-8")
    r = verify(valid)
    assert r["status"] != "PASS" and r["accounting"]["failed"] == 1


@pytest.mark.skipif(os.name == "nt" and not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_symlink_escape_rejected(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "root"
    root.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation not permitted on this host")
    with pytest.raises(UnsafeInput):
        contained(root, "link/file.csv")
    assert safe_walk(root) == []


def test_archive_bomb_and_traversal_rejected(tmp_path):
    bomb = tmp_path / "bomb.zip"
    with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("big.txt", b"0" * 5_000_000)
    with pytest.raises(UnsafeInput, match="bomb"):
        check_archive(bomb)
    trav = tmp_path / "trav.zip"
    with zipfile.ZipFile(trav, "w") as z:
        z.writestr("../evil.txt", "x")
    with pytest.raises(UnsafeInput, match="traversal"):
        check_archive(trav)
    _ = io


def test_oversized_and_unexpected_file_counts(tmp_path):
    f = tmp_path / "big.bin"
    f.write_bytes(b"x" * 1024)
    with pytest.raises(UnsafeInput):
        check_size(f, limit=10)
    for i in range(12):
        (tmp_path / f"f{i}").write_text("x")
    with pytest.raises(UnsafeInput, match="file count"):
        safe_walk(tmp_path, max_files=5)


def test_hash_mismatch_detected(valid):
    reg = valid / "inputs/registry.yaml"
    d = yaml.safe_load(reg.read_text(encoding="utf-8"))
    for c in d["claims"].values():
        c["output_sha256"] = "0" * 64
    reg.write_text(yaml.safe_dump(d), encoding="utf-8")
    r = verify(valid)
    assert r["status"] == "FAIL" and "SOURCE_MISMATCH" in r["reason_codes"]


def test_no_shell_strings_and_injection_inert(tmp_path):
    with pytest.raises(UnsafeInput):
        run_argv("echo hi; rm -rf /")  # type: ignore[arg-type]
    marker = tmp_path / "pwned"
    r = run_argv(["python", "-c", "import sys; print(sys.argv[1])", f"x; touch {marker}"])
    assert r["exit_code"] == 0 and not marker.exists()


def test_secrets_redacted_from_output():
    s = "Authorization: Bearer ghp_" + "A" * 36 + " and hf_" + "b" * 34
    red = redact(s)
    assert "ghp_" + "A" * 36 not in red and "hf_" + "b" * 34 not in red


def test_isolated_env_carries_no_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "secret-value")
    monkeypatch.setenv("HF_TOKEN", "secret-value")
    env = isolated_env(tmp_path)
    assert "GITHUB_TOKEN" not in env and "HF_TOKEN" not in env and env["HOME"] == str(tmp_path)


def test_writer_refuses_outside_output_dir(tmp_path):
    w = ReportWriter(tmp_path / "out")
    with pytest.raises(UnsafeInput):
        w.text("../escape.md", "x")
    assert not (tmp_path / "escape.md").exists()
    _ = Path


def test_public_writer_scrubs_private_names_and_host_paths(tmp_path):
    w = ReportWriter(tmp_path, redact_names=["secret-repo", "SZLHOLDINGS/private-ds"])
    p = w.text("r.md", r"see secret-repo and szl-holdings/secret-repo and SZLHOLDINGS/private-ds; not secret-repository; C:\Users\alice\AppData\Local\Temp\x")
    text = p.read_text(encoding="utf-8")
    assert "secret-repo " not in text and "private-ds" not in text and "alice" not in text
    assert "secret-repository" in text and text.count("<private>") == 3 and "<tmp>" in text
