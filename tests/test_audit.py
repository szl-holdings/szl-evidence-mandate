"""Audit tests 26-40 (Phase 6). All network access is mocked."""

from __future__ import annotations

import json
import random
import string
from datetime import datetime, timezone
from pathlib import Path

import httpx

from szl_evidence.adapters.http import CachedClient, paginate
from szl_evidence.audit import claims_extract, findings, reconcile, render
from szl_evidence.audit.common import FindingSink
from szl_evidence.audit.functional import run_paired_verifier
from szl_evidence.audit.github import GitHubCollector, scorecard
from szl_evidence.audit.pipeline import save
from szl_evidence.audit.secrets_scan import scan_tree
from szl_evidence.audit.zoomout import Recommendation, evaluate_recommendation
from szl_evidence.reports import HEADER_FIELDS

NOW = datetime(2026, 9, 25, tzinfo=timezone.utc)


def mock_client(handler, tmp_path: Path | None = None) -> CachedClient:
    return CachedClient(tmp_path, transport=httpx.MockTransport(handler), max_retries=0, surface="test")


# 26
def test_26_pagination_retrieves_all_pages(tmp_path):
    pages = {1: [{"n": 1}, {"n": 2}], 2: [{"n": 3}], 3: [{"n": 4}, {"n": 5}]}

    def h(req: httpx.Request) -> httpx.Response:
        p = int(req.url.params.get("page", "1"))
        link = f'<https://api.example/items?page={p + 1}>; rel="next"' if p < 3 else ""
        return httpx.Response(200, json=pages[p], headers={"link": link} if link else {})

    items, meta = paginate(mock_client(h, tmp_path), "https://api.example/items", {"page": 1})
    assert [i["n"] for i in items] == [1, 2, 3, 4, 5] and meta["pages"] == 3 and meta["denominator_state"] == "OBSERVED"
    cached = list((tmp_path / "test").glob("*.json"))
    assert len(cached) == 3 and all("retrieved_at" in json.loads(c.read_text()) and "body_sha256" in json.loads(c.read_text()) for c in cached)


# 27
def test_27_rate_limit_is_source_unavailable_not_a_finding():
    def h(req):
        return httpx.Response(403, json={"message": "API rate limit exceeded"}, headers={"x-ratelimit-remaining": "0"})

    c = mock_client(h)
    r = c.get("https://api.github.com/repos/o/r/actions/workflows")
    assert r.unavailable
    col = GitHubCollector(c, "o", authenticated=False)
    val = col._val(r)
    assert val["state"] == "SOURCE_UNAVAILABLE"
    repo = {"name": "r", "description": "d", "pushed_at": "2026-09-01T00:00:00Z", "default_branch": "main"}
    sc = scorecard(repo, {"workflows": val, "latest_runs": val, "releases": val}, None, None, None, NOW)
    assert sc["ci"]["state"] == "NOT_TESTED" and sc["release_integrity"]["state"] == "NOT_TESTED"
    items, meta = paginate(c, "https://api.github.com/orgs/o/repos")
    assert items == [] and meta["denominator_state"] == "UNAVAILABLE"


# 28
def test_28_unreachable_repo_is_not_tested_never_pass():
    repo = {"name": "r", "description": "x", "pushed_at": "2026-09-01T00:00:00Z", "license": None}
    sc = scorecard(repo, {"workflows": [], "releases": []}, None, None, None, NOW)
    for axis in ("provenance", "tests", "security_posture", "docs", "honest_scoping", "evidence_boundary", "cross_links"):
        assert sc[axis]["state"] == "NOT_TESTED", axis
    assert all(v["state"] != "PASS" for k, v in sc.items() if k not in ("maintenance",))


