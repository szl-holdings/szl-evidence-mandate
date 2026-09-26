# 08 — Developer view

```text
STATUS: FAIL
WHAT WAS EXPECTED: developer-experience facts from measured runs
WHAT WAS EXAMINED: 57 clean-environment runs; HF functional results
WHAT ACTUALLY RAN: aggregation of 02/03/04 measurements
WHAT PASSED: 39 repos reached a first successful run
WHAT FAILED: 3 failed install (a11oy, ayllu, killinchu); 8 test suites FAILED/ERROR with attribution
WHAT ABSTAINED: not smoke-tested: 61 of 118 repos (reasons in 02 coverage block)
WHAT REMAINS UNRESOLVED: 5 UNRESOLVED test outcomes (interim harness)
WHAT THIS RESULT DOES NOT PROVE: that failures reproduce on Linux; Clean-install/test runs executed on a Windows 11 host (Python 3.12 venv, stripped environment, shallow clones with core.symlinks=false); Windows-specific outcomes are attributed HOST_PLATFORM, not to repositories.
```

## Coverage accounting

```text
artifacts_expected: public 118 (org metadata, OBSERVED) + private UNAVAILABLE (not exposed by the org API)
artifacts_discovered: 118 (authenticated listing, all pages; 0 private)
artifacts_examined: 87
artifacts_functionally_tested: 57
artifacts_not_tested: 61
denominator_state: OBSERVED
# not tested (artifact: reason)
#   .github: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   a11oy-net: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   ayllu-hf-space: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   cosmos: archived: metadata-only scoring, not cloned
#   counsel: archived: metadata-only scoring, not cloned
#   developers: archived: metadata-only scoring, not cloned
#   docs-site: archived: metadata-only scoring, not cloned
#   energy-attest-holo: archived: metadata-only scoring, not cloned
#   evidence-doctrine: pnpm workspace ('catalog:' specifiers) installed with npm by the harness; not attributable to the repository
#   evidence-studio: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   evidence-typed-formula-governance: archived: metadata-only scoring, not cloned
#   fail-closed-governed-ai-services: archived: metadata-only scoring, not cloned
#   governance-as-code: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   governed-inference-meter: archived: metadata-only scoring, not cloned
#   governed-norm-holo: archived: metadata-only scoring, not cloned
#   immune-lattice: archived: metadata-only scoring, not cloned
#   khipu-consensus: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   khipu-lab: archived: metadata-only scoring, not cloned
#   khipu-pages: archived: metadata-only scoring, not cloned
#   khipu-sda-core: insufficient free disk on audit host (682 MB < 1536 MB)
#   lambda-gate-holo: archived: metadata-only scoring, not cloned
#   lean-kernel: archived: metadata-only scoring, not cloned
#   lutar-lean: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   ouroboros: archived: metadata-only scoring, not cloned
#   platform: insufficient free disk on audit host to clone (693 MB free < 1414 MB needed)
#   puriq-live: insufficient free disk on audit host (693 MB < 1536 MB)
#   receipt-chain-live: archived: metadata-only scoring, not cloned
#   sda: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-brand: insufficient free disk on audit host (659 MB < 1536 MB)
#   szl-build-env: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-constellation: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-cookbook: archived: metadata-only scoring, not cloned
#   szl-doctrine: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-drift: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-evidence-litellm: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-experiments: archived: metadata-only scoring, not cloned
#   szl-fleet-overlay: archived: metadata-only scoring, not cloned
#   szl-formula-ledger: archived: metadata-only scoring, not cloned
#   szl-formulas: insufficient free disk on audit host (681 MB < 1536 MB)
#   szl-gov: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-governed-norm: archived: metadata-only scoring, not cloned
#   szl-gpu-bridge: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-holdings.github.io: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-kernels: insufficient free disk on audit host (663 MB < 1536 MB)
#   szl-kernels-live: archived: metadata-only scoring, not cloned
#   szl-lake: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-lambda-gate: insufficient free disk on audit host (672 MB < 1536 MB)
#   szl-organ-integrity: archived: metadata-only scoring, not cloned
#   szl-otel-mesh: archived: metadata-only scoring, not cloned
#   szl-papers: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-pin: clone/checkout failed (exit 1): file-level analysis NOT_TESTED
#   szl-provctl-live: archived: metadata-only scoring, not cloned
#   szl-quant-witness: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-runbook-catalog: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-telemetry: archived: metadata-only scoring, not cloned
#   szl-trust: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   szl-typesafe-triage: insufficient free disk on audit host to clone (694 MB free < 702 MB needed)
#   szl-uds-deployment: archived: metadata-only scoring, not cloned
#   the-grid: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   uds-bundles: no Python/Node entry point: installability NOT_TESTED (file-level analysis done)
#   warhacker-demo: archived: metadata-only scoring, not cloned
```

## Time-to-first-successful-run (clean venv, seconds)

