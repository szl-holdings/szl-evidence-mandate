# 06 — Security findings (locations and classes only)

```text
STATUS: FAIL
WHAT WAS EXPECTED: secret and unsafe-pattern scan of every cloned repository; platform alert counts for every repository
WHAT WAS EXAMINED: 87 cloned repositories scanned (HEAD only)
WHAT ACTUALLY RAN: pattern+entropy secret scan; static risky-pattern scan; alert API queries
WHAT PASSED: 87 scanned repos with no likely-live credential in the local scan
WHAT FAILED: 0 likely-live local hits; 1 repos with open platform secret-scanning alerts
WHAT ABSTAINED: code-scanning UNAVAILABLE 28/118 (HTTP 403); code-scanning UNAVAILABLE 56/118 (HTTP 404); dependabot UNAVAILABLE 28/118 (HTTP 403)
WHAT REMAINS UNRESOLVED: git history (only HEAD scanned); blobs >2MB not fetched by partial clone
WHAT THIS RESULT DOES NOT PROVE: absence of secrets in git history, CI logs, or HF repos
```

## Coverage accounting

```text
artifacts_expected: 118 repositories
artifacts_discovered: 118
artifacts_examined: 87 cloned repositories scanned (HEAD only)
artifacts_functionally_tested: 87
artifacts_not_tested: 31
denominator_state: OBSERVED
# not tested (artifact: reason)
#   cosmos: archived (not cloned)
#   counsel: archived (not cloned)
#   developers: archived (not cloned)
#   docs-site: archived (not cloned)
#   energy-attest-holo: archived (not cloned)
#   evidence-typed-formula-governance: archived (not cloned)
#   fail-closed-governed-ai-services: archived (not cloned)
#   governed-inference-meter: archived (not cloned)
#   governed-norm-holo: archived (not cloned)
#   immune-lattice: archived (not cloned)
#   khipu-lab: archived (not cloned)
#   khipu-pages: archived (not cloned)
#   lambda-gate-holo: archived (not cloned)
#   lean-kernel: archived (not cloned)
#   ouroboros: archived (not cloned)
#   platform: insufficient free disk on audit host to clone (693 MB free < 1414 MB needed)
#   receipt-chain-live: archived (not cloned)
#   szl-cookbook: archived (not cloned)
#   szl-experiments: archived (not cloned)
#   szl-fleet-overlay: archived (not cloned)
#   szl-formula-ledger: archived (not cloned)
#   szl-governed-norm: archived (not cloned)
#   szl-kernels-live: archived (not cloned)
#   szl-organ-integrity: archived (not cloned)
#   szl-otel-mesh: archived (not cloned)
#   szl-pin: clone failed
#   szl-provctl-live: archived (not cloned)
#   szl-telemetry: archived (not cloned)
#   szl-typesafe-triage: insufficient free disk on audit host to clone (694 MB free < 702 MB needed)
#   szl-uds-deployment: archived (not cloned)
#   warhacker-demo: archived (not cloned)
```

Values are never printed. Each hit carries only location, type and a non-reversible fingerprint (in JSON).

Files scanned: 15892; skipped (binary/oversize/vendor): 3482.

## Secret-pattern hits

`pattern confidence` is the specificity of the matched pattern; `likely live` also accounts for context (test path, rule file, placeholder, key header without body).

| repo | path | line | type | pattern confidence | likely live | context |
|---|---|---|---|---|---|---|
| .github | .github/scripts/test_ci_health_digest.py | 52 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| .github | .github/scripts/test_hf_http_boundaries.py | 28 | generic_secret_assignment | LOW | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| .github | tests/test_frontier_issue_operator_authority.py | 362 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| .github | tests/test_frontier_issue_operator_authority.py | 528 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| a11oy | benchmarks/gdw/README.md | 7 | generic_secret_assignment | LOW | no | none |
| a11oy | packages/receipt-substrate/src/research_evidence.test.ts | 301 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| a11oy | spaces/immune/test/immune-v01.test.mjs | 330 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| a11oy | test_boot_preflight.py | 35 | openai_key | HIGH | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| a11oy | tests/test_finance_legacy_access.py | 13 | generic_secret_assignment | LOW | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| a11oy | tests/test_gdw_frontier.py | 104 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| a11oy | tests/test_gdw_principal_wiring.py | 12 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| hatun-mcp | .gitleaks.toml | 16 | private_key_block | HIGH | no | key header without key body |
| hatun-mcp | .gitleaks.toml | 20 | private_key_block | HIGH | no | key header without key body |
| hatun-mcp | docs/DSSE_KEY_INJECTION.md | 41 | private_key_block | HIGH | no | in test/fixture/example path; key header without key body |
| killinchu | tests/test_crawler_status_honesty.py | 144 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| killinchu | tests/test_hf_cpu_basic_capacity_transfer.py | 181 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| szl-forge | model-lab/tests/test_blueprints.py | 28 | generic_secret_assignment | LOW | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| szl-forge | operational/evidence_lab/risk_kernel/tests/test_unresolved_identifier_gate_v3.py | 25 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| szl-forge | tests/test_frontier_provider_unavailable_receipt.py | 108 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| szl-forge | tests/test_frontier_provider_unavailable_receipt.py | 131 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| szl-forge | tests/test_frontier_sealed_count.py | 144 | generic_secret_assignment | LOW | no | in test/fixture/example path |
| szl-forge | tests/test_public_estate_rate_control.py | 389 | generic_secret_assignment | LOW | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| szl-forge | tests/test_public_estate_rate_control.py | 403 | generic_secret_assignment | LOW | no | in test/fixture/example path; benign context (pattern/sentinel/fixture) |
| szl-kernels | .github/workflows/model-publish-gate.yml | 55 | private_key_block | HIGH | no | benign context (pattern/sentinel/fixture); key header without key body |
| szl-khipu | .github/workflows/model-publish-gate.yml | 55 | private_key_block | HIGH | no | benign context (pattern/sentinel/fixture); key header without key body |
| szl-receipt | .github/workflows/model-publish-gate.yml | 55 | private_key_block | HIGH | no | benign context (pattern/sentinel/fixture); key header without key body |

