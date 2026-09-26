# 07 — Investor view

```text
STATUS: FAIL
WHAT WAS EXPECTED: investor-relevant facts from measured evidence only
WHAT WAS EXAMINED: outputs of 02, 03, 04, 05
WHAT ACTUALLY RAN: aggregation only (no new measurement)
WHAT PASSED: 32 repos installed + tests passed; 22 public Spaces returned 200; 168 claims VERIFIED
WHAT FAILED: 4 CRITICAL/HIGH findings; 3 failed clean installs; 24 CONTRADICTED claims
WHAT ABSTAINED: valuation, market, revenue: not measured, not discussed
WHAT REMAINS UNRESOLVED: 5 test outcomes UNRESOLVED (interim harness); 0 private Spaces not probed; HF inference quality not measured
WHAT THIS RESULT DOES NOT PROVE: commercial viability, product-market fit, or future maintenance
```

## Coverage accounting

```text
artifacts_expected: GitHub: public 118 (org metadata, OBSERVED) + private UNAVAILABLE (not exposed by the org API); HF: 120
artifacts_discovered: GitHub: 118 (authenticated listing, all pages; 0 private); HF: 107 (authenticated listing; 0 private)
artifacts_examined: GitHub: 87 cloned; HF: 107
artifacts_functionally_tested: GitHub: 57; HF: 83
artifacts_not_tested: GitHub: 61; HF: 41 (per-artifact reasons in 02 and 03)
denominator_state: OBSERVED
```

Only measured facts. No valuation, market or fundraising commentary.

## What exists and is independently runnable today (measured)
- Installed in a clean venv **and** passed their own test suite: 32 — <private>, anatomy, frontier-bench, hatun-mcp, immune, khipu-x1, lyte-lattice, lyte-services, szl-blocked, szl-calibration, szl-ci-witness, szl-command-lab, szl-crosscheck, szl-eclipse, szl-engine-bench, szl-govsign, szl-guardrail-receipt, szl-invariants, szl-khipu, szl-nemo, szl-ouroboros, szl-provctl, szl-quant-bench, szl-real-estate, szl-receipt, szl-retrieval-bench, szl-router, szl-sovereign-os, szl-substrate, szl-vertical-forge, szl-wave1-report, vsp-otel
- Installed; tests failed, unresolved or not run: 22 — YARQA-ATTN, david-leads, governed-receipt-spec, holographic-unify, nexus, quant-curve, retrieval-bench, szl-atelier, szl-block-kv, szl-energy-attest, szl-forge, szl-frontier, szl-maskmod, szl-mesh, szl-platform, szl-quant, szl-receipt-attn, szl-second-brain, szl-seismic-review, szl-serve, vertical-services, yarqa
- Failed clean install: 3 — a11oy, ayllu, killinchu
- Public Spaces: 22 of 22 probed returned HTTP 200 at `/`; 1 public Space(s) not probed (a11oy: runtime RUNNING_APP_STARTING; not requested (would wake/restart the Space)); 0 private Spaces not probed.

## Demonstrated vs asserted
- Claims: 707; VERIFIED 168, STALE 71, CONTRADICTED 24, UNVERIFIABLE 444 (see 05).
- Model repositories by measured class (TRAINED_WEIGHTS/TRAINED_ADAPTER = neural-network weight files present; SMALL_ARRAYS = numpy arrays only):
- SOFTWARE_KERNEL: 15
- TRAINED_ADAPTER: 14
- SMALL_ARRAYS: 10
- CODE_ONLY: 4
- DOCS_OR_CONFIG_ONLY: 3
- TRAINED_WEIGHTS: 3
- Conformance: SZLHOLDINGS/governed-receipts-bench: szl-holdings/governed-receipt-spec@007106bcb021 (pinned) 7/7, szl-holdings/governed-receipt-spec@2c82320a9946 (default-branch HEAD) 6/7

## Pre-launch, simulated or historical (as labelled by the estate itself)
- Artifacts tagged roadmap / test-fixture / simulated / synthetic on HF:
- SZLHOLDINGS/KILLINCHU-EYE
- SZLHOLDINGS/MiniEmbed-Nano
- SZLHOLDINGS/Moons-Nano
- SZLHOLDINGS/ReceiptAgent-Nano
- SZLHOLDINGS/TinyKhipu-Nano
- SZLHOLDINGS/chakana
- SZLHOLDINGS/oac-clinical-transport-observability-synthetic
- SZLHOLDINGS/qantu
- SZLHOLDINGS/tinku
- SZLHOLDINGS/waman
- Claims explicitly marked historical in text: 4