# 29
def test_29_secret_scanner_detects_planted_token_never_prints_value(tmp_path):
    rnd = random.Random(7)
    token = "ghp_" + "".join(rnd.choice(string.ascii_letters + string.digits) for _ in range(36))
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "config.py").write_text(f'GITHUB = "{token}"\n', encoding="utf-8")
    res = scan_tree(tmp_path)
    hits = res["hits"]
    assert len(hits) == 1 and hits[0]["type"] == "github_token" and hits[0]["likely_live"] and hits[0]["path"] == "src/config.py"
    assert token not in json.dumps(res)
    w = render.ReportWriter(tmp_path / "out")
    render.r06(w, {"files": {"repo": {"secrets": res, "code_risks": {}}}, "gh": {"repos": [{"name": "repo", "detail": {}}]}})
    assert token not in (tmp_path / "out" / "06-security-findings.md").read_text(encoding="utf-8")


# 30
def test_30_claim_extractor_finds_planted_claims():
    readme = "# X\n\nWe publish **21 public Spaces, 46 models, 35 datasets.** Observed 2026-09-10T03:20:41Z.\n\nDoctrine v11 (LOCKED): 749 declarations / 14 axioms / 163 sorries; trust ceiling 0.97.\n\n```\n99 models in code block\n```\nDOI 10.5281/zenodo.19944926\n"
    cl = claims_extract.extract(readme, "fixture/README.md")
    types = [(c.claim_type, c.value, c.unit) for c in cl]
    for t in [("inventory_count", "21", "spaces"), ("inventory_count", "46", "models"), ("inventory_count", "35", "datasets"), ("lean_count", "749", "declarations"), ("lean_count", "14", "axioms"), ("lean_count", "163", "sorries"), ("doctrine_version", "11", "")]:
        assert t in types, t
    assert any(c.claim_type == "trust_ceiling" and c.value == "0.97" for c in cl)
    assert any(c.claim_type == "locked_marker" for c in cl) and any(c.claim_type == "doi" for c in cl)
    assert not any(c.value == "99" for c in cl)  # code blocks are skipped


# 31
def test_31_drifted_dated_observation_is_stale_not_contradicted():
    cl = claims_extract.extract("Public estate: **21 public Spaces**. Observed 2026-09-10T03:20:41Z.", "f")
    out = claims_extract.verify_claims(cl, {"public_counts": {"spaces": 22}, "public_counts_at": "2026-09-25T00:00:00Z"}, "2026-09-25T00:00:00Z")
    c = next(x for x in out if x.claim_type == "inventory_count")
    assert c.verdict == "STALE" and "2026-09-10" in c.evidence and "2026-09-25" in c.evidence
    undated = claims_extract.verify_claims(claims_extract.extract("The public estate has 21 public Spaces.", "g"), {"public_counts": {"spaces": 22}}, "now")
    assert next(x for x in undated if x.claim_type == "inventory_count").verdict == "CONTRADICTED"


# 32
def test_32_missing_license_file_with_declared_metadata_is_contradicted():
    repo = {"name": "r", "description": "d", "pushed_at": "2026-09-01T00:00:00Z", "license": {"spdx_id": "MIT"}}
    files = {"presence": {"LICENSE": None, "README": "README.md"}, "declared_package_licenses": {}, "license_file_kind": None, "lockfiles": [], "dependency_pinning": {}, "manifests": {}, "containers": [], "test_files": 0, "test_functions_static": 0, "tests_dirs": [], "secrets": {"hits": []}, "code_risks": {}, "path_traversal_defense_seen": False, "readme_text": ""}
    sc = scorecard(repo, {"workflows": []}, files, None, None, NOW)
    assert sc["license"]["state"] == "FAIL" and "CONTRADICTED" in sc["license"]["evidence"]


def _space(state="DID_NOT_LOAD", private=False):
    return {"kind": "space", "id": "ORG/s", "private": private, "files": [], "card": {"axes": {}}, "functional": {"runtime_state": "RUNNING", "runtime_stage_raw": "RUNNING", "http": {"state": state, "probes": [{"path": "/", "status": 503, "latency_ms": 5}]}}}


