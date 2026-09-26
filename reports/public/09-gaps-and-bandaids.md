# 09 — Gaps and band-aids

```text
STATUS: FAIL
WHAT WAS EXPECTED: systemic gap analysis across both estates
WHAT WAS EXAMINED: 169 findings + reconciliation + claims
WHAT ACTUALLY RAN: rule-based band-aid detection (each rule fires only on evidence)
WHAT PASSED: none
WHAT FAILED: 6 band-aids identified; 3 contradiction groups; 33 contradicted claims
WHAT ABSTAINED: band-aids without machine-visible evidence are not reported
WHAT REMAINS UNRESOLVED: organisational causes (staffing, priorities) are out of scope
WHAT THIS RESULT DOES NOT PROVE: that the listed structural fixes are sufficient on their own
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

## Band-aids (root cause → structural fix; symptom-only fixes marked INSUFFICIENT)

### Hand-published dated inventory counts
- Evidence: 14 dated inventory claims have drifted, e.g. github:szl-holdings/szl-constellation/README.md:61: claimed 41 observed 2026-09-23; live 35 observed 2026-09-25T16:34:27Z; drift -6
- Root cause: Counts are embedded as static prose, regenerated only when someone runs the snapshot workflow
- Symptom-only recommendation: “Edit the README numbers to today's values” → **INSUFFICIENT**
- Structural fix (replacement): Render counts from a scheduled live-API inventory job that commits the JSON and fails CI when any README/card count disagrees

### Pinned Lean counts copied into prose
- Evidence: 66 Lean-count claims match the pinned revision but not HEAD, e.g. github:szl-holdings/.github/README.md:147: claimed 14 matches pinned revision c7c0ba17 (2026-05-31T00:51:46-04:00) but HEAD 75a4a311 has 33
- Root cause: Numbers are measured once with a regex counter and copied into many cards and READMEs
- Symptom-only recommendation: “Update 749/14/163 to the new numbers” → **INSUFFICIENT**
- Structural fix (replacement): Count via the Lean environment (enumerate constants, `#print axioms`, sorry detection by elaboration) in lutar-lean CI; publish one JSON; all surfaces template from it with a drift check

### Conformance corpus pinned to an old verifier commit
- Evidence: SZLHOLDINGS/governed-receipts-bench: all fixtures match at pinned 007106bcb021, but current default branch mismatches [['valid/lake-inference-receipt.json']]
- Root cause: The verifier evolves without running the corpus; pinning hides the break instead of detecting it
- Symptom-only recommendation: “Update the pin in the card to the newest commit” → **INSUFFICIENT**
- Structural fix (replacement): Required CI job in the verifier repo that replays every corpus fixture; corpus expected outcomes versioned per verifier release with an explicit changelog of semantic changes

### Per-repo receipt verifiers
- Evidence: 17 separate verifier implementations: ['.github/.github/scripts/frontier_payload/verify.py', 'a11oy/anatomy-ledger/tools/verify.py', 'a11oy/governance-evidence-plane/scripts/receipt_verify.py', 'a11oy/payloads/round-10-estate/a11oy/verifier.py', 'a11oy/src/a11oy/verifier.py', 'ayllu/scripts/verify_receipt.py', 'frontier-bench/verify/verifier.py', 'governed-receipt-spec/verify.py', 'quant-curve/verify/verifier.py', 'retrieval-bench/verify/verifier.py']
- Root cause: No shared receipt library; each component re-implements parsing and checks
- Symptom-only recommendation: “Fix the bug in whichever verifier failed” → **INSUFFICIENT**
- Structural fix (replacement): One canonical receipt schema + one shared verifier library consumed by all components; a conformance suite in that library gates every consumer's CI

### Copy-pasted grep secret gates
- Evidence: identical grep-based secret gate in ['szl-kernels/.github/workflows/model-publish-gate.yml', 'szl-khipu/.github/workflows/model-publish-gate.yml']
- Root cause: Secret detection implemented per repo as a workflow step
- Symptom-only recommendation: “Add another token pattern to the grep” → **INSUFFICIENT**
- Structural fix (replacement): Org-level GitHub secret scanning + push protection and a required reusable workflow (gitleaks) from .github

