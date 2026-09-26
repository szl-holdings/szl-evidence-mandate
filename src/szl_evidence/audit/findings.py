"""Derive severity-ranked findings from collected evidence. Every finding cites evidence,
a source URL/path, an observation timestamp and a confidence. Nothing here is asserted
without a measured datum behind it."""

from __future__ import annotations

from typing import Any

from .common import FindingSink

FLAGSHIPS = ["szl-router", "a11oy", "szl-forge", "hatun-mcp", "szl-frontier", "killinchu", "governed-receipt-spec", "szl-receipt", "szl-guardrail-receipt", "szl-eclipse"]


def github_findings(sink: FindingSink, gh: dict[str, Any], files: dict[str, Any], smoke: dict[str, Any], scores: dict[str, Any]) -> None:
    now = gh.get("completed_at")
    for r in gh["repos"]:
        name = r["name"]
        url = r["html_url"]
        f = files.get(name)
        s = smoke.get(name) or {}
        sc = scores.get(name, {})
        public = not r.get("private")
        cl = r.get("clone", {})
        if not r.get("archived") and not cl.get("ok") and isinstance(cl.get("exit_code"), int) and "invalid path" in str(cl.get("output", "")):
            sink.add("MEDIUM", name, "Repository cannot be checked out on Windows", f"clone exit {r['clone'].get('exit_code')}: {str(r['clone'].get('output', ''))[-160:]}", url, "HIGH", "portability", "File names contain characters invalid on NTFS (e.g. ':' in timestamps)", "Enforce a filename lint (no ':' '<' '>' '|' '?' '*') in CI for all repos", "S", observed_at=now)
        if f:
            for h in f["secrets"]["hits"]:
                if h["likely_live"]:
                    sink.add("CRITICAL", name, "CRITICAL_MANUAL_REVIEW: suspected live credential", f"type={h['type']} at {h['path']}:{h['line']} (value withheld; fingerprint {h['fingerprint']})", f"{url}/blob/HEAD/{h['path']}#L{h['line']}", "MEDIUM", "secret", "Credential committed to source", "Rotate the credential, purge history, enable push protection org-wide", "M", observed_at=now)
            risky = {k: v for k, v in f["code_risks"].items() if k in ("shell_true", "pickle_load", "yaml_unsafe_load", "torch_load_unsafe", "tar_extractall_unfiltered", "os_system")}
            if risky:
                locs = "; ".join(f"{k}×{v['count']} e.g. {v['locations'][0]}" for k, v in risky.items())
                sink.add("MEDIUM" if name in FLAGSHIPS else "LOW", name, "Unsafe execution/deserialisation patterns present (needs review)", locs, url, "MEDIUM", "security", "No org-wide static rule forbids shell=True / pickle / unsafe yaml", "Adopt a shared ruff/bandit config (S602,S301,S506) as a required org check", "S", observed_at=now)
            lic = sc.get("license", {})
            if lic.get("state") == "FAIL" and public:
                sink.add("HIGH", name, "License missing or contradicted on a public repository", lic.get("evidence", ""), url, "HIGH", "license", "Licence is set per-repo by hand", "Org template + CI check that LICENSE exists and matches metadata/package manifests", "S", observed_at=now)
            if public and not f["presence"].get("SECURITY") and name in FLAGSHIPS:
                sink.add("MEDIUM", name, "Flagship has no SECURITY.md in-repo", "presence scan found no SECURITY file (org-level .github SECURITY.md may apply to GitHub UI only)", url, "HIGH", "docs", "Security policy lives only at org level", "Rely on org default or add in-repo; add check", "S", observed_at=now)
        nodist = None
        if s and s.get("install_ok") is False:
            import re as _re

            m = _re.search(r"No matching distribution found for ([A-Za-z0-9_.\-]+)", str(next((x.get("output", "") for x in s.get("steps", []) if x.get("step") == "install"), "")))
            nodist = m.group(1) if m else None
        if s and r.get("name") in FLAGSHIPS and s.get("install_ok") is False:
            step = next((x for x in s.get("steps", []) if x.get("step") == "install"), {})
            sink.add("HIGH", name, "Flagship cannot be installed from a clean environment", f"`{' '.join(step.get('argv', [])[-3:])}` exit {step.get('exit_code')} after {step.get('duration_s')}s: {str(step.get('output', ''))[-220:]}", url, "HIGH", "developer-experience", f"Requirements name '{nodist}', which is not published to any package index" if nodist else "No clean-environment install job in CI", f"Publish '{nodist}' or reference it by pinned git URL; add a clean-install CI job for the documented path" if nodist else "Add a CI job: fresh venv -> pip install . -> import -> --help, on every PR", "M", observed_at=now)
        elif s and s.get("install_ok") is False:
            step = next((x for x in s.get("steps", []) if x.get("step") == "install"), {})
            sink.add("MEDIUM", name, "Repository cannot be installed from a clean environment", f"exit {step.get('exit_code')}: {str(step.get('output', ''))[-200:]}", url, "HIGH", "developer-experience", f"Requirements name '{nodist}', which is not published to any package index" if nodist else "No clean-environment install job in CI", f"Publish '{nodist}' or reference it by pinned git URL" if nodist else "Reusable org workflow for clean install + import", "M", observed_at=now)
        t = (s or {}).get("tests") or {}
        prov = f" [evidence: {s.get('evidence_admission')}; HEAD at test {str(s.get('head_at_test'))[:8]}, now {str(s.get('head_now'))[:8]}]" if s and s.get("evidence_admission") else ""
        if t.get("state") in ("FAILED", "ERROR") and t.get("attribution") == "REPO_DEFECT":
            sink.add("HIGH" if name in FLAGSHIPS else "MEDIUM", name, "Test suite fails from a clean install", f"{t.get('reason')}; summary {t.get('summary')}; tail: {str(t.get('output_tail', ''))[-200:]}{prov}", url, "HIGH", "tests", "Test dependencies are not declared in an installable extra; CI environment differs from a clean install", "Declare test deps in a `[test]` extra; CI job installs `.[test]` in a fresh venv and runs the suite as a required check", "S", observed_at=now)
        elif t.get("state") in ("FAILED", "ERROR"):
            sink.add("MEDIUM" if name in FLAGSHIPS else "LOW", name, "Test suite fails from a clean install on the audit host (attribution unconfirmed)", f"summary {t.get('summary')}; {t.get('reason', '')}; tail: {str(t.get('output_tail', ''))[-200:]}{prov}", url, "MEDIUM", "tests", "Unknown until reproduced on Linux CI", "Reproduce in a fresh Linux venv; if it reproduces, make the suite a required check", "S", observed_at=now)
        ci = sc.get("ci", {})
        if ci.get("state") == "FAIL" and not r.get("archived") and name in FLAGSHIPS:
            sink.add("HIGH", name, "Flagship CI failing or absent", ci.get("evidence", ""), url, "HIGH", "ci", "CI is not a merge gate", "Branch protection with required checks on default branch", "S", observed_at=now)
        if public and not r.get("archived") and sc.get("release_integrity", {}).get("state") == "FAIL" and name in FLAGSHIPS:
            sink.add("MEDIUM", name, "Flagship has no published release", sc["release_integrity"]["evidence"], url, "HIGH", "release", "Releases are not part of the delivery path", "Tagged, signed releases with hashed assets via a shared release workflow", "M", observed_at=now)
        if public and not r.get("archived") and sc.get("honest_scoping", {}).get("state") == "FAIL" and name in FLAGSHIPS:
            sink.add("MEDIUM", name, "Flagship README does not state what it does not prove", sc["honest_scoping"]["evidence"], url, "MEDIUM", "scoping", "No README template section for non-claims", "README template with mandatory 'What this does not establish' section + lint", "S", observed_at=now)
        runs = r["detail"].get("latest_runs")
        if name in FLAGSHIPS and isinstance(runs, list) and not r.get("archived"):
            latest: dict[str, Any] = {}
            for run in runs:
                latest.setdefault(run.get("name"), run)
            failing = sorted(k for k, x in latest.items() if x.get("conclusion") == "failure" and x.get("event") == "schedule")
            if failing:
                sink.add("MEDIUM", name, "Scheduled monitor workflows are failing", f"latest scheduled runs concluding failure: {failing}", f"{url}/actions", "HIGH", "monitoring", "Monitors alert by failing a workflow nobody is gated on", "Route monitor failures to an issue/on-call and track time-to-acknowledge", "S", observed_at=now)
        bp = r["detail"].get("branch_protection")
        rules = r["detail"].get("rulesets")
        if name in FLAGSHIPS and isinstance(bp, dict) and bp.get("state") and not rules:
            not_protected = "not protected" in str(bp.get("message", "")).lower()
            title = "Default branch not protected and no ruleset applies" if not_protected else "Default branch protection state UNAVAILABLE and no ruleset applies"
            sink.add("MEDIUM" if not_protected else "LOW", name, title, f"branch protection: HTTP {bp.get('http')} {bp.get('message') or '(no message recorded)'}; rulesets on default branch: {rules if rules else 'none'}", url, "HIGH" if not_protected else "LOW", "governance", "Protection configured per repo, if at all", "Org-level ruleset covering all default branches", "S", observed_at=now)