# 33
def test_33_dead_space_is_critical():
    s = FindingSink("huggingface")
    findings.hf_findings(s, {"artifacts": [_space()], "completed_at": "t"}, {"corpora": []})
    assert [f.severity for f in s.items] == ["CRITICAL"] and "will not load" in s.items[0].title


# 34
def test_34_conformance_mismatch_is_critical(tmp_path):
    fx = tmp_path / "bench"
    (fx / "invalid").mkdir(parents=True)
    (fx / "invalid" / "tampered.json").write_text("{}", encoding="utf-8")
    ver = tmp_path / "verifier"
    ver.mkdir()
    (ver / "verify.py").write_text("print('OVERALL: PASS')\n", encoding="utf-8")  # a verifier that accepts everything
    res = run_paired_verifier(fx, [{"file": "invalid/tampered.json", "expected_result": "FAIL"}], ver, "toy@HEAD (HEAD)")
    assert res["mismatched"] == ["invalid/tampered.json"] and res["results"][0]["observed"] == "PASS"
    s = FindingSink("huggingface")
    findings.hf_findings(s, {"artifacts": [], "completed_at": "t"}, {"corpora": [{"dataset": "ORG/bench", "runs": [res]}]})
    assert any(f.severity == "CRITICAL" and "does not conform" in f.title for f in s.items)


def _gh(repos):
    return {"repos": [{"name": n, "archived": a, "private": False, "pushed_at": "2026-09-20T00:00:00Z", "detail": {"head": {"sha": sha}, "workflows": []}} for n, a, sha in repos]}


# 35
def test_35_reconciliation_flags_orphaned_artifact(tmp_path):
    gh = _gh([("live", False, "a" * 40), ("old", True, "b" * 40)])
    hf = {"artifacts": [
        {"id": "ORG/nolink", "kind": "model", "files": [], "readme_text": "no links", "last_modified": "2026-09-01T00:00:00Z"},
        {"id": "ORG/archived-src", "kind": "dataset", "files": [], "readme_text": "https://github.com/szl-holdings/old", "last_modified": "2026-09-01T00:00:00Z"},
        {"id": "ORG/broken", "kind": "dataset", "files": [], "readme_text": "https://github.com/szl-holdings/gone", "last_modified": "2026-09-01T00:00:00Z"},
    ]}
    rec = reconcile.reconcile(gh, hf, {}, tmp_path)
    states = {o["artifact"]: o["state"] for o in rec["orphaned_hf"]}
    assert states == {"ORG/nolink": "NO_SOURCE_LINK", "ORG/archived-src": "SOURCE_ARCHIVED", "ORG/broken": "BROKEN_SOURCE_LINK"}


# 36
def test_36_reconciliation_flags_version_drift(tmp_path):
    gh = _gh([("a11oy", False, "1234567" + "0" * 33)])
    hf = {"artifacts": [{"id": "ORG/bench", "kind": "dataset", "files": [], "readme_text": "Mirrored from szl-holdings/a11oy@1b40fcbe and https://github.com/szl-holdings/a11oy", "last_modified": "2026-09-01T00:00:00Z"}]}
    rec = reconcile.reconcile(gh, hf, {}, tmp_path)
    assert rec["version_drift"] and rec["version_drift"][0]["pinned"] == "1b40fcbe" and rec["version_drift"][0]["drifted"]


# 37
def test_37_coverage_accounting_closes_or_declares_unavailable(valid):
    from szl_evidence.verifier import verify

    acct = verify(valid)["accounting"]
    assert acct["input_closure"]["closes"] and acct["denominator_state"] == "OBSERVED"
    calls = {"n": 0}

    def h(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=[{"id": 1}], headers={"link": '<https://x/items?page=2>; rel="next"'})
        raise httpx.ConnectError("down")

    items, meta = paginate(mock_client(h), "https://x/items")
    assert meta["denominator_state"] == "UNAVAILABLE" and len(items) == 1  # partial is never presented as complete