### Skipped signature check reported as PASS
- Evidence: szl-holdings/governed-receipt-spec@2c82320a9946 (default-branch HEAD): 'sig: PASS SKIP ... signature not cryptographically verified' on ['valid/a11oy-khipu-chain.json', 'valid/a11oy-khipu-genesis.json', 'valid/lake-inference-receipt.json', 'valid/daily-activity-receipt.json', 'invalid/tampered-payload.json', 'invalid/broken-chain.json']
- Root cause: Verifier collapses NOT_TESTED into PASS
- Symptom-only recommendation: “Always pass --verify-key in the documented command” → **INSUFFICIENT**
- Structural fix (replacement): Verifier emits NOT_TESTED for skipped checks and an ABSTAIN overall; conformance fixtures include a no-key case expecting ABSTAIN

## Contradictions

### Same fact stated with different values (same unit and basis)

| type | unit | basis | value → locations |
|---|---|---|---|
| lean_count | axioms_raw | undated | 15: hf:dataset:SZLHOLDINGS/thesis-v18-formal-verification/README.md:68 ‖ 23: github:szl-holdings/lutar-lean/README.md:57 |
| lean_count | declarations | undated | 1323: github:szl-holdings/lutar-lean/README.md:57 ‖ 749: github:szl-holdings/.github/README.md:158, github:szl-holdings/killinchu/README.md:64, github:szl-holdings/szl-doctrine/README.md:78, github:szl-holdings/szl-kernels/README.md:283 (+22 more) |
| doctrine_version | none | any (current and historical uses mixed) | v2: github:szl-holdings/killinchu/README.md:344, hf:space:SZLHOLDINGS/killinchu/README.md:344 ‖ v6: hf:dataset:<private>/README.md:68 ‖ v7: hf:dataset:SZLHOLDINGS/why-we-lead/README.md:3, hf:dataset:SZLHOLDINGS/why-we-lead/README.md:18, hf:dataset:SZLHOLDINGS/why-we-lead/README.md:26 ‖ v10: github:szl-holdings/szl-kernels/README.md:35, hf:model:SZLHOLDINGS/szl-kernels/README.md:67, hf:dataset:SZLHOLDINGS/rag-corpus-v1/README.md:47, hf:dataset:SZLHOLDINGS/rag-corpus-v1/README.md:74 (+4 more) ‖ v11: github:szl-holdings/.github/README.md:1, github:szl-holdings/.github/README.md:158, github:szl-holdings/a11oy/README.md:261, github:szl-holdings/a11oy/README.md:280 (+220 more) |

### Claims contradicted by measurement 

| location | type | claimed | observed | evidence |
|---|---|---|---|---|
| github:szl-holdings/governance-as-code/README.md:18 | inventory_count | 45 spaces | 22 | undated claim 45 != live public 22 (authenticated total 28) |
| github:szl-holdings/lutar-lean/README.md:57 | lean_count | 1323 declarations | HEAD=2119, pinned=749 | undated claim 1323; HEAD recomputation 2119; pinned 749 |
| github:szl-holdings/lutar-lean/README.md:57 | lean_count | 23 axioms_raw | HEAD=34, pinned=15 | undated claim 23; HEAD recomputation 34; pinned 15 |
| github:szl-holdings/szl-mesh/README.md:356 | doi | 10.1145/296806.296824 | NOT_FOUND | handle state NOT_FOUND; existence does not verify the content attributed to it |
| hf:dataset:SZLHOLDINGS/thesis-v18-formal-verification/README.md:109 | inventory_count | 17 spaces | 22 | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/thesis-v18-formal-verification/README.md:109 | inventory_count | 29 datasets | 35 | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | inventory_count | 13 spaces | 22 | undated claim 13 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | inventory_count | 28 datasets | 35 | undated claim 28 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | inventory_count | 3 models | 49 | undated claim 3 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | inventory_count | 25 spaces | 22 | undated claim 25 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | inventory_count | 27 datasets | 35 | undated claim 27 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | inventory_count | 9 models | 49 | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:<private>/README.md:97 | inventory_count | 25 spaces | 28 | undated claim 25 != live public 28 (authenticated total 28) |
| hf:dataset:<private>/README.md:97 | inventory_count | 27 datasets | 43 | undated claim 27 != live public 43 (authenticated total 43) |
| hf:dataset:<private>/README.md:97 | inventory_count | 9 models | 49 | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | inventory_count | 17 spaces | 22 | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | inventory_count | 29 datasets | 35 | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | inventory_count | 8 models | 49 | undated claim 8 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | inventory_count | 25 spaces | 22 | undated claim 25 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | inventory_count | 27 datasets | 35 | undated claim 27 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | inventory_count | 9 models | 49 | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:<private>/README.md:108 | inventory_count | 25 spaces | 28 | undated claim 25 != live public 28 (authenticated total 28) |
| hf:dataset:<private>/README.md:108 | inventory_count | 27 datasets | 43 | undated claim 27 != live public 43 (authenticated total 43) |
| hf:dataset:<private>/README.md:108 | inventory_count | 9 models | 49 | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:<private>/README.md:120 | inventory_count | 25 spaces | 28 | undated claim 25 != live public 28 (authenticated total 28) |
| hf:dataset:<private>/README.md:120 | inventory_count | 27 datasets | 43 | undated claim 27 != live public 43 (authenticated total 43) |
| hf:dataset:<private>/README.md:120 | inventory_count | 9 models | 49 | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/lean-theorem-tree/README.md:111 | inventory_count | 17 spaces | 22 | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/lean-theorem-tree/README.md:111 | inventory_count | 29 datasets | 35 | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:12 | inventory_count | 44 models | 49 | undated claim 44 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:70 | inventory_count | 44 models | 49 | undated claim 44 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:70 | inventory_count | 30 datasets | 35 | undated claim 30 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:71 | inventory_count | 47 spaces | 22 | undated claim 47 != live public 22 (authenticated total 28) |