CRITICAL_MANUAL_REVIEW items (likely live, local scan): 0. Repositories with open GitHub secret-scanning alerts (class and count only): szl-forge.

## Risky code patterns (location only; each needs human review)

Distinct sites only; 12 matches in vendored/minified third-party files excluded.

| repo | pattern | distinct sites | first locations |
|---|---|---|---|
| .github | shell_true | 2 | tests/test_estate_deadman.py:1021, tools/production/szl_production_auditor_v5.py:80 |
| .github | tar_extractall_unfiltered | 2 | scripts/restore_llm_router_flagship.py:151, scripts/restore_llm_router_flagship_v2.py:144 |
| a11oy | eval_exec | 22 | a11oy_code_engine.py:347, a11oy_code_runloop.py:96, a11oy_governed_kernel.py:135 (+19 more) |
| a11oy | js_eval | 3 | scripts/test_holo_lab_security.mjs:19, static/3d/surfaces/braineval.js:17, static/3d/surfaces/execverify.js:6 |
| a11oy | yaml_unsafe_load | 2 | scripts/hf_universal_frontend_control.py:342, tests/test_hf_recovery_workflow_definition.py:40 |
| a11oy-net | eval_exec | 1 | tests/test_alloy_local_kernel.py:85 |
| a11oy-net | js_eval | 1 | tests/local-kernel.test.cjs:136 |
| anatomy | eval_exec | 6 | tests/test_creator_publication_title.py:41, tests/test_creator_publication_title.py:63, tests/test_holographic_v7_contract.py:79 (+3 more) |
| frontier-bench | eval_exec | 1 | deploy/bench-plane/finish_bench_plane.py:2156 |
| immune | eval_exec | 2 | tests/test_immune_publication_guard.py:407, tests/test_immune_publication_workflow.py:40 |
| killinchu | eval_exec | 12 | a11oy_code_engine.py:347, killinchu_anatomy.py:147, serve.py:1710 (+9 more) |
| killinchu | os_system | 3 | tests/test_asset_exposure_wave5.py:528, tests/test_defensive_fusion_wave4.py:182, tests/test_public_source_fabric.py:330 |
| lyte-lattice | eval_exec | 1 | python/lyte_lattice/organs/n21_sandbox.py:155 |
| lyte-services | eval_exec | 1 | tests/test_frontend_contract.py:131 |
| szl-atelier | eval_exec | 1 | tests/test_archive_revival_showcase_v2.py:170 |
| szl-brand | eval_exec | 2 | anatomy/scripts/build_anatomy_blood_immune.py:278, anatomy/scripts/build_anatomy_wires.py:567 |
| szl-build-env | yaml_unsafe_load | 1 | verify/test_registry_auth_contract.py:362 |
| szl-doctrine | yaml_unsafe_load | 1 | .github/scripts/release_boundary.py:509 |
| szl-energy-attest | eval_exec | 1 | tests/test_hardening.py:184 |
| szl-forge | eval_exec | 8 | eval/run_heldout.py:2, frontier/qwen35-receiptagent-v3/supervisor_bootstrap.py:474, khipu/sanity_gate.py:216 (+5 more) |
| szl-forge | tar_extractall_unfiltered | 1 | a11oy_mini/convert_a11oy_mini_gguf.py:229 |
| szl-forge | yaml_unsafe_load | 2 | model-lab/tests/test_workflow_contract.py:9, tests/test_lora_ci_ownership.py:12 |
| szl-gpu-bridge | eval_exec | 1 | laptop/runjob.py:291 |
| szl-invariants | eval_exec | 3 | scripts/benchmark_cpu.py:67, tests/test_readme_loading.py:29, tests/test_readme_loading.py:45 |
| szl-kernels | eval_exec | 1 | eval/run_heldout.py:2 |
| szl-khipu | eval_exec | 1 | eval/run_heldout.py:2 |
| szl-receipt | eval_exec | 1 | eval/run_heldout.py:2 |
| szl-substrate | eval_exec | 2 | src/szl_substrate/a11oy_code_engine.py:346, src/szl_substrate/szl_deepdive_gaps.py:247 |
| uds-bundles | yaml_unsafe_load | 1 | observatory/parsing.py:115 |
| vertical-services | eval_exec | 1 | tests/test_counsel_claim_integrity.py:238 |