def bus_factor(r: dict[str, Any]) -> Any:
    c = r["detail"].get("contributors")
    if not isinstance(c, list) or not c:
        return "UNAVAILABLE"
    humans = [x for x in c if (x.get("type") or "User") != "Bot" and not str(x.get("login", "")).endswith("[bot]")]
    total = sum(x["contributions"] for x in humans) or 1
    acc = 0
    for i, x in enumerate(sorted(humans, key=lambda y: -y["contributions"]), 1):
        acc += x["contributions"]
        if acc / total >= 0.5:
            return i
    return len(humans)


def hf_findings(sink: FindingSink, hf: dict[str, Any], conf: dict[str, Any]) -> None:
    now = hf.get("completed_at")
    for a in hf["artifacts"]:
        if "files" not in a:
            continue
        rid = a["id"]
        prefix = {"model": "", "dataset": "datasets/", "space": "spaces/"}[a["kind"]]
        url = f"https://huggingface.co/{prefix}{rid}"
        fn = a.get("functional") or {}
        public = not a.get("private")
        if a["kind"] == "space":
            http = fn.get("http") or {}
            if fn.get("runtime_state") in ("BUILD_ERROR", "RUNTIME_ERROR") or http.get("state") == "DID_NOT_LOAD":
                sink.add("CRITICAL" if public else "HIGH", rid, "Space will not load", f"runtime={fn.get('runtime_stage_raw')}; http={http.get('state')} probes={[(p['path'], p['status']) for p in http.get('probes', [])]}", url, "HIGH", "availability", "No liveness monitoring on Spaces", "Scheduled read-only liveness probe with alerting; publication gate requires healthy build", "S", observed_at=now)
        if a["kind"] == "model":
            mc = a.get("model_class") or {}
            if mc.get("mistakable_for_trained_model"):
                sev = "HIGH" if any(("pipeline_tag" in m or "library_name" in m or "task tags" in m) for m in mc["mistakable_for_trained_model"]) else "MEDIUM"
                sink.add(sev, rid, f"{mc.get('artifact_class')} presented in a way that could be mistaken for a trained model", f"signals: {mc['mistakable_for_trained_model']}; weights={mc.get('weight_bytes')} bytes", url, "MEDIUM", "misleading-presentation", "Model-repo type used for code/kernels with trained-model metadata", "Card template field `artifact_class` + lint forbidding task pipeline_tag on non-weight repos", "S", observed_at=now)
            if mc.get("coherence_issues"):
                sink.add("MEDIUM", rid, "Model file set incoherent with declared framework", "; ".join(mc["coherence_issues"]), url, "HIGH", "packaging", "No file-set validation on publish", "Publish gate validating framework/file coherence", "S", observed_at=now)
            ld = (fn.get("load") or {})
            if ld.get("state") == "LOAD_FAILED":
                sink.add("HIGH", rid, "Model arrays fail to load", str(ld)[:300], url, "HIGH", "functional", "", "Load test in publish gate", "S", observed_at=now)
            for k, h in (fn.get("headers") or {}).items():
                if h.get("state") == "INVALID":
                    small = isinstance(h.get("bytes"), int) and h["bytes"] < 1_000_000
                    if small:
                        sink.add("MEDIUM", rid, "File with a weights extension is not a weights file", f"{h.get('file')} ({h.get('bytes')} bytes): {h.get('detail')}", url, "HIGH", "packaging", "Auxiliary file (e.g. Ollama Modelfile) given a .gguf extension", "Rename to its real type; publish gate validates magic bytes for every weights-extension file", "S", observed_at=now)
                    else:
                        sink.add("HIGH", rid, f"{k} weights header invalid", str(h), url, "HIGH", "functional", "Corrupt or mislabelled weights", "Header validation in publish gate", "S", observed_at=now)
        if a["kind"] == "dataset":
            st = (fn.get("slice") or {}).get("state") or (fn.get("splits") or {}).get("state")
            if st in ("LOAD_FAILED", "LOAD_FAILED_SCHEMA_INCONSISTENT"):
                df = fn.get("direct_files") or {}
                sink.add("HIGH" if public else "MEDIUM", rid, "Dataset fails to load via the Hub datasets server", f"{st}: {str((fn.get('slice') or fn.get('splits') or {}).get('detail', ''))[:220]}; direct parse of raw files: {df.get('state')}", url, "HIGH", "functional", "Heterogeneous files under one config with no declared features", "Declare configs/features in card YAML; CI load test with `datasets` before publish", "S", observed_at=now)
            if fn.get("pii_patterns"):
                sink.add("MEDIUM", rid, "Sensitive-content patterns in first rows (manual review, not a conclusion)", f"pattern counts: {fn['pii_patterns']}", url, "LOW", "privacy", "", "Manual review; PII scan in publish gate", "S", observed_at=now)
            cs = fn.get("card_schema") or {}
            for split, v in (cs.get("row_counts") or {}).items():
                if v.get("match") is False:
                    sink.add("MEDIUM", rid, "Declared row count differs from observed", f"split {split}: declared {v['declared']} observed {v['observed']}", url, "HIGH", "card-accuracy", "Counts hand-copied into card", "Generate dataset_info from data at publish", "S", observed_at=now)
            if cs.get("schema_match") is False:
                sink.add("MEDIUM", rid, "Card-declared features differ from loaded schema", f"declared {cs.get('declared_features')}", url, "HIGH", "card-accuracy", "", "Generate dataset_info from data at publish", "S", observed_at=now)
        card = a.get("card") or {}
        if public and card.get("capability_without_evidence"):
            sink.add("MEDIUM", rid, "Card asserts capability with no linked evaluation evidence", f"assertions: {card['capability_assertions']}", url, "MEDIUM", "unverified-claim", "Cards written by hand without an evidence link requirement", "Card lint: capability phrases require an evaluation section with data+metric+receipt", "S", observed_at=now)
        ax = card.get("axes") or {}
        if public and ax.get("license", {}).get("state") == "FAIL":
            sink.add("MEDIUM", rid, "No usable licence on public artifact", ax["license"]["evidence"], url, "HIGH", "license", "", "Card template requires SPDX licence + LICENSE file", "S", observed_at=now)
    for c in conf.get("corpora", []):
        url = f"https://huggingface.co/datasets/{c['dataset']}"
        for run in c.get("runs", []):
            if run.get("mismatched"):
                sink.add("CRITICAL", c["dataset"], "Conformance corpus does not conform with its paired verifier", f"{run['verifier']}: {run['matched']}/{run['fixtures']} fixtures match; mismatched {run['mismatched']}; " + "; ".join(f"{x['file']}: declared {x['declared']} observed {x['observed']}" for x in run["results"] if not x["match"]), url, "HIGH", "conformance", "Bench pins an old verifier commit; verifier changes are not tested against the bench", "Run the bench as a required CI job in the verifier repo; version expected outcomes per verifier release", "M", "any claim that receipts in this format are verifiable with the current verifier")
            if run.get("results"):
                skipped_sig = [x["file"] for x in run["results"] if "PASS SKIP" in x.get("output_tail", "")]
                if skipped_sig:
                    sink.add("HIGH", "governed-receipt-spec", "Verifier reports PASS for a signature check it skipped", f"{run['verifier']}: 'sig: PASS SKIP ... signature not cryptographically verified' on {skipped_sig}", url, "HIGH", "vacuous-pass", "Tri-state outcome collapsed into PASS", "Emit NOT_TESTED for skipped checks and make OVERALL ABSTAIN (not PASS) when a required check did not run", "S")
            if run.get("state") == "SOURCE_UNAVAILABLE":
                sink.add("INFO", c["dataset"], "Paired verifier could not be retrieved", run.get("detail", ""), url, "LOW", "coverage")
