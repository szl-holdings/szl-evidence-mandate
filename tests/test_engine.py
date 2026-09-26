"""Engine tests 1-25 (Phase 6)."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
import yaml

from szl_evidence.adapters.citations import CrossrefResolver
from szl_evidence.claims import parse_number, quantities_equal, value_matches
from szl_evidence.dependencies import DependencyGraph
from szl_evidence.fixturegen import VARIANTS, _edit_csv
from szl_evidence.invariants import check_invariants
from szl_evidence.models import Validity, sha256_file
from szl_evidence.mutations import run_mutations
from szl_evidence.packaging import package
from szl_evidence.receipts import RECEIPT_STATEMENT, receipt_hash
from szl_evidence.engine_stage import evidence_tokens
from szl_evidence.verifier import verify, verify_receipt


def _non_pass(r):
    return {i["check"] for i in r["invocations"] if i["result"]["status"] != "PASS"}


# 1
def test_01_empty_directory_abstains_exit_2(fixture_copy):
    r = verify(fixture_copy("empty-input"))
    assert r["status"] == "ABSTAIN" and r["exit_code"] == 2
    assert "VACUOUS_PASS" in r["failures"]


# 2
def test_02_valid_input_passes_with_nonempty_evidence(valid):
    r = verify(valid)
    assert r["status"] == "PASS" and r["exit_code"] == 0
    pe = r["pass_evidence"]
    assert pe["rows_examined"] > 0 and pe["checks_executed"] == pe["checks_expected"] == len(r["required_checks"])
    assert pe["checks_failed"] == 0 and pe["checks_abstained"] == 0
    assert all(i["result"]["evidence"] for i in r["invocations"])
    assert r["evidence_manifest"] and pe["evidence_manifest_sha256"] == r["evidence_manifest_sha256"]


# 3
def test_03_pass_impossible_at_zero_rows(valid):
    for f in (valid / "inputs").glob("*.csv"):
        header = f.read_text(encoding="utf-8").splitlines()[0]
        f.write_text(header + "\n", encoding="utf-8")
    r = verify(valid)
    assert r["status"] != "PASS"
    assert r["accounting"]["rows_examined"] == 0


# 4
def test_04_pass_impossible_with_uninvoked_required_check(valid):
    r = verify(valid, skip_checks={"citation_metadata"})
    assert r["status"] == "ERROR" and r["exit_code"] == 3
    assert any(v["invariant"] == "every_required_check_has_terminal_state" for v in r["invariant_violations"])


# 5
def test_05_narrated_verification_is_unverified(fixture_copy):
    r = verify(fixture_copy("narrated-verification"))
    assert r["status"] == "ABSTAIN" and r["exit_code"] == 2
    inv = next(i for i in r["invocations"] if i["check"] == "attested_invocations")
    assert inv["result"]["reason"] == "UNVERIFIED" and "NARRATED_VERIFICATION" in inv["result"]["failures"]


# 6
def test_06_missing_tables_visible(fixture_copy):
    r = verify(fixture_copy("missing-table"))
    assert r["status"] == "ABSTAIN"
    assert r["accounting"]["missing"] == 1
    inv = next(i for i in r["invocations"] if i["check"] == "inputs_present")
    assert "reviews" in inv["result"]["detail"]


# 7
def test_07_partial_execution_not_presentable_as_complete(fixture_copy):
    r = verify(fixture_copy("partial-execution"))
    assert r["status"] == "ABSTAIN" and "PARTIAL_EXECUTION" in r["failures"]
    assert r["pass_evidence"] is None
    assert r["accounting"]["rows_examined"] < r["accounting"]["rows_parsed"]


# 8
def test_08_duplicates_detected(fixture_copy):
    r = verify(fixture_copy("duplicate-row"))
    assert r["status"] == "FAIL" and "duplicate_records:records" in _non_pass(r)


# 9
def test_09_deletions_detected_from_snapshot(fixture_copy):
    r = verify(fixture_copy("deleted-row"))
    inv = next(i for i in r["invocations"] if i["check"] == "snapshot_rows")
    assert inv["result"]["status"] == "FAIL" and inv["result"]["evidence"][0]["deleted"] == ["R5"]


# 10
def test_10_unregistered_claims_detected(fixture_copy):
    r = verify(fixture_copy("unregistered-claim"))
    assert r["status"] == "FAIL"
    inv = next(i for i in r["invocations"] if i["check"] == "claim_value:C4")
    assert "EPHEMERAL_CLAIM" in inv["result"]["failures"]
    # other claims are registered and still pass - they do not excuse C4
    assert next(i for i in r["invocations"] if i["check"] == "claim_value:C1")["result"]["status"] == "PASS"


# 11
def test_11_rounding_cannot_create_false_agreement(fixture_copy):
    ok, _ = quantities_equal("0.8549", "0.8451", "0.001")
    assert not ok
    assert value_matches("0.85", "0.8549")[0] and value_matches("0.85", "0.8451")[0]  # both round to 0.85...
    r = verify(fixture_copy("numeric-rounding"))
    assert r["status"] == "FAIL" and "claim_value:C3" in _non_pass(r)  # ...but equality is refused


# 12
def test_12_thousands_separators_do_not_evade_comparison(fixture_copy):
    assert parse_number("12,480").value == parse_number("12480").value
    with pytest.raises(ValueError):
        parse_number("1,5")  # ambiguous comma is rejected, not guessed
    r = verify(fixture_copy("comma-tokenization"))
    assert r["status"] == "FAIL" and "claim_value:C1" in _non_pass(r)


# 13
def test_13_deterministic_across_hash_seeds(valid, tmp_path):
    digests = set()
    for seed in ("0", "7", "4242"):
        out = tmp_path / f"r{seed}.json"
        env = {**os.environ, "PYTHONHASHSEED": seed, "SOURCE_DATE_EPOCH": "1767225600"}
        p = subprocess.run([sys.executable, "-m", "szl_evidence.cli", "engine", "verify", str(valid), "--receipt", str(out), "--quiet"], env=env, capture_output=True, timeout=300, check=False)
        assert p.returncode == 0, p.stderr.decode()
        digests.add(sha256_file(out))
    assert len(digests) == 1


# 14
def test_14_timezone_mismatch_is_source_mismatch(fixture_copy):
    r = verify(fixture_copy("timezone-mismatch"))
    inv = next(i for i in r["invocations"] if i["check"] == "timestamp_consistency")
    assert inv["result"]["reason"] == "SOURCE_MISMATCH"
    assert inv["result"]["evidence"][0]["same_wallclock_different_offset"] == ["R2"]


# 15
def test_15_reviewer_shortfall_is_protocol_broken(fixture_copy):
    r = verify(fixture_copy("missing-reviewer"))
    inv = next(i for i in r["invocations"] if i["check"] == "reviewer_protocol")
    assert inv["result"]["reason"] == "PROTOCOL_BROKEN" and inv["result"]["evidence"][0]["shortfall"] == {"R4": 1}


# 16
def test_16_citation_fixtures_catch_wrong_authors_and_nonexistent_doi(fixture_copy):
    a = verify(fixture_copy("wrong-authors"))
    b = verify(fixture_copy("nonexistent-doi"))
    ia = next(i for i in a["invocations"] if i["check"] == "citation_metadata")
    ib = next(i for i in b["invocations"] if i["check"] == "citation_metadata")
    assert ia["result"]["reason"] == "SOURCE_MISMATCH"
    assert ib["result"]["status"] == "FAIL" and ib["result"]["evidence"][0]["doi_not_found"] == ["10.5555/szl.fixture.9999"]


# 17
def test_17_network_failure_never_becomes_rejection(valid):
    def boom(request):
        raise httpx.ConnectError("offline")

    resolver = CrossrefResolver(client=httpx.Client(transport=httpx.MockTransport(boom)))
    r = verify(valid, resolver=resolver)
    inv = next(i for i in r["invocations"] if i["check"] == "citation_metadata")
    assert inv["result"]["status"] == "ABSTAIN" and inv["result"]["reason"] == "SOURCE_UNAVAILABLE"
    assert r["status"] == "ABSTAIN"  # never FAIL


# 18
def test_18_mutations_report_detections_and_blind_spots(valid):
    res = run_mutations(valid)
    ids = {m["id"]: m for m in res["results"]}
    assert all(k in ids for k in [f"M{i:02d}" for i in range(1, 20)])
    assert ids["M11"]["status"] == "CORRECTLY_IGNORED"
    assert res["summary"]["detected"] >= 19
    # blind spots are reported, not hidden
    assert set(res["summary"]["blind_spots"]) == {r["id"] for r in res["results"] if r["status"] == "BLIND_SPOT"}
    assert "P03" in res["summary"]["blind_spots"]


# 19
def test_19_upstream_change_marks_descendants_stale(fixture_copy):
    d = fixture_copy("stale-dependency")
    g = DependencyGraph.load(yaml.safe_load((d / "inputs/dag.yaml").read_text(encoding="utf-8")), d)
    ev = g.evaluate()
    assert set(ev["stale"]) == {"admitted-evidence", "analysis-run", "ranking", "figure", "conclusion"}
    assert "source-snapshot" not in ev["stale"] and "design" not in ev["stale"]
    r = verify(d)
    assert r["status"] == "ABSTAIN"  # staleness is not falsity


# 20
def test_20_revalidation_distinguishes_unchanged_from_changed(fixture_copy):
    d = fixture_copy("stale-dependency")
    data = yaml.safe_load((d / "inputs/dag.yaml").read_text(encoding="utf-8"))
    g1 = DependencyGraph.load(copy.deepcopy(data), d)
    g1.evaluate()
    g1.nodes["admitted-evidence"].output_sha256 = "h0"
    r1 = g1.revalidate("admitted-evidence", "h0")
    assert r1["result"] == Validity.REVALIDATED_UNCHANGED.value and r1["descendants_still_pending"] == []
    g2 = DependencyGraph.load(copy.deepcopy(data), d)
    g2.evaluate()
    g2.nodes["admitted-evidence"].output_sha256 = "h0"
    r2 = g2.revalidate("admitted-evidence", "h1")
    assert r2["result"] == Validity.REVALIDATED_CHANGED.value and "conclusion" in r2["descendants_still_pending"]


# 21
def test_21_every_verdict_has_invocation(valid):
    r = verify(valid)
    ids = {i["invocation_id"] for i in r["invocations"]}
    assert all(v["invocation_id"] in ids for v in r["verdicts"])
    bad = copy.deepcopy(r)
    bad["verdicts"].append({**bad["verdicts"][0], "verdict_id": "v-x", "invocation_id": "nope"})
    bad["receipt_sha256"] = receipt_hash(bad)
    assert any(v["invariant"] == "every_verdict_has_invocation" for v in check_invariants(bad))


# 22
def test_22_every_invocation_has_result(valid):
    r = verify(valid)
    assert all(i["result"]["status"] in {"PASS", "FAIL", "ABSTAIN", "ERROR"} for i in r["invocations"])
    bad = copy.deepcopy(r)
    del bad["invocations"][0]["result"]
    assert any(v["invariant"] == "every_invocation_has_result" for v in check_invariants(bad, check_hash=False))


# 23
def test_23_receipt_hash_changes_when_protected_content_changes(valid):
    r = verify(valid)
    h0 = r["receipt_sha256"]
    _edit_csv(valid, "inputs/records.csv", lambda rows: [{**x, "title": x["title"] + "!"} if x["record_id"] == "R1" else x for x in rows])
    r2 = verify(valid)
    assert r2["receipt_sha256"] != h0
    t = copy.deepcopy(r)
    t["status"] = "FAIL"
    assert not verify_receipt(t)["valid"]


# 24
def test_24_no_key_means_unsigned(valid, monkeypatch):
    monkeypatch.delenv("SZL_RECEIPT_ED25519_KEY", raising=False)
    r = verify(valid)
    assert r["signature_state"] == "UNSIGNED" and "signature" not in r
    assert r["receipt_statement"] == RECEIPT_STATEMENT
    monkeypatch.setenv("SZL_RECEIPT_ED25519_KEY", str(valid / "no-such-key.pem"))
    r2 = verify(valid)
    assert r2["signature_state"] == "UNSIGNED" and "signature" not in r2  # unusable key: still honest


# 25
def test_25_controlled_local_packaging_copies_no_protected_inputs(valid, tmp_path):
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["access"] = "controlled-local"
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    out = tmp_path / "pkg"
    idx = package(valid, out)
    assert idx["files_copied"] == 0 and not (out / "corpus").exists()
    assert all(not f["copied"] and len(f["sha256"]) == 64 for f in idx["files"])
    assert {p.name for p in out.iterdir()} == {"receipt.json", "manifest.yaml", "package-index.json"}


def test_committed_fixtures_match_expected(committed):
    for name in VARIANTS:
        exp = yaml.safe_load((committed / name / "expected.yaml").read_text(encoding="utf-8"))
        r = verify(committed / name)
        assert (r["status"], r["exit_code"]) == (exp["expected_status"], exp["expected_exit_code"]), name
        toks = evidence_tokens(r)
        for e in exp["required_evidence"]:
            assert e in toks, (name, e, sorted(toks))


def test_cli_exit_codes_valid_empty_narrated(committed):
    codes = []
    for name in ("valid", "empty-input", "narrated-verification"):
        p = subprocess.run([sys.executable, "-m", "szl_evidence.cli", "engine", "verify", str(committed / name), "--quiet", "--output", str(Path(os.environ.get("TMP", ".")) / "szl-cli-test")], capture_output=True, timeout=300, check=False)
        codes.append(p.returncode)
    assert codes == [0, 2, 2]



def test_out_of_scope_and_not_tested_reasons_are_reachable(valid):
    reg = valid / "inputs/registry.yaml"
    d = yaml.safe_load(reg.read_text(encoding="utf-8"))
    d["claims"]["C2"]["recipe"][0]["op"] = "median"  # not implemented by the interpreter
    reg.write_text(yaml.safe_dump(d), encoding="utf-8")
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["deferred_checks"] = ["citation_metadata"]
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    r = verify(valid)
    reasons = {i["check"]: i["result"]["reason"] for i in r["invocations"]}
    assert reasons["claim_value:C2"] == "OUT_OF_SCOPE"
    assert reasons["citation_metadata"] == "NOT_TESTED" and r["status"] != "PASS"


def test_registry_binds_code_version_and_input_manifest(valid):
    reg = valid / "inputs/registry.yaml"
    d = yaml.safe_load(reg.read_text(encoding="utf-8"))
    d["claims"]["C2"]["code_version"] = "some-other-tool/9"
    d["claims"]["C3"]["input_manifest_sha256"] = "0" * 64
    reg.write_text(yaml.safe_dump(d), encoding="utf-8")
    res = {i["check"]: i["result"] for i in verify(valid)["invocations"]}
    assert res["claim_value:C2"]["status"] == "ABSTAIN" and res["claim_value:C2"]["reason"] == "UNVERIFIED"
    assert res["claim_value:C3"]["status"] == "FAIL" and res["claim_value:C3"]["reason"] == "SOURCE_MISMATCH"


def test_optional_missing_input_is_deferred_and_accounting_closes(valid):
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["inputs"].append({"id": "extra", "path": "inputs/extra.csv", "kind": "table", "required": False})
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    acct = verify(valid)["accounting"]
    assert acct["deferred"] == 1 and acct["missing"] == 0 and acct["input_closure"]["closes"]


def test_determinism_requires_distinct_seed_provenance(valid):
    m = yaml.safe_load((valid / "manifest.yaml").read_text(encoding="utf-8"))
    m["determinism"]["replicates"] = [{"input": "replicate_a", "hash_seed": 0}, {"input": "replicate_b", "hash_seed": 0}]
    (valid / "manifest.yaml").write_text(yaml.safe_dump(m), encoding="utf-8")
    inv = next(i for i in verify(valid)["invocations"] if i["check"] == "output_determinism")
    assert inv["result"]["status"] == "ABSTAIN"


def test_supersede_invalidate_unresolved_transitions(valid):
    data = yaml.safe_load((valid / "inputs/dag.yaml").read_text(encoding="utf-8"))
    g = DependencyGraph.load(copy.deepcopy(data), valid)
    s = g.supersede("ranking", by="figure")
    assert g.nodes["ranking"].state == Validity.SUPERSEDED and "conclusion" in s["descendants_marked_stale"]
    g2 = DependencyGraph.load(copy.deepcopy(data), valid)
    inv = g2.invalidate("analysis-run", "wrong input")
    assert g2.nodes["analysis-run"].state == Validity.INVALIDATED
    assert g2.nodes["conclusion"].state == Validity.STALE_PENDING_REVALIDATION and inv["note"]
    data["nodes"].append({"id": "orphan", "kind": "FIGURE", "version": "1", "depends_on": ["missing-node"]})
    g3 = DependencyGraph.load(data, valid)
    assert g3.mark_unresolved() == ["orphan"] and g3.nodes["orphan"].state == Validity.UNRESOLVED


def test_detection_by_unintended_check_is_not_counted_as_detected(valid):
    res = run_mutations(valid)
    p04 = next(r for r in res["results"] if r["id"] == "P04")
    assert p04["status"] == "DETECTED_INCIDENTALLY" and "P04" in res["summary"]["detected_incidentally"]