## Orphans
- HF artifacts whose card declares no source link: 22 (3 private)
  - SZLHOLDINGS/SZLHOLDINGS
  - SZLHOLDINGS/KHIPU-R2
  - SZLHOLDINGS/WILLAY
  - SZLHOLDINGS/qantu
  - SZLHOLDINGS/waman
  - SZLHOLDINGS/chakana
  - SZLHOLDINGS/tinku
  - SZLHOLDINGS/szl-training-scripts
  - SZLHOLDINGS/TinyKhipu-Nano
  - SZLHOLDINGS/ReceiptAgent-Nano
  - SZLHOLDINGS/why-we-lead
  - <private>
  - <private>
  - SZLHOLDINGS/szl-second-brain-inrepo
  - SZLHOLDINGS/model-bom
  - SZLHOLDINGS/release-assets
  - SZLHOLDINGS/szl-estate-graph
  - SZLHOLDINGS/david-leads-data
  - SZLHOLDINGS/lyte
  - SZLHOLDINGS/szl-atelier
  - <private>
  - SZLHOLDINGS/holographic-unify
- HF artifacts whose linked source repo is archived: 2
  - SZLHOLDINGS/szl-governed-norm → governed-receipt-spec, szl-governed-norm, szl-khipu, szl-lambda-gate, szl-papers
  - SZLHOLDINGS/governed-inference-meter → governed-inference-meter, szl-energy-attest
- HF artifacts linking a source repo that does not exist: 0
- Repos linking HF targets that do not exist:
- .github: datasets/szlholdings/doctrine-v11
- a11oy: spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/sda
- anatomy: spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/sda
- governed-receipt-spec: spaces/szlholdings/governed-receipt-verifier
- khipu-consensus: spaces/szlholdings/khipu-constellation
- killinchu: spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/sda
- lutar-lean: spaces/szlholdings/lambda-aggregator-live
- szl-govsign: spaces/szlholdings/govsign-live
- szl-guardrail-receipt: spaces/szlholdings/guardrail-receipt
- szl-kernels: spaces/szlholdings/holographic
- szl-khipu: spaces/szlholdings/anatomy
- szl-provctl: spaces/szlholdings/szl-provctl-live
- szl-serve: spaces/szlholdings/szl-forge-lab

## Possible duplicates: files matching verifier file-name patterns (lower bound; independence NOT_TESTED) 
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