## Concentration risk
- Primary languages (non-archived repos): Python 69, TypeScript 9, HTML 4, JavaScript 4, TeX 2, Lean 1, CSS 1
- maintainer concentration: top human contributor accounts for 11087/15177 (73%) of contributions across 126 repos
- bus factor per flagship (min contributors for 50% of commits): a11oy: 1, governed-receipt-spec: 1, hatun-mcp: 1, killinchu: 1, szl-eclipse: 1, szl-forge: 1, szl-frontier: 1, szl-guardrail-receipt: 1, szl-receipt: 1, szl-router: 1
- Contributor figures are per GitHub account (type User) and do not merge aliases of the same person or exclude automation identities; treat concentration as a lower bound.

## License and IP clarity (public repos, GitHub licence metadata)
- Apache-2.0 107, NONE 5, CC-BY-4.0 4, NOASSERTION 2

## Dependency and supply-chain exposure
- Repos with a lockfile: 11 of 87 cloned.
- Dependabot alert data visible for 90 of 118 repos.

## Flagships: backed by runnable artifacts?
| flagship | install | tests | CI (merge gate) | release | bus factor |
|---|---|---|---|---|---|
| szl-router | yes | PASSED | PASS | FAIL | 1 |
| a11oy | no | NOT_TESTED | PASS | PASS | 1 |
| szl-forge | yes | UNRESOLVED | PASS | FAIL | 1 |
| hatun-mcp | yes | PASSED | PASS | PARTIAL | 1 |
| szl-frontier | yes | NOT_TESTED | PASS | PARTIAL | 1 |
| killinchu | no | NOT_TESTED | FAIL | PARTIAL | 1 |
| governed-receipt-spec | yes | HOST_LIMITED | PASS | FAIL | 1 |
| szl-receipt | yes | PASSED | PASS | PASS | 1 |
| szl-guardrail-receipt | yes | PASSED | PASS | FAIL | 1 |
| szl-eclipse | yes | PASSED | PASS | FAIL | 1 |

## Most-downloaded artifacts (HF downloads, last 30 days)
| artifact | kind | downloads 30d | class |
|---|---|---|---|
| SZLHOLDINGS/killinchu-osint-corpus | dataset | 64044 | n/a |
| SZLHOLDINGS/szl-lake | dataset | 6981 | n/a |
| SZLHOLDINGS/chaski | model | 4585 | TRAINED_ADAPTER |
| SZLHOLDINGS/a11oy-verifiable-corpus | dataset | 3893 | n/a |
| SZLHOLDINGS/SZL-Khipu-1.5B | model | 2938 | TRAINED_ADAPTER |
| SZLHOLDINGS/SZL-Khipu-1.5B-GGUF | model | 1735 | TRAINED_WEIGHTS |
| SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent | model | 1727 | TRAINED_ADAPTER |
| SZLHOLDINGS/szl-artifacts | dataset | 760 | n/a |
| SZLHOLDINGS/uds-governance-receipts | dataset | 710 | n/a |
| SZLHOLDINGS/lean-proofs-v1 | dataset | 575 | n/a |

## Highest-severity findings (sorted by severity, then confidence)
1. **[HIGH] killinchu — Documented install `pip install -r requirements.txt` fails: internal dependency vsp-otel is not on PyPI**: `-q -r requirements.txt` exit 1 after 10.22s: ERROR: Could not find a version that satisfies the requirement vsp-otel>=0.1 (from versions: none) ERROR: No matching distribution found for vsp-otel>=0.1 | Verified by two independent reviewers: PyPI JSON API 404 for vsp-otel at audit time
2. **[HIGH] SZLHOLDINGS/lean-theorem-tree — Dataset fails to load via the Hub datasets server**: LOAD_FAILED_SCHEMA_INCONSISTENT: {"error":"Cannot load the dataset split (in streaming mode) to extract the first rows.","cause_exception":"CastError","cause_message":"Couldn't cast\nmeta: struct<title: string, repo: string, commit: string, commit_date:; direct parse of raw files: PARSED
3. **[HIGH] SZLHOLDINGS/szl-1-doctrine-sft — Dataset fails to load via the Hub datasets server**: LOAD_FAILED_SCHEMA_INCONSISTENT: {"error":"Cannot load the dataset split (in streaming mode) to extract the first rows.","cause_exception":"CastError","cause_message":"Couldn't cast\nmessages: list<item: struct<role: string, content: string>>\n child 0; direct parse of raw files: PARSED