Definition: seconds from venv creation to the first successful import, `--help`, quickstart command or passing test suite. Import, build and test results are shown separately in 02.

| repo | seconds | tests | evidence |
|---|---|---|---|
| szl-quant-bench | 16.8 | PASSED | admitted from interim run (HEAD at test 9364ee78; unchanged) |
| szl-ci-witness | 17.7 | PASSED | admitted from interim run (HEAD at test fd50310f; changed since) |
| szl-provctl | 18.1 | PASSED | admitted from interim run (HEAD at test 7e416471; unchanged) |
| szl-real-estate | 18.3 | PASSED | admitted from interim run (HEAD at test 8961ba7e; changed since) |
| <private> | 19.0 | PASSED | admitted from interim run (HEAD at test f3c01663; changed since) |
| szl-ouroboros | 20.1 | PASSED | admitted from interim run (HEAD at test 209a6439; changed since) |
| szl-blocked | 22.3 | PASSED | admitted from interim run (HEAD at test 5873409a; changed since) |
| szl-retrieval-bench | 22.8 | PASSED | admitted from interim run (HEAD at test 54f5dd96; unchanged) |
| szl-sovereign-os | 23.2 | PASSED | admitted from interim run (HEAD at test a18f76e9; changed since) |
| szl-frontier | 24.4 | NOT_TESTED | admitted from interim run (HEAD at test d24d7a22; changed since) |
| szl-invariants | 25.9 | PASSED | admitted from interim run (HEAD at test a88731a0; unchanged) |
| szl-govsign | 27.8 | PASSED | admitted from interim run (HEAD at test 1eba876a; unchanged) |
| szl-crosscheck | 27.9 | PASSED | admitted from interim run (HEAD at test 998fd8b3; changed since) |
| szl-mesh | 28.3 | FAILED | admitted from interim run (HEAD at test 4f72f452; unchanged) |
| szl-vertical-forge | 28.5 | PASSED | admitted from interim run (HEAD at test 6a05a170; changed since) |
| szl-wave1-report | 28.5 | PASSED | admitted from interim run (HEAD at test f5370d55; unchanged) |
| szl-guardrail-receipt | 33.5 | PASSED | admitted from interim run (HEAD at test e7ef3d79; changed since) |
| szl-nemo | 33.8 | PASSED | admitted from interim run (HEAD at test f7cce8e4; unchanged) |
| szl-engine-bench | 33.9 | PASSED | admitted from interim run (HEAD at test c5ec41b9; unchanged) |
| anatomy | 34.0 | PASSED | fresh (pip-cache fix; pre-fix2 clone) |
| szl-receipt | 34.0 | PASSED | admitted from interim run (HEAD at test c3ad652f; unchanged) |
| szl-eclipse | 34.2 | PASSED | admitted from interim run (HEAD at test 8739668a; changed since) |
| szl-energy-attest | 35.9 | UNRESOLVED | admitted from interim run (HEAD at test 217ba7d5; unchanged) |
| frontier-bench | 38.3 | PASSED | fresh (pip-cache fix; pre-fix2 clone) |
| szl-serve | 38.8 | UNRESOLVED | admitted from interim run (HEAD at test 201a7b3d; unchanged) |
| lyte-lattice | 42.7 | PASSED | admitted from interim run (HEAD at test 309d759c; unchanged) |
| immune | 44.0 | PASSED | admitted from interim run (HEAD at test cb5768dd; changed since) |
| szl-router | 44.7 | PASSED | admitted from interim run (HEAD at test 00b07f17; changed since) |
| szl-command-lab | 50.5 | PASSED | admitted from interim run (HEAD at test 88dc7c6c; unchanged) |
| szl-second-brain | 53.7 | FAILED | admitted from interim run (HEAD at test 25c12301; unchanged) |
| szl-calibration | 55.8 | PASSED | admitted from interim run (HEAD at test 6a7973aa; changed since) |
| khipu-x1 | 57.5 | PASSED | admitted from interim run (HEAD at test 360bb6c5; changed since) |
| szl-substrate | 65.2 | PASSED | admitted from interim run (HEAD at test 5b4d0d5b; unchanged) |
| yarqa | 67.3 | FAILED | admitted from interim run (HEAD at test 99e16ae4; unchanged) |
| hatun-mcp | 67.6 | PASSED | fresh (pip-cache fix; pre-fix2 clone) |
| vsp-otel | 68.9 | PASSED | admitted from interim run (HEAD at test b88ec43a; changed since) |
| szl-forge | 76.2 | UNRESOLVED | admitted from interim run (HEAD at test 26ae8bfc; changed since) |
| lyte-services | 82.1 | PASSED | admitted from interim run (HEAD at test 9ce4e6b5; changed since) |
| szl-khipu | 87.0 | PASSED | admitted from interim run (HEAD at test ef7e85a1; changed since) |

Flagships without a successful measured run:
- a11oy
- killinchu
- governed-receipt-spec