# 38
def test_38_symptom_only_recommendation_is_insufficient():
    r = evaluate_recommendation(Recommendation("Edit README numbers to today's values", "instance", "manual"), "generate from live API with CI drift check")
    assert r.verdict == "INSUFFICIENT" and r.replacement
    ok = evaluate_recommendation(Recommendation("CI drift check on every PR", "class", "automated"), "x")
    assert ok.verdict == "SUFFICIENT"


def synthetic_state(out: Path) -> None:
    repo = {"name": "demo", "full_name": "o/demo", "html_url": "https://github.com/o/demo", "private": False, "archived": False, "visibility": "public", "default_branch": "main", "pushed_at": "2026-09-20T00:00:00Z", "size_kb": 10, "language": "Python", "stars": 0, "forks": 0, "watchers": "UNAVAILABLE", "license": None, "description": "demo", "clone": {"ok": True, "head": "a" * 40},
            "detail": {"head": {"sha": "a" * 40}, "workflows": [], "releases": [], "contributors": [{"login": "u", "type": "User", "contributions": 3}], "dependabot_alerts": {"state": "UNAVAILABLE", "http": 403}}}
    files = {"demo": {"presence": {"README": "README.md"}, "secrets": {"hits": [], "files_scanned": 1, "files_skipped": 0}, "code_risks": {}, "lockfiles": [], "readme_text": "demo"}}
    scores = {"demo": scorecard(repo, repo["detail"], None, None, None, NOW)}
    gh = {"gh": {"org": "o", "org_meta": {"public_repos": 1}, "auth": {}, "listing": {"denominator_state": "OBSERVED"}, "repos": [repo], "completed_at": "t"}, "files": files, "smoke": {}, "scores": scores, "lean": {}}
    model = {"kind": "model", "id": "ORG/m", "private": False, "files": [], "library": "NONE", "pipeline_tag": "NONE", "downloads_30d": "UNAVAILABLE", "tags": [], "card": {"axes": {k: {"state": "FAIL"} for k in render.CARD_AXES}, "capability_without_evidence": False}, "model_class": {"artifact_class": "CODE_ONLY", "weight_bytes": 0, "mistakable_for_trained_model": [], "coherence_issues": []}, "functional": {"load": {"state": "NOT_A_MODEL_REPO"}, "config": {"state": "ABSENT"}}}
    hf = {"hf": {"org": "ORG", "auth": {}, "listing": {"model": {"count": 1, "denominator_state": "OBSERVED"}}, "artifacts": [model]}, "conformance": {"corpora": []}, "public_counts": {"counts": {"models": 1}}}
    rec = {"hf_to_source": [], "source_to_hf": [], "orphaned_hf": [], "orphaned_repo_claims": [], "version_drift": [], "naming_inconsistencies": [], "receipt_schema_ids": {}, "receipt_schema_distinct": 0, "schema_version_skew": [], "inventory_drift": []}
    cl = {"claims": [], "consistency": [], "facts": {"public_counts": {}, "public_counts_at": "t", "lean": {}}}
    z = {"findings": [], "bandaids": [], "systemic": {"contradictions": [], "orphans": {"hf_without_living_source": [], "repos_claiming_missing_targets": []}, "duplicates": [], "unenforced_doctrine": [], "unverified_claims": [], "single_points_of_failure": [], "schema_skew": [], "evidence_boundary_violations": []}, "remediation": [], "verifier_implementations": [], "spof": [], "bus_factor": {}}
    for n, obj in (("github", gh), ("hf", hf), ("reconcile", rec), ("claims", cl), ("zoomout", z)):
        save(out, n, obj)


# 39
def test_39_every_report_has_mandatory_header(tmp_path):
    synthetic_state(tmp_path)
    written = render.render_all(tmp_path)
    mds = [p for p in written if p.endswith(".md")]
    assert len(mds) == 12
    for name in mds:
        text = (tmp_path / name).read_text(encoding="utf-8")
        for field in HEADER_FIELDS:
            assert f"\n{field}: " in text, (name, field)