## Unenforced doctrine (stated in prose, no machine check found) 
| type | location | text |
|---|---|---|
| doctrine_version | github:szl-holdings/.github/README.md:1 | > **SZL Holdings** · Doctrine v11 · Λ = Conjecture 1 (advisory, never "green"/theorem) · canonical [a-11-oy.com](https:/ |
| doctrine_version | github:szl-holdings/.github/README.md:158 | Org page: [github.com/szl-holdings](https://github.com/szl-holdings) · Doctrine v11 · 14 unique axioms · 749 declaration |
| locked_marker | github:szl-holdings/a11oy/README.md:31 | Honesty doctrine LOCKED. DCO + Conventional Commits. |
| locked_marker | github:szl-holdings/a11oy/README.md:60 | \| Doctrine \| v11 LOCKED \| |
| trust_ceiling | github:szl-holdings/a11oy/README.md:64 | \| Trust ceiling \| 0.97 \| |
| locked_marker | github:szl-holdings/a11oy/README.md:171 | \| 8 formulas locked-proven (Lean 4) \| **LOCKED · kernel c7c0ba17** \| |
| doctrine_version | github:szl-holdings/a11oy/README.md:261 | <sub>SZL Holdings · a11oy · Doctrine v11 LOCKED · Λ = Conjecture 1 · SLSA L1 honest · L2 build-attested · L3 roadmap · N |
| locked_marker | github:szl-holdings/a11oy/README.md:261 | <sub>SZL Holdings · a11oy · Doctrine v11 LOCKED · Λ = Conjecture 1 · SLSA L1 honest · L2 build-attested · L3 roadmap · N |
| doctrine_version | github:szl-holdings/a11oy/README.md:280 | <sub>Doctrine v11 · Λ = Conjecture 1, never green · honest by design · public data only.</sub> |
| locked_marker | github:szl-holdings/a11oy-net/README.md:140 | **UNAVAILABLE**. Catalog `LOCKED-PROVEN=25` stays labelled as genome catalog, |
| trust_ceiling | github:szl-holdings/a11oy-net/README.md:142 | **Conjecture 1**, advisory and not a theorem. The trust ceiling is `0.97`, |
| doctrine_version | github:szl-holdings/anatomy/README.md:24 | <a href="https://github.com/szl-holdings/.github/tree/main/doctrine"><img src="https://img.shields.io/badge/doctrine-v11 |
| trust_ceiling | github:szl-holdings/anatomy/README.md:174 | governance bypass · self-harm), trust ceiling 0.97, read live from |
| doctrine_version | github:szl-holdings/anatomy/README.md:302 | **Honest by design (doctrine v11/v12):** |
| doctrine_version | github:szl-holdings/anatomy/README.md:363 | browser would silently ignore (doctrine v11: never fabricate): |
| doctrine_version | github:szl-holdings/anatomy/README.md:421 | …proof→organ map · AI-assurance · yarqa+PINN (MODELED) · GPU-sovereign stack (SUBSTRATE) · Doctrine v11 LOCKED · 749/14/ |
| locked_marker | github:szl-holdings/anatomy/README.md:421 | …ap · AI-assurance · yarqa+PINN (MODELED) · GPU-sovereign stack (SUBSTRATE) · Doctrine v11 LOCKED · 749/14/163 · kernel |
| doctrine_version | github:szl-holdings/anatomy/README.md:444 | <sub>Doctrine v11 · Λ = Conjecture 1 (advisory — never "green"/theorem; open) · honest by design · public data only.</su |
| doctrine_version | github:szl-holdings/ayllu/README.md:118 | Apache-2.0. Doctrine v11. Λ = Conjecture 1. |
| doctrine_version | github:szl-holdings/hatun-mcp/README.md:14 | [![Doctrine v11 LOCKED](https://img.shields.io/badge/Doctrine-v11_LOCKED-d4a444.svg)](https://github.com/szl-holdings/lu |
| locked_marker | github:szl-holdings/hatun-mcp/README.md:14 | [![Doctrine v11 LOCKED](https://img.shields.io/badge/Doctrine-v11_LOCKED-d4a444.svg)](https://github.com/szl-holdings/lu |
| doctrine_version | github:szl-holdings/hatun-mcp/README.md:371 | **Honesty (Doctrine v11 · 749/14/163):** Λ is consumed here as an input scalar in [0,1] and |
| doctrine_version | github:szl-holdings/hatun-mcp/README.md:379 | **Doctrine v11 LOCKED — 749 / 14 / 163 · Λ = Conjecture 1 (NOT a theorem) · SLSA L1 honest · L2 verified-provenance on r |
| locked_marker | github:szl-holdings/hatun-mcp/README.md:379 | **Doctrine v11 LOCKED — 749 / 14 / 163 · Λ = Conjecture 1 (NOT a theorem) · SLSA L1 honest · L2 verified-provenance on r |
| doctrine_version | github:szl-holdings/holographic-unify/README.md:24 | <a href="https://github.com/szl-holdings/.github/tree/main/doctrine"><img src="https://img.shields.io/badge/doctrine-v11 |
| doctrine_version | github:szl-holdings/holographic-unify/README.md:114 | Apache-2.0 · Doctrine v11 LOCKED · Copyright 2026 SZL Holdings. |
| locked_marker | github:szl-holdings/holographic-unify/README.md:114 | Apache-2.0 · Doctrine v11 LOCKED · Copyright 2026 SZL Holdings. |
| doctrine_version | github:szl-holdings/immune/README.md:1 | > **SZL Holdings** · Doctrine v11 · Λ = Conjecture 1 (advisory, never "green"/theorem) · canonical [a-11-oy.com](https:/ |
| doctrine_version | github:szl-holdings/immune/README.md:96 | tasking, CIA-style OSINT attribution — independently implemented under Doctrine v11. |
| doctrine_version | github:szl-holdings/immune/README.md:209 | *SZL Holdings · Doctrine v11 · honest by design · Apache-2.0* |

## Unverified categorical claims 
| type | location | text |
|---|---|---|
| formula_count | github:szl-holdings/.github/README.md:147 | - [`lutar-lean`](https://github.com/szl-holdings/lutar-lean) — Lean 4 + Mathlib proofs of the Λ aggregator (749 decl / 1 |
| locked_marker | github:szl-holdings/a11oy/README.md:31 | Honesty doctrine LOCKED. DCO + Conventional Commits. |
| locked_marker | github:szl-holdings/a11oy/README.md:60 | \| Doctrine \| v11 LOCKED \| |
| trust_ceiling | github:szl-holdings/a11oy/README.md:64 | \| Trust ceiling \| 0.97 \| |
| formula_count | github:szl-holdings/a11oy/README.md:96 | - **8 formulas locked-proven** at kernel `c7c0ba17` — receipt replay, DAG acyclicity, FIFO ordering, ledger conservation |
| locked_marker | github:szl-holdings/a11oy/README.md:171 | \| 8 formulas locked-proven (Lean 4) \| **LOCKED · kernel c7c0ba17** \| |
| formula_count | github:szl-holdings/a11oy/README.md:171 | \| 8 formulas locked-proven (Lean 4) \| **LOCKED · kernel c7c0ba17** \| |
| locked_marker | github:szl-holdings/a11oy/README.md:261 | <sub>SZL Holdings · a11oy · Doctrine v11 LOCKED · Λ = Conjecture 1 · SLSA L1 honest · L2 build-attested · L3 roadmap · N |
| locked_marker | github:szl-holdings/a11oy-net/README.md:140 | **UNAVAILABLE**. Catalog `LOCKED-PROVEN=25` stays labelled as genome catalog, |
| trust_ceiling | github:szl-holdings/a11oy-net/README.md:142 | **Conjecture 1**, advisory and not a theorem. The trust ceiling is `0.97`, |
| trust_ceiling | github:szl-holdings/anatomy/README.md:174 | governance bypass · self-harm), trust ceiling 0.97, read live from |
| locked_marker | github:szl-holdings/anatomy/README.md:421 | …ap · AI-assurance · yarqa+PINN (MODELED) · GPU-sovereign stack (SUBSTRATE) · Doctrine v11 LOCKED · 749/14/163 · kernel |
| locked_marker | github:szl-holdings/hatun-mcp/README.md:14 | [![Doctrine v11 LOCKED](https://img.shields.io/badge/Doctrine-v11_LOCKED-d4a444.svg)](https://github.com/szl-holdings/lu |
| locked_marker | github:szl-holdings/hatun-mcp/README.md:379 | **Doctrine v11 LOCKED — 749 / 14 / 163 · Λ = Conjecture 1 (NOT a theorem) · SLSA L1 honest · L2 verified-provenance on r |
| locked_marker | github:szl-holdings/holographic-unify/README.md:114 | Apache-2.0 · Doctrine v11 LOCKED · Copyright 2026 SZL Holdings. |
| locked_marker | github:szl-holdings/khipu-consensus/README.md:171 | <sub>Λ Conjecture 1 (not a theorem) · 749/14/163 v11 LOCKED (kernel `c7c0ba17`) · SLSA L1 honest · Section 889 = 5 vendo |
| locked_marker | github:szl-holdings/killinchu/README.md:64 | **LOCKED kernel `c7c0ba17` · 749 declarations · 14 axioms · 163 sorries · Doctrine v11** |
| locked_marker | github:szl-holdings/killinchu/README.md:349 | - **Doctrine v11 LOCKED** — 749/14/163 · kernel `c7c0ba17` (never bumped) |
| locked_marker | github:szl-holdings/killinchu/README.md:421 | <sub>Λ Conjecture 1 (not a theorem) · 749/14/163 v11 LOCKED · SLSA L1 honest · L2 build-attested · L3 roadmap · Section |
| locked_marker | github:szl-holdings/killinchu/README.md:488 | …<sub>Doctrine v11 LOCKED · 749/14/163 · kernel `c7c0ba17` · SLSA L1 honest · L2 build-attested (container provenance, S |
| locked_marker | github:szl-holdings/lutar-lean/README.md:49 | ### Tier 1 — LOCKED (proven, sorry-free, count machine-enforced) |
| formula_count | github:szl-holdings/lutar-lean/README.md:51 | > **Exactly 8 formulas are locked-proven: `F1, F4, F7, F11, F12, F18, F19, F22`.** |
| locked_marker | github:szl-holdings/lyte-lattice/README.md:111 | Apache-2.0 · Doctrine v11 LOCKED · Copyright 2026 SZL Holdings. |
| locked_marker | github:szl-holdings/szl-atelier/README.md:63 | Doctrine v11 LOCKED · 749/14/163 · locked-proven 8. Apache-2.0. Copyright 2026 SZL Holdings · Stephen P. Lutar Jr. · ORC |
| locked_marker | github:szl-holdings/szl-build-env/README.md:53 | > Doctrine v11 LOCKED `749/14/163` @ kernel commit `c7c0ba17`. |
| locked_marker | github:szl-holdings/szl-build-env/README.md:227 | <sub>Λ Conjecture 1 (not a theorem) · 749/14/163 v11 LOCKED (kernel `c7c0ba17`) · SLSA L1 honest · Section 889 = 5 vendo |
| trust_ceiling | github:szl-holdings/szl-constellation/README.md:92 | <sub>SZL Holdings · governed, receipted, verifiable · Λ = Conjecture 1 (advisory, never a theorem) · trust ceiling 0.97< |
| locked_marker | github:szl-holdings/szl-doctrine/README.md:76 | \| Doctrine version \| **v11 LOCKED** \| the published security/compliance contract \| |
| locked_marker | github:szl-holdings/szl-doctrine/README.md:156 | <sub>Λ Conjecture 1 (not a theorem) · 749/14/163 v11 LOCKED (kernel `c7c0ba17`) · SLSA L1 honest · Section 889 = 5 vendo |
| locked_marker | github:szl-holdings/szl-drift/README.md:26 | - Doctrine v11 LOCKED |

## Single points of failure
- maintainer concentration: top human contributor accounts for 11087/15177 (73%) of contributions across 126 repos
- bus factor per flagship (min contributors for 50% of commits): a11oy: 1, governed-receipt-spec: 1, hatun-mcp: 1, killinchu: 1, szl-eclipse: 1, szl-forge: 1, szl-frontier: 1, szl-guardrail-receipt: 1, szl-receipt: 1, szl-router: 1
- Contributor figures are per GitHub account (type User); aliases are not merged and automation-named identities are not excluded.

## Schema skew
Genuine skew (distinct version numbers within an estate schema family) is listed in 04; separator-only variants are naming inconsistencies, not skew.

## Evidence-boundary violations (integrity allowed to imply validity)
- governed-receipt-spec: Verifier reports PASS for a signature check it skipped — szl-holdings/governed-receipt-spec@2c82320a9946 (default-branch HEAD): 'sig: PASS SKIP ... signature not cryptographically verified' on ['valid/a11oy-khipu-chain.json', 'valid/a11oy-khipu-genesis.json', 'valid/lake-inference-receipt.json',