## Platform alert visibility

Counts of 100 are first-page lower bounds (the API was not paginated in this run).

| repo | Dependabot | code scanning | secret scanning |
|---|---|---|---|
| .github | open 0 | open 50 | open 0 |
| a11oy | open 3 | open >=100 (first page only) | open 0 |
| <private> | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| a11oy-net | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| anatomy | open 0 | open 28 | open 0 |
| ayllu | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| ayllu-hf-space | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| cosmos | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| counsel | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| david-leads | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| developers | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| docs-site | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| energy-attest-holo | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| evidence-doctrine | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| evidence-studio | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| evidence-typed-formula-governance | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| fail-closed-governed-ai-services | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| frontier-bench | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| governance-as-code | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| governed-inference-meter | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| governed-norm-holo | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| governed-receipt-spec | open 0 | open 0 | open 0 |
| hatun-mcp | open 0 | open 8 | open 0 |
| holographic-unify | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| immune | open 2 | open 32 | open 0 |
| immune-lattice | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| khipu-consensus | open 0 | open 8 | open 0 |
| khipu-lab | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| khipu-pages | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| khipu-sda-core | open 0 | open 5 | open 0 |
| khipu-x1 | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| killinchu | open 0 | open 44 | open 0 |
| lambda-gate-holo | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| lean-kernel | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| lutar-lean | open 0 | open 17 | open 0 |
| lyte-lattice | open 0 | open 0 | open 0 |
| lyte-services | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| nexus | open 0 | open 0 | open 0 |
| ouroboros | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| platform | open 7 | open 19 | open 0 |
| puriq-live | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| quant-curve | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| receipt-chain-live | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| retrieval-bench | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| sda | open 0 | open 0 | open 0 |
| szl-atelier | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-block-kv | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-blocked | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-brand | open 0 | open 1 | open 0 |
| szl-build-env | open 0 | open 7 | open 0 |
| szl-calibration | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-ci-witness | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-command-lab | open 0 | open 0 | open 0 |
| szl-constellation | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-cookbook | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-crosscheck | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-doctrine | open 0 | open 5 | open 0 |
| szl-drift | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-eclipse | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-energy-attest | open 0 | open 6 | open 0 |
| szl-engine-bench | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-evidence-litellm | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-experiments | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-fleet-overlay | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-forge | open 1 | open 0 | open 1 [mistral_ai_api_key] |
| szl-formula-ledger | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-formulas | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-frontier | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-gov | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-governed-norm | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-govsign | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-gpu-bridge | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-guardrail-receipt | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-holdings.github.io | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-invariants | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-kernels | open 0 | open 0 | open 0 |
| szl-kernels-live | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-khipu | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-lake | open 0 | open 14 | open 0 |
| szl-lambda-gate | open 0 | open 7 | open 0 |
| szl-maskmod | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-mesh | open 0 | open 15 | open 0 |
| szl-nemo | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-organ-integrity | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-otel-mesh | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-ouroboros | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-papers | open 0 | open 4 | open 0 |
| szl-pin | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-platform | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-provctl | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-provctl-live | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-quant | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-quant-bench | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-quant-witness | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-real-estate | open 0 | open 0 | open 0 |
| szl-receipt | open 0 | open 15 | open 0 |
| szl-receipt-attn | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-retrieval-bench | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-router | open 0 | open 21 | open 0 |
| szl-runbook-catalog | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-second-brain | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-seismic-review | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-serve | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-sovereign-os | open 0 | open 0 | open 0 |
| szl-substrate | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-telemetry | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-trust | open 0 | open 7 | open 0 |
| szl-typesafe-triage | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-uds-deployment | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| szl-vertical-forge | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| szl-wave1-report | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| the-grid | open 0 | UNAVAILABLE (HTTP 404) | open 0 |
| uds-bundles | open 0 | open 14 | open 0 |
| vertical-services | open 0 | open 0 | open 0 |
| vsp-otel | open 0 | open 1 | open 0 |
| warhacker-demo | UNAVAILABLE (HTTP 403) | UNAVAILABLE (HTTP 403) | open 0 |
| yarqa | open 0 | open 11 | open 0 |
| YARQA-ATTN | open 0 | UNAVAILABLE (HTTP 404) | open 0 |

## This tool's own security limitations

- Clean-environment smoke tests execute repository code inside a venv with a stripped environment and redirected HOME/APPDATA/HF_HOME. This is process isolation, not a sandbox: code could still reach the network or the OS credential store.
- `gh` CLI is used for authenticated clones; the token stays in the OS keyring and is never written to reports, logs or the HTTP cache (Authorization headers are not cached; URLs are redacted).
- Entropy/pattern scanning has false negatives (custom formats) and false positives (patterns inside rules/tests).
