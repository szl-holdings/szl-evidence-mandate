"""Phase 7 hardening tests."""

from __future__ import annotations

import csv
import io
import json
import os
import zipfile
from pathlib import Path

import pytest
import yaml

from szl_evidence.manifest import ManifestError, load_manifest
from szl_evidence.cli import _print
from szl_evidence.models import sha256_bytes
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


# Synthetic markers only: these tests never read credentials or provider data.
OUTPUT_MARKERS = [
    "ghp_" + "A" * 36,
    "github_pat_" + "B" * 30,
    "hf_" + "C" * 34,
    "sk-" + "D" * 30,
    "AKIA" + "E" * 16,
    "xoxb-" + "F" * 20,
    "Authorization: Bearer synthetic-test-value",
]


@pytest.mark.parametrize("marker", OUTPUT_MARKERS)
@pytest.mark.parametrize("kind", ["text", "json", "csv"])
def test_report_output_redacts_credentials_without_corrupting_format(tmp_path, marker, kind):
    writer = ReportWriter(tmp_path)
    if kind == "text":
        path = writer.text("report.txt", f"finding: {marker}\nstatus: HOLD\n")
    elif kind == "json":
        path = writer.json("report.json", {"nested": [marker], "status": "HOLD"})
    else:
        path = writer.csv("report.csv", ["finding", "status"], [[marker, "HOLD"]])
    data = path.read_bytes()
    text = data.decode("utf-8")
    assert marker not in text and "[REDACTED]" in text
    assert writer.hashes[path.name] == sha256_bytes(data)
    if kind == "json":
        assert json.loads(text) == {"nested": [redact(marker)], "status": "HOLD"}
    elif kind == "csv":
        assert list(csv.reader(io.StringIO(text))) == [["finding", "status"], [redact(marker), "HOLD"]]


@pytest.mark.parametrize("marker", OUTPUT_MARKERS)
def test_cli_output_redacts_credentials_and_preserves_json(marker, capsys):
    payload = {"nested": [marker], "status": "HOLD", "receipt_sha256": "a" * 64}
    original = json.dumps(payload, sort_keys=True)
    _print(payload)
    output = capsys.readouterr().out
    assert marker not in output
    assert json.loads(output) == {"nested": [redact(marker)], "status": "HOLD", "receipt_sha256": "a" * 64}
    assert json.dumps(payload, sort_keys=True) == original


def test_cli_quiet_output_stays_empty(capsys):
    _print({"finding": OUTPUT_MARKERS[0]}, quiet=True)
    assert capsys.readouterr().out == ""


def test_structured_reports_scrub_keys_and_values_without_mutating_receipt(tmp_path):
    marker = OUTPUT_MARKERS[0]
    payload = {marker: {"finding": marker, "receipt_sha256": "f" * 64}, "status": "FAIL", "count": 2}
    original = json.dumps(payload, sort_keys=True)
    writer = ReportWriter(tmp_path)
    result = json.loads(writer.json("report.json", payload).read_text(encoding="utf-8"))
    assert result == {"[REDACTED]": {"finding": "[REDACTED]", "receipt_sha256": "f" * 64}, "status": "FAIL", "count": 2}
    assert json.dumps(payload, sort_keys=True) == original


@pytest.mark.parametrize("sink", ["report", "cli"])
def test_redacted_json_key_collision_fails_closed(tmp_path, sink):
    payload = {OUTPUT_MARKERS[0]: "first", OUTPUT_MARKERS[1]: "second"}
    with pytest.raises(ValueError, match="output key collision"):
        if sink == "report":
            ReportWriter(tmp_path).json("report.json", payload)
        else:
            _print(payload)
    assert not (tmp_path / "report.json").exists()


def test_csv_scrubs_cells_before_escaping_and_preserves_none(tmp_path):
    writer = ReportWriter(tmp_path)
    marker = "Authorization: Bearer synthetic-test-value"
    path = writer.csv("report.csv", ["finding", "detail", "empty"], [[marker, 'comma, quote " and\nnewline', None]])
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    assert rows == [["finding", "detail", "empty"], [redact(marker), 'comma, quote " and\nnewline', ""]]


def test_json_report_preserves_unicode_private_and_host_scrubbing(tmp_path):
    writer = ReportWriter(tmp_path, redact_names=["secret-repo"])
    path = writer.json("report.json", {"note": "café secret-repo", "host": r"C:\Users\alice\file", "count": 3})
    text = path.read_text(encoding="utf-8")
    assert "café" in text and "alice" not in text and "secret-repo" not in text
    assert json.loads(text) == {"note": "café <private>", "host": r"<home>\file", "count": 3}


def test_duplicate_normalized_json_names_fail_without_overwriting_report(tmp_path):
    writer = ReportWriter(tmp_path)
    path = writer.text("report.json", "prior report\n")
    original_hash = writer.hashes["report.json"]
    with pytest.raises(ValueError, match="^output key collision$"):
        writer.json("report.json", {"nested": {"1": "first", 1: "second"}})
    assert path.read_bytes() == b"prior report\n"
    assert writer.hashes["report.json"] == original_hash


def test_private_json_key_collision_is_not_silently_lost(tmp_path):
    writer = ReportWriter(tmp_path, redact_names=["private-one", "private-two"])
    with pytest.raises(ValueError, match="^output key collision$"):
        writer.json("report.json", {"private-one": 1, "private-two": 2})
    assert not (tmp_path / "report.json").exists()


def test_cli_formatting_and_default_string_compatibility(capsys):
    payload = {"path": Path("ordinary/file"), "unicode": "café", "nested": (None, True, 1.25)}
    _print(payload)
    assert capsys.readouterr().out == json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