# 40
def test_40_no_report_asserts_unmeasured_value(tmp_path):
    synthetic_state(tmp_path)
    render.render_all(tmp_path)
    gh_md = (tmp_path / "02-github-audit.md").read_text(encoding="utf-8")
    hf_md = (tmp_path / "03-huggingface-audit.md").read_text(encoding="utf-8")
    assert "watchers UNAVAILABLE" in gh_md and "watchers 0" not in gh_md
    assert "Dependabot UNAVAILABLE (HTTP 403)" in gh_md
    assert "| UNAVAILABLE |" in hf_md.split("## Models")[1].split("##")[0]  # downloads unknown, not 0
    assert render.fmt(None) == "UNAVAILABLE" and render.fmt({}) == "none" and render.fmt(True) == "yes"


def test_prior_evidence_admission_rule():
    from szl_evidence.audit.admission import admit

    def h(req):
        return httpx.Response(404) if req.url.path.endswith("/ghost-pkg/json") else httpx.Response(200, json={})

    prior = {
        "ok": {"install_ok": True, "tests": {"state": "PASSED"}},
        "harness": {"install_ok": False, "steps": [{"step": "install", "output": "Multiple top-level packages discovered"}]},
        "ghost": {"install_ok": False, "steps": [{"step": "install", "output": "No matching distribution found for ghost-pkg"}]},
        "real": {"install_ok": False, "steps": [{"step": "install", "output": "No matching distribution found for requests"}]},
    }
    res = admit(prior, {"ok": "a"}, {"ok": "b"}, "interim", client=mock_client(h))
    assert set(res["admitted"]) == {"ok", "ghost"}
    assert res["admitted"]["ok"]["head_changed_since"] is True
    assert set(res["excluded"]) == {"harness", "real"}


def test_unavailable_listing_never_overwrites_observed_state(tmp_path, monkeypatch):
    from szl_evidence.audit import github as gh_mod
    from szl_evidence.audit import pipeline

    save(tmp_path, "github", {"gh": {"repos": [{"name": "kept"}]}})
    monkeypatch.setattr(gh_mod, "collect", lambda *a, **k: {"repos": [], "listing": {"denominator_state": "UNAVAILABLE", "detail": "rate limited"}})
    res = pipeline.run_github("o", tmp_path, clone=False, deep=False, dry_run=False)
    assert res["state"] == "ABSTAIN"
    assert pipeline.load(tmp_path, "github")["gh"]["repos"] == [{"name": "kept"}]


def test_stream_mode_bounds_disk_and_persists_evidence(tmp_path, monkeypatch):
    from szl_evidence.audit import github as gh_mod
    from szl_evidence.audit import pipeline

    def fake_clone(full, dest, timeout=900):
        dest.mkdir(parents=True)
        (dest / "README.md").write_text("x")
        return {"ok": True, "head": "a" * 40, "exit_code": 0}

    import shutil
    from collections import namedtuple

    monkeypatch.setattr(shutil, "disk_usage", lambda p: namedtuple("du", "total used free")(10**12, 0, 10**11))
    monkeypatch.setattr(gh_mod, "clone_repo", fake_clone)
    monkeypatch.setattr(gh_mod, "analyze_clone", lambda p: {"manifests": {}, "receipt_schema_ids": ["szl.receipt/v1"], "verifier_impl_paths": [], "secret_grep_gates": {}})
    gh = {"repos": [{"name": "keepme", "full_name": "o/keepme", "archived": False, "size_kb": 1}, {"name": ".github", "full_name": "o/.github", "archived": False, "size_kb": 1}, {"name": "old", "full_name": "o/old", "archived": True, "size_kb": 1}]}
    files, smoke = pipeline.stream_repos(gh, tmp_path / "clones", deep=True, smoke_cache={})
    assert set(files) == {"keepme", ".github"} and files["keepme"]["receipt_schema_ids"] == ["szl.receipt/v1"]
    assert not (tmp_path / "clones" / "keepme").exists()  # deleted after analysis
    assert (tmp_path / "clones" / ".github").exists()  # org profile kept for later stages
    assert gh["repos"][2]["clone"]["reason"] == "archived"