## Onboarding blockers (ranked by frequency)
1. NOT_TESTED: no entry point detected (no import, --help or quickstart attempted) — 15 repos
2. test suite fails on clean install (REPO_DEFECT) — 8 repos
3. test outcome UNRESOLVED (recorded under interim harness; re-run needed) — 5 repos
4. dependency not on PyPI / unresolvable — 2 repos
5. packaging: setuptools flat-layout discovery / build backend error — 1 repos

## Flagships with no test files
- none

## Files matching verifier file-name patterns (lower bound; independence NOT_TESTED)
17 files match `verify|verifier|verify_receipt|receipt_verify|verify_chain|dsse_verify`.py outside tests 
- .github/.github/scripts/frontier_payload/verify.py
- a11oy/anatomy-ledger/tools/verify.py
- a11oy/governance-evidence-plane/scripts/receipt_verify.py
- a11oy/payloads/round-10-estate/a11oy/verifier.py
- a11oy/src/a11oy/verifier.py
- ayllu/scripts/verify_receipt.py
- frontier-bench/verify/verifier.py
- governed-receipt-spec/verify.py
- quant-curve/verify/verifier.py
- retrieval-bench/verify/verifier.py
- szl-build-env/verify/dsse_verify.py
- <private>/verify.py
- szl-gov/tools/verify_receipt.py
- szl-guardrail-receipt/src/szl_guardrail_receipt/verify.py
- szl-router/szl_router/verify.py
- szl-trust/scripts/verify_chain.py
- yarqa/scripts/verify_receipt.py

## Near-duplicate repository names (merge/rename candidates; human judgement needed)
- .github ↔ szl-holdings.github.io
- YARQA-ATTN ↔ yarqa
- a11oy ↔ <private>
- a11oy ↔ a11oy-net
- ayllu ↔ ayllu-hf-space
- evidence-doctrine ↔ szl-doctrine
- frontier-bench ↔ szl-frontier
- governance-as-code ↔ szl-gov
- governed-receipt-spec ↔ szl-gov
- governed-receipt-spec ↔ szl-receipt
- khipu-consensus ↔ szl-khipu
- khipu-sda-core ↔ sda
- khipu-sda-core ↔ szl-khipu
- khipu-x1 ↔ szl-khipu
- platform ↔ szl-platform
- quant-curve ↔ szl-quant
- retrieval-bench ↔ szl-retrieval-bench
- szl-forge ↔ szl-vertical-forge
- szl-guardrail-receipt ↔ szl-receipt
- szl-quant ↔ szl-quant-bench
- szl-quant ↔ szl-quant-witness
- szl-receipt ↔ szl-receipt-attn

## Receipt-like schema identifiers
- 305 identifiers found; see 04 for the estate/standard/test split and genuine version skew.

## Missing CITATION.cff on repos whose README contains a DOI, arXiv id, BibTeX block or citation heading
- evidence-doctrine
- szl-receipt
- szl-seismic-review
- szl-substrate

## For a newcomer
- Try first (fastest measured success with passing tests): szl-quant-bench (16.8 s)
- Public Spaces answering `/` with 200 (fastest first; latencies were timed with a ~15.6 ms-resolution clock on this host (values are multiples of it; differences below that are not measurable).): SZLHOLDINGS/ayllu (78 ms), SZLHOLDINGS/szl-khipu (78 ms), SZLHOLDINGS/finance (79 ms), SZLHOLDINGS/szl-atelier (94 ms), SZLHOLDINGS/david-leads (109 ms)
- Can they succeed in five minutes? yes for szl-quant-bench
- Cards that may mislead (showing 15 of 36; full list in 09/11):
- SZLHOLDINGS/a11oy-v19-substrate: DOCS_OR_CONFIG_ONLY presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-governed-norm: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-lambda-gate: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/governed-inference-meter: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/governed-inference-meter: Card asserts capability with no linked evaluation evidence
- SZLHOLDINGS/szl-kernels: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-kernels: Card asserts capability with no linked evaluation evidence
- SZLHOLDINGS/szl-blocked: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-govsign: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-provctl: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-nemo: CODE_ONLY presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-invariants: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-ouroboros: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/szl-formulas: SOFTWARE_KERNEL presented in a way that could be mistaken for a trained model
- SZLHOLDINGS/SZLHOLDINGS: DOCS_OR_CONFIG_ONLY presented in a way that could be mistaken for a trained model
- Dead Spaces: none among publicly probeable Spaces
- Datasets that fail to load:
- SZLHOLDINGS/ouroboros-arxiv-preprint
- SZLHOLDINGS/lean-theorem-tree
- SZLHOLDINGS/doctrine-v10-v11
- SZLHOLDINGS/szl-1-doctrine-sft
- SZLHOLDINGS/governed-agent-bench
- SZLHOLDINGS/szl-frontier-covenant
- SZLHOLDINGS/david-leads-data