def test_stream_mode_skips_clone_when_disk_insufficient(tmp_path, monkeypatch):
    import shutil
    from collections import namedtuple

    from szl_evidence.audit import github as gh_mod
    from szl_evidence.audit import pipeline

    monkeypatch.setattr(shutil, "disk_usage", lambda p: namedtuple("du", "total used free")(10**12, 10**12, 10 * 2**20))
    monkeypatch.setattr(gh_mod, "clone_repo", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not clone")))
    gh = {"repos": [{"name": "big", "full_name": "o/big", "archived": False, "size_kb": 500_000}]}
    files, _ = pipeline.stream_repos(gh, tmp_path / "c", deep=True, smoke_cache={})
    assert files == {} and gh["repos"][0]["clone"]["exit_code"] == "NOT_TESTED" and "insufficient free disk" in gh["repos"][0]["clone"]["reason"]


def test_attribution_never_charges_host_or_harness_failures_to_repo():
    from szl_evidence.audit.attribution import classify

    base = {"install_ok": True, "steps": []}
    sym = classify({**base, "tests": {"state": "FAILED", "output_tail": "OSError: [WinError 1314] A required privilege is not held by the client"}}, crlf_risk=False, partial_clone=False)
    assert sym["tests"]["state"] == "HOST_LIMITED" and sym["tests"]["attribution"] == "HOST_PLATFORM"
    nopy = classify({**base, "tests": {"state": "ERROR", "output_tail": "python.exe: No module named pytest"}}, crlf_risk=False, partial_clone=False)
    assert nopy["tests"]["state"] == "NOT_TESTED"
    crlf = classify({**base, "tests": {"state": "FAILED", "output_tail": "FAILED test_manifest_sha256_matches"}}, crlf_risk=True, partial_clone=True)
    assert crlf["tests"]["state"] == "UNRESOLVED"
    dep = classify({**base, "tests": {"state": "FAILED", "output_tail": "RuntimeError: The starlette.testclient module requires the httpx package"}}, crlf_risk=True, partial_clone=True)
    assert dep["tests"]["attribution"] == "REPO_DEFECT" and dep["tests"]["state"] == "FAILED"


def test_stage_receipts_form_a_verifiable_hash_chain(tmp_path):
    from szl_evidence.audit.pipeline import receipt, verify_receipt_chain

    a = receipt(tmp_path, "github-audit", {"inputs_sha256": "a"}, "2026-01-01T00:00:00Z", "PASS", [])
    b = receipt(tmp_path, "hf-audit", {"inputs_sha256": "b"}, "2026-01-01T00:01:00Z", "PASS", [])
    assert b["parent_sha256"] == a["receipt_sha256"]
    res = verify_receipt_chain(tmp_path / "receipts")
    assert res["state"] == "PASS" and len(res["chain"]) == 2
    f = next((tmp_path / "receipts").glob("github-audit-*.json"))
    f.write_text(f.read_text(encoding="utf-8").replace('"PASS"', '"FAIL"'), encoding="utf-8")
    assert verify_receipt_chain(tmp_path / "receipts")["state"] == "FAIL"


def test_every_fix_is_judged_and_symptom_fixes_are_insufficient():
    from szl_evidence.audit.zoomout import evaluate_fixes

    fs = evaluate_fixes([{"structural_fix": "Update the README number"}, {"structural_fix": "Required CI check that fails on drift"}])
    assert [f["fix_verdict"] for f in fs] == ["INSUFFICIENT", "SUFFICIENT"] and "INSUFFICIENT alone" in fs[0]["structural_fix"]
