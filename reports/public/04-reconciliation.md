# 04 — Cross-surface reconciliation

```text
STATUS: FAIL
WHAT WAS EXPECTED: every HF artifact mapped to a source and every publishing repo mapped to a target
WHAT WAS EXAMINED: 107 HF cards; 87 repo READMEs (cloned repos)
WHAT ACTUALLY RAN: link extraction from cards/READMEs, inventory lookups, pinned-SHA comparison, schema-id scan of cloned sources
WHAT PASSED: 86 artifacts linked to a living source
WHAT FAILED: 21 artifacts without a living source link; 13 repos link HF targets that do not exist; 2 pinned-version drifts; inventory claims 21 CONTRADICTED, 11 STALE
WHAT ABSTAINED: relationships not written in any card/README are invisible to this method
WHAT REMAINS UNRESOLVED: whether unlinked artifacts have an owner outside these surfaces
WHAT THIS RESULT DOES NOT PROVE: that linked artifacts were built from the linked source
```

## Coverage accounting

```text
artifacts_expected: 107 HF artifacts + 118 repos
artifacts_discovered: 107 HF artifacts; 118 repos
artifacts_examined: 107 HF cards; 87 repo READMEs (cloned repos)
artifacts_functionally_tested: NOT_TESTED (reconciliation is link/metadata based)
artifacts_not_tested: 31
denominator_state: OBSERVED
# not tested (artifact: reason)
#   cosmos: archived (README not cloned)
#   counsel: archived (README not cloned)
#   developers: archived (README not cloned)
#   docs-site: archived (README not cloned)
#   energy-attest-holo: archived (README not cloned)
#   evidence-typed-formula-governance: archived (README not cloned)
#   fail-closed-governed-ai-services: archived (README not cloned)
#   governed-inference-meter: archived (README not cloned)
#   governed-norm-holo: archived (README not cloned)
#   immune-lattice: archived (README not cloned)
#   khipu-lab: archived (README not cloned)
#   khipu-pages: archived (README not cloned)
#   lambda-gate-holo: archived (README not cloned)
#   lean-kernel: archived (README not cloned)
#   ouroboros: archived (README not cloned)
#   platform: insufficient free disk on audit host to clone (693 MB free < 1414 MB needed)
#   receipt-chain-live: archived (README not cloned)
#   szl-cookbook: archived (README not cloned)
#   szl-experiments: archived (README not cloned)
#   szl-fleet-overlay: archived (README not cloned)
#   szl-formula-ledger: archived (README not cloned)
#   szl-governed-norm: archived (README not cloned)
#   szl-kernels-live: archived (README not cloned)
#   szl-organ-integrity: archived (README not cloned)
#   szl-otel-mesh: archived (README not cloned)
#   szl-pin: clone failed
#   szl-provctl-live: archived (README not cloned)
#   szl-telemetry: archived (README not cloned)
#   szl-typesafe-triage: insufficient free disk on audit host to clone (694 MB free < 702 MB needed)
#   szl-uds-deployment: archived (README not cloned)
#   warhacker-demo: archived (README not cloned)
```

## HF artifact → canonical source

| artifact | kind | private | canonical source | state | source newer by (days) |
|---|---|---|---|---|---|
| SZLHOLDINGS/a11oy-v19-substrate | model | no | a11oy | LINKED | 23 |
| SZLHOLDINGS/szl-governed-norm | model | no | szl-governed-norm | SOURCE_ARCHIVED | -47 |
| SZLHOLDINGS/szl-lambda-gate | model | no | szl-lambda-gate | LINKED | 0 |
| SZLHOLDINGS/governed-inference-meter | model | no | governed-inference-meter | SOURCE_ARCHIVED | -25 |
| SZLHOLDINGS/szl-kernels | model | no | szl-kernels | LINKED | 23 |
| SZLHOLDINGS/szl-blocked | model | no | szl-blocked | LINKED | 0 |
| SZLHOLDINGS/szl-govsign | model | no | szl-govsign | LINKED | 15 |
| SZLHOLDINGS/szl-provctl | model | no | szl-provctl | LINKED | -3 |
| SZLHOLDINGS/szl-nemo | model | no | szl-nemo | LINKED | 13 |
| SZLHOLDINGS/szl-invariants | model | no | szl-invariants | LINKED | 4 |
| SZLHOLDINGS/szl-ouroboros | model | no | szl-ouroboros | LINKED | 17 |
| SZLHOLDINGS/szl-formulas | model | no | szl-formulas | LINKED | 16 |
| SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent | model | no | szl-forge | LINKED | 20 |
| SZLHOLDINGS/SZL-Khipu-1.5B | model | no | szl-forge | LINKED | 0 |
| SZLHOLDINGS/SZL-Khipu-1.5B-GGUF | model | no | szl-forge | LINKED | 14 |
| SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2 | model | no | szl-forge | LINKED | 9 |
| SZLHOLDINGS/SZLHOLDINGS | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/KHIPU-R2 | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/WILLAY | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/KILLINCHU-EYE | model | no | killinchu | LINKED | 23 |
| SZLHOLDINGS/YARQA-ATTN | model | no | yarqa-attn | LINKED | -19 |
| SZLHOLDINGS/A11OY-MINI | model | no | szl-forge | LINKED | 0 |
| SZLHOLDINGS/chaski | model | no | szl-forge | LINKED | 13 |
| SZLHOLDINGS/qantu | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/waman | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/chakana | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/tinku | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-receipt-attn | model | no | szl-receipt-attn | LINKED | -19 |
| SZLHOLDINGS/szl-maskmod | model | no | szl-maskmod | LINKED | 0 |
| SZLHOLDINGS/szl-block-kv | model | no | szl-block-kv | LINKED | -2 |
| SZLHOLDINGS/SZL-Khipu-1.5B-abstain | model | no | szl-forge | LINKED | 16 |
| SZLHOLDINGS/chaski-5050 | model | no | szl-forge | LINKED | 11 |
| SZLHOLDINGS/chaski-r2 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-training-scripts | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-khipu | model | no | szl-khipu | LINKED | -1 |
| SZLHOLDINGS/TinyKhipu-Nano | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/ReceiptAgent-Nano | model | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-khipu-kernels | model | no | szl-khipu | LINKED | 23 |
| SZLHOLDINGS/Moons-Nano | model | no | szl-khipu | LINKED | 13 |
| SZLHOLDINGS/MiniEmbed-Nano | model | no | szl-khipu | LINKED | 13 |
| SZLHOLDINGS/brain-navigator-r2 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v3 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/khipu-r3 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-energy-attest | model | no | szl-energy-attest | LINKED | 0 |
| SZLHOLDINGS/oac-clinical-transport-health-v1 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/oac-system-health-v1 | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2-merged | model | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora | model | no | szl-typesafe-triage | LINKED | 2 |
| SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora-study5 | model | no | szl-typesafe-triage | LINKED | 0 |
| SZLHOLDINGS/thesis-v18-formal-verification | dataset | no | a11oy | LINKED | 65 |
| SZLHOLDINGS/uds-spans-receipts | dataset | no | a11oy | LINKED | 25 |
| SZLHOLDINGS/uds-governance-receipts | dataset | no | a11oy | LINKED | 25 |
| SZLHOLDINGS/SZLHOLDINGS | dataset | no | szl-papers | LINKED | 25 |
| SZLHOLDINGS/why-we-lead | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/ouroboros-arxiv-preprint | dataset | no | a11oy | LINKED | 65 |
| SZLHOLDINGS/szl-artifacts | dataset | no | a11oy | LINKED | 65 |
| SZLHOLDINGS/lean-theorem-tree | dataset | no | a11oy | LINKED | 65 |
| SZLHOLDINGS/rag-corpus-v1 | dataset | no | szl-papers | LINKED | 65 |
| SZLHOLDINGS/lean-proofs-v1 | dataset | no | governed-receipt-spec | LINKED | 24 |
| SZLHOLDINGS/canonical-formulas-v1 | dataset | no | szl-papers | LINKED | 25 |
| SZLHOLDINGS/thesis-corpus-v18 | dataset | no | szl-papers | LINKED | 25 |
| SZLHOLDINGS/doctrine-v10-v11 | dataset | no | szl-papers | LINKED | 25 |
| SZLHOLDINGS/k-verify-benchmark-v1 | dataset | no | szl-papers | LINKED | 25 |
| SZLHOLDINGS/uds-bundles-v1 | dataset | no | szl-papers | LINKED | 65 |
| SZLHOLDINGS/readiness-runs | dataset | no | governed-receipt-spec | LINKED | 64 |
| SZLHOLDINGS/szl-lake | dataset | no | lutar-lean | LINKED | 0 |
| SZLHOLDINGS/a11oy-verifiable-corpus | dataset | no | a11oy | LINKED | 4 |
| SZLHOLDINGS/killinchu-osint-corpus | dataset | no | killinchu | LINKED | 0 |
| SZLHOLDINGS/governed-receipts-bench | dataset | no | governed-receipt-spec | LINKED | 64 |
| SZLHOLDINGS/energy-attested-runs | dataset | no | governed-receipt-spec | LINKED | 64 |
| SZLHOLDINGS/alloy-sovereign-eval-runs | dataset | no | governed-receipt-spec | LINKED | 64 |
| SZLHOLDINGS/szl-1-doctrine-sft | dataset | no | szl-forge | LINKED | 65 |
| SZLHOLDINGS/szl-second-brain-inrepo | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-quant-sft-v1 | dataset | no | szl-quant | LINKED | 0 |
| SZLHOLDINGS/test-results | dataset | no | hatun-mcp | LINKED | 24 |
| SZLHOLDINGS/governed-agent-bench | dataset | no | a11oy | LINKED | 25 |
| SZLHOLDINGS/receipted-unsloth | dataset | no | szl-forge | LINKED | 27 |
| SZLHOLDINGS/model-bom | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-frontier-covenant | dataset | no | szl-frontier | LINKED | 17 |
| SZLHOLDINGS/release-assets | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-estate-graph | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/david-leads-data | dataset | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/oac-clinical-transport-observability-synthetic | dataset | no | szl-forge | LINKED | 1 |
| SZLHOLDINGS/szl-frontier-evaluation-receipts | dataset | no | governed-receipt-spec | LINKED | -1 |
| SZLHOLDINGS/a11oy | space | no | a11oy | LINKED | 0 |
| SZLHOLDINGS/README | space | no | a11oy | LINKED | 3 |
| SZLHOLDINGS/killinchu | space | no | killinchu | LINKED | 0 |
| SZLHOLDINGS/counsel | space | no | a11oy | LINKED | 5 |
| SZLHOLDINGS/terra | space | no | a11oy | LINKED | 5 |
| SZLHOLDINGS/sentra | space | no | a11oy | LINKED | 5 |
| SZLHOLDINGS/finance | space | no | a11oy | LINKED | 5 |
| SZLHOLDINGS/lyte | space | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/vertical-services | space | no | vertical-services | LINKED | 17 |
| SZLHOLDINGS/szl-command-lab | space | no | szl-command-lab | LINKED | -1 |
| SZLHOLDINGS/david-leads | space | no | david-leads | LINKED | -1 |
| SZLHOLDINGS/szl-constellation | space | no | szl-constellation | LINKED | -1 |
| SZLHOLDINGS/szl-frontier | space | no | a11oy | LINKED | 0 |
| SZLHOLDINGS/szl-model-inference-lab | space | no | szl-forge | LINKED | 20 |
| SZLHOLDINGS/immune-lattice | space | no | immune | LINKED | 20 |
| SZLHOLDINGS/immune | space | no | immune | LINKED | -1 |
| SZLHOLDINGS/ayllu | space | no | ayllu | LINKED | -1 |
| SZLHOLDINGS/yarqa | space | no | yarqa | LINKED | -1 |
| SZLHOLDINGS/szl-atelier | space | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/holographic-unify | space | no | NO_SOURCE_LINK | NO_SOURCE_LINK | UNKNOWN |
| SZLHOLDINGS/szl-khipu | space | no | szl-khipu | LINKED | -1 |
| SZLHOLDINGS/llm-router-live | space | no | szl-router | LINKED | 0 |
| SZLHOLDINGS/szl-constellation-staging | space | no | szl-constellation | LINKED | 0 |

## Source repo → HF target

| repo | archived | state | README HF targets | missing targets | HF artifacts linking back |
|---|---|---|---|---|---|
| .github | no | CLAIMED_TARGET_MISSING | datasets/szlholdings/doctrine-v11 | datasets/szlholdings/doctrine-v11 | none |
| a11oy | no | HAS_TARGET_WITH_MISSING | spaces/szlholdings/a11oy, spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/immune, spaces/szlholdings/killinchu, spaces/szlholdings/sda, spaces/szlholdings/yarqa | spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/sda | SZLHOLDINGS/a11oy-v19-substrate, SZLHOLDINGS/thesis-v18-formal-verification, SZLHOLDINGS/uds-spans-receipts, SZLHOLDINGS/uds-governance-receipts, <private>, SZLHOLDINGS/ouroboros-arxiv-preprint, SZLHOLDINGS/szl-artifacts, <private>, <private>, SZLHOLDINGS/lean-theorem-tree, SZLHOLDINGS/a11oy-verifiable-corpus, SZLHOLDINGS/governed-agent-bench, SZLHOLDINGS/a11oy, SZLHOLDINGS/README, SZLHOLDINGS/counsel, SZLHOLDINGS/terra, SZLHOLDINGS/sentra, SZLHOLDINGS/finance, <private>, <private>, <private>, SZLHOLDINGS/szl-frontier |
| <private> | no | NO_PUBLISHED_TARGET | none | none | none |
| a11oy-net | no | HAS_TARGET | spaces/szlholdings/killinchu | none | none |
| anatomy | no | CLAIMED_TARGET_MISSING | datasets/szlholdings/governed-receipts-bench, datasets/szlholdings/szl-lake, datasets/szlholdings/test-results, spaces/szlholdings/a11oy, spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/immune, spaces/szlholdings/killinchu, spaces/szlholdings/readme | spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/sda | none |
| ayllu | no | HAS_TARGET | spaces/szlholdings/ayllu | none | SZLHOLDINGS/ayllu |
| ayllu-hf-space | no | HAS_TARGET | spaces/szlholdings/ayllu | none | none |
| counsel | yes | NO_PUBLISHED_TARGET | none | none | none |
| david-leads | no | HAS_TARGET | datasets/szlholdings/david-leads-data, spaces/szlholdings/david-leads | none | SZLHOLDINGS/david-leads |
| energy-attest-holo | yes | NO_PUBLISHED_TARGET | none | none | none |
| governed-inference-meter | yes | HAS_TARGET | none | none | SZLHOLDINGS/governed-inference-meter |
| governed-norm-holo | yes | NO_PUBLISHED_TARGET | none | none | none |
| governed-receipt-spec | no | HAS_TARGET_WITH_MISSING | datasets/szlholdings/governed-receipts-bench, spaces/szlholdings/governed-receipt-verifier | spaces/szlholdings/governed-receipt-verifier | SZLHOLDINGS/lean-proofs-v1, SZLHOLDINGS/readiness-runs, SZLHOLDINGS/governed-receipts-bench, SZLHOLDINGS/energy-attested-runs, SZLHOLDINGS/alloy-sovereign-eval-runs, SZLHOLDINGS/szl-frontier-evaluation-receipts |
| hatun-mcp | no | HAS_TARGET | none | none | SZLHOLDINGS/test-results |
| holographic-unify | no | HAS_TARGET | spaces/szlholdings/readme | none | none |
| immune | no | HAS_TARGET | none | none | SZLHOLDINGS/immune-lattice, SZLHOLDINGS/immune |
| khipu-consensus | no | CLAIMED_TARGET_MISSING | spaces/szlholdings/khipu-constellation | spaces/szlholdings/khipu-constellation | none |
| khipu-lab | yes | NO_PUBLISHED_TARGET | none | none | none |
| killinchu | no | HAS_TARGET_WITH_MISSING | datasets/szlholdings/governed-receipts-bench, datasets/szlholdings/szl-lake, spaces/szlholdings/a11oy, spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/immune, spaces/szlholdings/killinchu, spaces/szlholdings/readme | spaces/szlholdings/anatomy, spaces/szlholdings/cosmos, spaces/szlholdings/governed-receipt-verifier, spaces/szlholdings/holographic, spaces/szlholdings/sda | SZLHOLDINGS/KILLINCHU-EYE, SZLHOLDINGS/killinchu-osint-corpus, SZLHOLDINGS/killinchu |
| lambda-gate-holo | yes | NO_PUBLISHED_TARGET | none | none | none |
| lutar-lean | no | HAS_TARGET_WITH_MISSING | spaces/szlholdings/lambda-aggregator-live | spaces/szlholdings/lambda-aggregator-live | SZLHOLDINGS/szl-lake |
| lyte-lattice | no | HAS_TARGET | spaces/szlholdings/lyte, spaces/szlholdings/readme | none | none |
| lyte-services | no | HAS_TARGET | spaces/szlholdings/lyte | none | none |
| nexus | no | HAS_TARGET | spaces/szlholdings/readme | none | none |
| platform | no | HAS_TARGET | none | none | <private>, <private> |
| receipt-chain-live | yes | NO_PUBLISHED_TARGET | none | none | none |
| sda | no | HAS_TARGET | spaces/szlholdings/readme | none | none |
| szl-atelier | no | HAS_TARGET | spaces/szlholdings/szl-atelier, spaces/szlholdings/szl-khipu | none | none |
| szl-block-kv | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-block-kv |
| szl-blocked | no | HAS_TARGET | models/szlholdings/szl-blocked | none | SZLHOLDINGS/szl-blocked |
| szl-command-lab | no | HAS_TARGET | spaces/szlholdings/readme, spaces/szlholdings/szl-command-lab | none | SZLHOLDINGS/szl-command-lab |
| szl-constellation | no | HAS_TARGET | datasets/szlholdings/killinchu-osint-corpus, datasets/szlholdings/szl-lake, models/szlholdings/szl-khipu-1.5b, spaces/szlholdings/szl-constellation | none | SZLHOLDINGS/szl-constellation, SZLHOLDINGS/szl-constellation-staging |
| szl-energy-attest | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-energy-attest |
| szl-experiments | yes | NO_PUBLISHED_TARGET | none | none | none |
| szl-forge | no | HAS_TARGET | datasets/szlholdings/oac-clinical-transport-observability-synthetic, models/szlholdings/oac-system-health-v1, models/szlholdings/szl-forge-1.5b-receiptagent, models/szlholdings/szl-khipu-1.5b, models/szlholdings/szl-khipu-1.5b-gguf, models/szlholdings/szl-receiptagent-qwen35-0.8b-v2 | none | SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent, SZLHOLDINGS/SZL-Khipu-1.5B, SZLHOLDINGS/SZL-Khipu-1.5B-GGUF, SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2, SZLHOLDINGS/A11OY-MINI, SZLHOLDINGS/chaski, SZLHOLDINGS/SZL-Khipu-1.5B-abstain, SZLHOLDINGS/chaski-5050, SZLHOLDINGS/chaski-r2, SZLHOLDINGS/brain-navigator-r2, SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v3, SZLHOLDINGS/khipu-r3, SZLHOLDINGS/oac-clinical-transport-health-v1, SZLHOLDINGS/oac-system-health-v1, SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2-merged, SZLHOLDINGS/szl-1-doctrine-sft, SZLHOLDINGS/receipted-unsloth, SZLHOLDINGS/oac-clinical-transport-observability-synthetic, SZLHOLDINGS/szl-model-inference-lab |
| szl-formulas | no | HAS_TARGET | models/szlholdings/szl-formulas | none | SZLHOLDINGS/szl-formulas |
| szl-frontier | no | HAS_TARGET | spaces/szlholdings/szl-frontier | none | SZLHOLDINGS/szl-frontier-covenant |
| szl-governed-norm | yes | HAS_TARGET | none | none | SZLHOLDINGS/szl-governed-norm |
| szl-govsign | no | HAS_TARGET_WITH_MISSING | models/szlholdings/szl-govsign, spaces/szlholdings/govsign-live | spaces/szlholdings/govsign-live | SZLHOLDINGS/szl-govsign |
| szl-gpu-bridge | no | HAS_TARGET | none | none | <private> |
| szl-guardrail-receipt | no | CLAIMED_TARGET_MISSING | spaces/szlholdings/guardrail-receipt | spaces/szlholdings/guardrail-receipt | none |
| szl-invariants | no | HAS_TARGET | models/szlholdings/szl-invariants | none | SZLHOLDINGS/szl-invariants |
| szl-kernels | no | HAS_TARGET_WITH_MISSING | datasets/szlholdings/szl-lake, models/szlholdings/a11oy-v19-substrate, models/szlholdings/governed-inference-meter, models/szlholdings/szl-blocked, models/szlholdings/szl-formulas, models/szlholdings/szl-governed-norm, models/szlholdings/szl-govsign, models/szlholdings/szl-invariants, models/szlholdings/szl-kernels, models/szlholdings/szl-lambda-gate | spaces/szlholdings/holographic | SZLHOLDINGS/szl-kernels |
| szl-kernels-live | yes | NO_PUBLISHED_TARGET | none | none | none |
| szl-khipu | no | HAS_TARGET_WITH_MISSING | models/szlholdings/szl-khipu, spaces/szlholdings/anatomy | spaces/szlholdings/anatomy | SZLHOLDINGS/szl-khipu, SZLHOLDINGS/szl-khipu-kernels, SZLHOLDINGS/Moons-Nano, SZLHOLDINGS/MiniEmbed-Nano, SZLHOLDINGS/szl-khipu |
| szl-lake | no | HAS_TARGET | datasets/szlholdings/szl-lake | none | none |
| szl-lambda-gate | no | HAS_TARGET | models/szlholdings/szl-lambda-gate | none | SZLHOLDINGS/szl-lambda-gate |
| szl-maskmod | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-maskmod |
| szl-nemo | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-nemo |
| szl-ouroboros | no | HAS_TARGET | models/szlholdings/szl-ouroboros | none | SZLHOLDINGS/szl-ouroboros |
| szl-papers | no | HAS_TARGET | none | none | SZLHOLDINGS/SZLHOLDINGS, SZLHOLDINGS/rag-corpus-v1, SZLHOLDINGS/canonical-formulas-v1, SZLHOLDINGS/thesis-corpus-v18, SZLHOLDINGS/doctrine-v10-v11, SZLHOLDINGS/k-verify-benchmark-v1, SZLHOLDINGS/uds-bundles-v1 |
| szl-provctl | no | HAS_TARGET_WITH_MISSING | models/szlholdings/szl-provctl, spaces/szlholdings/szl-provctl-live | spaces/szlholdings/szl-provctl-live | SZLHOLDINGS/szl-provctl |
| szl-provctl-live | yes | NO_PUBLISHED_TARGET | none | none | none |
| szl-quant | no | HAS_TARGET | datasets/szlholdings/szl-quant-sft-v1 | none | SZLHOLDINGS/szl-quant-sft-v1 |
| szl-real-estate | no | HAS_TARGET | spaces/szlholdings/terra | none | none |
| szl-receipt-attn | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-receipt-attn |
| szl-router | no | HAS_TARGET | spaces/szlholdings/llm-router-live | none | SZLHOLDINGS/llm-router-live |
| szl-serve | no | CLAIMED_TARGET_MISSING | models/szlholdings/szl-khipu-1.5b-gguf, spaces/szlholdings/szl-forge-lab, spaces/szlholdings/szl-model-inference-lab | spaces/szlholdings/szl-forge-lab | none |
| szl-trust | no | HAS_TARGET | datasets/szlholdings/szl-lake, models/szlholdings/szl-kernels | none | none |
| szl-typesafe-triage | no | HAS_TARGET | none | none | SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora, SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora-study5 |
| vertical-services | no | HAS_TARGET | none | none | SZLHOLDINGS/vertical-services |
| yarqa | no | HAS_TARGET | none | none | SZLHOLDINGS/yarqa |
| YARQA-ATTN | no | HAS_TARGET | none | none | SZLHOLDINGS/YARQA-ATTN |

## Version drift (pinned source commit vs source HEAD)

| artifact | repo | pinned | source HEAD |
|---|---|---|---|
| SZLHOLDINGS/szl-lake | lutar-lean | 3f3ad80d | 75a4a3112287 |
| SZLHOLDINGS/governed-agent-bench | a11oy | 1b40fcbe0f65c1ad1e07776f83aa01abb067e864 | 53366a17087c |

## Naming inconsistencies

none observed between HF ids and GitHub repo names

| schema family | version | spellings | repos |
|---|---|---|---|
| szl.receipt-verification | 1 | szl.receipt-verification.v1, szl.receipt-verification/v1 | anatomy, vertical-services |

## Receipt/schema identifiers in use

284 receipt-like identifiers found in cloned sources: 252 estate-defined, 3 standard media types (DSSE/in-toto), 29 test/example ids. Scan scope: all cloned repos.

| estate schema id | repos |
|---|---|
| DecisionReceipt.v2 | a11oy |
| DecisionReceipt.v3 | a11oy |
| SZL.Energy.Receipt.v1 | a11oy |
| a11oy.holographic.brain-evidence.v1 | a11oy |
| application/vnd.szl.a11oy-receipt+json | a11oy |
| application/vnd.szl.agent.receipt+json;v=2 | a11oy, killinchu, szl-substrate |
| application/vnd.szl.amaru.receipt+json | a11oy |
| application/vnd.szl.brain_jack.receipt+json | a11oy |
| application/vnd.szl.frontier-operation-evidence.v1+json | a11oy |
| application/vnd.szl.guardrail-receipt+json | szl-guardrail-receipt |
| application/vnd.szl.khipu+json | .github, a11oy, governed-receipt-spec, killinchu |
| application/vnd.szl.khipu-receipt+json;v=1 | a11oy, killinchu, szl-substrate |
| application/vnd.szl.khipu.organ-verdict+json | khipu-consensus, szl-mesh |
| application/vnd.szl.ops.receipt+json | killinchu |
| application/vnd.szl.organism.receipt+json | killinchu |
| application/vnd.szl.receipt+json | .github, a11oy, anatomy, ayllu, hatun-mcp, killinchu, szl-lake, szl-substrate |
| application/vnd.szl.rosie_companion.receipt+json | a11oy, killinchu, szl-substrate |
| david.evidence-constellation.v1 | david-leads |
| github-actions-evidence-verification.v1 | a11oy |
| governed-agent-receipt/0.1 | a11oy |
| https://a-11-oy.com/schemas/authorization-receipt.schema.json | a11oy |
| https://a-11-oy.com/schemas/brain-row-provenance-license-crosswalk-receipt.v1.json | a11oy |
| https://a-11-oy.com/schemas/compute-pool-inference-receipt.v1.schema.json | a11oy |
| https://a-11-oy.com/schemas/evidenceos/claim-atomize-request.v1.schema.json | a11oy |
| https://a-11-oy.com/schemas/evidenceos/claim-evaluate-request.v1.schema.json | a11oy |
| https://a-11-oy.com/schemas/evidenceos/public-claim-manifest.v1.schema.json | a11oy |
| https://a-11-oy.com/schemas/evidenceos/public-claim-report.v1.schema.json | a11oy |
| https://a-11-oy.com/schemas/oro/v1/barrier-receipt.schema.json | a11oy |
| https://a-11-oy.com/schemas/puriq-receipt-v1.json | a11oy, david-leads |
| https://a-11-oy.com/schemas/receipt-agent-artifact-reconciliation.v1.json | a11oy |
| https://a-11-oy.com/schemas/receipt-agent-public-candidate-qualification-receipt.v1.json | a11oy |
| https://a-11-oy.com/schemas/szl-forge-receipt-agent-draft-v1.json | a11oy |
| https://a-11-oy.com/schemas/szl-khipu-second-brain.schema.json | a11oy |
| https://a-11-oy.com/schemas/szl-receipt-agent-admission-manifest-v1.json | a11oy |
| https://a-11-oy.com/schemas/szl-receipt-agent-evaluation-manifest-v1.json | a11oy |
| https://a-11-oy.com/schemas/szl-receipt-agent-output-v1.json | a11oy |
| https://a-11-oy.com/schemas/szl-receipt-agent-release-manifest-v1.json | a11oy |
| https://github.com/szl-holdings/governed-receipt-spec/schema/governed-receipt.schema.json | a11oy-net, governed-receipt-spec |
| https://huggingface.co/datasets/szl-holdings/uds-observability/schemas/receipt_schema.json | a11oy |
| https://schemas.szlholdings.com/khipu-package/v0.1 | szl-platform |
| https://szl.ai/schemas/receiptagent-v3-release-manifest-v1.json | szl-forge |
| https://szl.ai/schemas/receiptagent-v3/authenticated-receipt.schema.json | szl-forge |
| https://szl.holdings/khipu-governed-inference/v1 | a11oy |
| https://szl.holdings/schemas/receipt-agent-qwen35-v3-output.json | szl-forge |
| https://szl.holdings/schemas/receipt-agent-qwen35-v3-request.json | szl-forge |
| khipu-causal-lm-kv-state/v0.1 | szl-khipu |
| khipu-checkpoint/v1 | a11oy |
| khipu-int8-quant/v0.1 | szl-khipu |
| khipu-inventory-spec-comparison/v0.1 | szl-khipu |
| khipu-model-weight-inventory-digest/v0.1 | szl-khipu |
| khipu-model-weight-inventory/v0.1 | szl-khipu |
| khipu-safetensors-causal-lm-mapping/v0.1 | szl-khipu |
| khipu-safetensors-decoder-mapping/v0.1 | szl-khipu |
| khipu-safetensors-file-inventory/v0.1 | szl-khipu |
| khipu-target-budget/v0.1 | szl-khipu |
| khipu-tokenizer-artifact-binding/v0.1 | szl-khipu |
| khipu-transformer-readiness/v0.1 | szl-khipu |
| khipu-x1-source-lock/v0.1 | szl-khipu |
| szl-bench-receipt/v3 | frontier-bench |
| szl-khipu-x1-upstream-map-v1 | khipu-x1 |
| szl-oac/transport-health-artifact-receipt/v1 | szl-forge |
| szl-oac/transport-health-dataset-receipt/v1 | szl-forge |
| szl.a11oy.assurance.evidence-pack.envelope.v1 | a11oy |
| szl.a11oy.assurance.evidence-pack.v1 | a11oy |
| szl.a11oy.brain.energy.receipt.v1 | a11oy |
| szl.a11oy.code_receipt/v1 | a11oy |
| szl.a11oy.owned-khipu-cortex-error/v1 | a11oy |
| szl.a11oy.owned-khipu-live-proof/v1 | a11oy |
| szl.a11oy.specdec.receipt.v1 | a11oy |
| szl.agent.master_receipt/v1 | a11oy, killinchu, szl-substrate |
| szl.agent.receipt/v2 | a11oy, killinchu, szl-substrate |
| szl.anatomy-evidence/v1 | a11oy, anatomy, killinchu |
| szl.anatomy-integrity-receipt/v1 | anatomy |
| szl.anatomy.covenant-cockpit/receipts/v1 | a11oy, anatomy |
| szl.ayllu.ask-receipt/v1 | ayllu |
| szl.ayllu.council-receipt/v2 | a11oy |
| szl.ayllu.counsel-receipt/v1 | ayllu |
| szl.ayllu.evidence-bound-council/v2 | a11oy, ayllu |
| szl.ayllu.psyche-receipt/v1 | ayllu |
| szl.body_of_evidence/v1 | a11oy, killinchu, szl-substrate |
| szl.bounded-lora-training-receipt/v1 | a11oy |
| szl.brain-quantum-evidence-info.v1 | a11oy |
| szl.brain-row-evidence-gap.v1 | a11oy |
| szl.brain-row-provenance-license-crosswalk-receipt.v1 | a11oy |
| szl.brain.artifact-receipt.v1 | a11oy |
| szl.brain.corpus-bridge-receipt.v1 | a11oy |
| szl.brain.corpus-evidence.v1 | a11oy |
| szl.brain.evidence-evaluation-preregistration.v1 | a11oy |
| szl.brain.evidence-evaluation-results.v1 | a11oy |
| szl.brain.evidence-manifest.v1 | a11oy |
| szl.brain.evidence-qrels.v1 | a11oy |
| szl.brain.reranker.receipt.v1 | a11oy |
| szl.brain.semantic-index.receipt.v1 | a11oy |
| szl.brain.signed-inference-receipt/v1 | a11oy |
| szl.brain.verifiable-answer-receipt/v1 | a11oy |
| szl.brain_jack.receipt/v1 | a11oy |
| szl.budget_action.receipt/v1 | .github |
| szl.chaos.receipt/v1 | .github |
| szl.claim-integrity-receipt/v1 | vertical-services |
| szl.connector-evidence-resolution/v1 | vertical-services |
| szl.connector-evidence-snapshot/v1 | vertical-services |
| szl.degradation.receipt/v1 | .github, a11oy |
| szl.deployment-review-receipt/v1 | .github |
| szl.deployment-source-evidence/v1 | sda |
| szl.estate-alignment-receipt/v1 | .github |
| szl.estate-deadman-receipt/v1 | .github |
| szl.estate-release-train.receipt/v1 | szl-forge |
| szl.evidence-bearing-ui/v8 | a11oy |
| szl.evidence-file-manifest/v1 | szl-forge |
| szl.evidence-index/v1 | lyte-services |
| szl.finance-receipts/v1 | vertical-services |
| szl.finance-receipts/verify/v1 | vertical-services |
| szl.finance.computation-receipt/v1 | a11oy |
| szl.forge-capacity-probe-receipt.v1 | a11oy |
| szl.forge-final-input-integrity-receipt.v1 | a11oy |
| szl.forge-gpu-load-admission-receipt.v1 | a11oy |
| szl.forge-input-snapshot-receipt.v1 | a11oy |
| szl.forge-preflight-receipt.v1 | a11oy |
| szl.forge-receipt-draft.v1 | a11oy |
| szl.forge-reload-evaluation-receipt.v1 | a11oy |
| szl.forge-resume-admission-receipt.v1 | a11oy |
| szl.forge-training-receipt.v1 | a11oy |
| szl.forge.hf-frontier-receipt.v2 | szl-forge |
| szl.forge.hf-kernels-0.17-evidence.v1 | szl-forge |
| szl.forge.inference-receipt/v1 | szl-forge |
| szl.forge.lab-receipt-envelope/v1 | szl-forge |
| szl.forge.lora-merge-receipt.v1 | szl-forge |
| szl.forge.production-inference-receipt/v2 | szl-forge |
| szl.forge.receipt/v1 | szl-forge |
| szl.forge.receiptagent-merged-candidate.v1 | szl-forge |
| szl.forge.trl-activation-offload-evidence.v1 | szl-forge |
| szl.formula-training-admission-artifact-receipt.v1 | a11oy |
| szl.frontier-operation-evidence.v1 | a11oy |
| szl.frontier-receipt-validation/v1 | .github |
| szl.frontier.evaluation-evidence-projection.v1 | szl-frontier |
| szl.frontier.evidence/v1 | szl-frontier |
| szl.frontier.nemo-model-wave-witness-envelope.v1 | szl-nemo |
| szl.frontier.terminal-evidence-verification.v1 | szl-forge |
| szl.frontier.wave4-receipt/v1 | szl-frontier |
| szl.gate_decision.receipt/v1 | .github, a11oy |
| szl.gdw.delta-update-receipt/v1 | a11oy |
| szl.gdw.kernel-receipt/v1 | a11oy |
| szl.gdw.transaction-receipt/v1 | a11oy |
| szl.gdw.transient-effect-recovery-receipt/v2 | a11oy |
| szl.governed-receipt/v8 | a11oy |
| szl.harness_apply.receipt/v1 | a11oy |
| szl.hatun-puriq-review-receipt/v1 | puriq-live |
| szl.hatun-review-receipt/v2 | vertical-services |
| szl.hatun.evidence.v1 | a11oy, killinchu |
| szl.hf-deployment-receipt/v3 | szl-khipu |
| szl.hf-gdw-transient-recovery-evidence/v1 | a11oy |
| szl.immune-nexus-receipt-read/v1 | immune |
| szl.immune-nexus-receipt/v1 | immune |
| szl.incident.receipt/v1 | .github |
| szl.invariants-release-evidence-inspection/v1 | szl-forge |
| szl.khipu-abstention-bench/v1 | szl-khipu |
| szl.khipu.compound-second-brain.v1 | a11oy |
| szl.khipu.cosign-keys/v1 | .github, szl-lake |
| szl.khipu.demo/v1 | a11oy, killinchu, szl-substrate |
| szl.khipu.distinct-candidate-witness/v1 | szl-forge |
| szl.khipu.distinct-candidate/v1 | szl-forge |
| szl.khipu.empty-chain-manifest/v1 | szl-lake |
| szl.khipu.multi-witness-receipt/v1 | khipu-consensus |
| szl.khipu.organ_verdict/v1 | a11oy, david-leads, khipu-consensus, killinchu, szl-mesh, szl-substrate |
| szl.khipu.receipt/v1 | lutar-lean, szl-lake |
| szl.khipu.second-brain-live-verification.v1 | a11oy |
| szl.khipu.verify_op/v1 | a11oy, killinchu, szl-substrate |
| szl.khipu.witness-registry/v1 | khipu-consensus |
| szl.killinchu-dsse-verify/v1 | killinchu |
| szl.killinchu.defend-receipt/v1 | killinchu |
| szl.killinchu.receipt/v1 | killinchu |
| szl.llm_route.lambda_receipt/v1 | a11oy, killinchu, szl-substrate |
| szl.lyte-observation-receipt/v3 | lyte-services |
| szl.lyte-ui-browser-evidence/v1 | lyte-services |
| szl.lyte.forecast-inspection-envelope/v1 | a11oy |
| szl.lyte.hf-evidence/v1 | lyte-services |
| szl.lyte.receipt-page/v1 | lyte-services |
| szl.lyte.receipt-view/v1 | lyte-services |
| szl.mosaic.receipt/v1 | a11oy, killinchu |
| szl.nemo.activation-offload-calibration-receipt.v1 | a11oy |
| szl.nemo.base-fetch-receipt.v1 | a11oy |
| szl.nemo.capacity-probe-receipt.v1 | a11oy |
| szl.nemo.execution-lane-receipt.v1 | a11oy |
| szl.nemo.frontier-qualification-receipt.v1 | szl-forge, szl-nemo |
| szl.nemo.inference-envelope.v1 | a11oy, szl-forge, szl-nemo |
| szl.nemo.low-vram-calibration-receipt.v1 | a11oy |
| szl.nemo.preflight-receipt.v1 | a11oy |
| szl.nemo.reload-evaluation-receipt.v1 | a11oy |
| szl.nemo.training-evidence.v1 | a11oy |
| szl.nemo.training-receipt.v1 | a11oy |
| szl.numerics.network-namespace-evidence/v1 | a11oy |
| szl.offline-retrieval-training-receipt/v1 | szl-kernels |
| szl.ouroboros-governance-ablation-receipt/v1 | a11oy |
| szl.pcai.receipt/v1 | a11oy |
| szl.production-audit-receipt/v5 | .github |
| szl.public-receipt-verifier/manifest/v1 | a11oy, killinchu |
| szl.quant-live-benchmark-receipt.v1 | a11oy |
| szl.rag.lambda_receipt/v1 | a11oy, killinchu, szl-substrate |
| szl.rag_query.receipt/v1 | a11oy |
| szl.receipt-agent-admission-manifest.v1 | a11oy |
| szl.receipt-agent-binding.v1 | a11oy |
| szl.receipt-agent-evaluation-manifest.v1 | a11oy |
| szl.receipt-agent-output.v1 | a11oy |
| szl.receipt-agent-public-candidate-heldout-contract.v1 | a11oy |
| szl.receipt-agent-public-candidate-qualification-receipt.v1 | a11oy |
| szl.receipt-agent-public-candidate-qualification-refusal.v1 | a11oy |
| szl.receipt-agent-release-manifest.v1 | a11oy |
| szl.receipt-agent-verifier-result.v1 | a11oy |
| szl.receipt-checkpoint/v1 | szl-kernels |
| szl.receipt-verification.v1 | vertical-services |
| szl.receipt-verification/v1 | anatomy |
| szl.receipt.replay.v1 | a11oy |
| szl.receipt_shape/v1 | .github |
| szl.receiptagent-artifact-reconciliation.v1 | a11oy |
| szl.receiptagent-tournament/v1 | szl-forge |
| szl.receiptagent-v3-containment-probe/v1 | szl-forge |
| szl.receiptagent-v3-curriculum-manifest/v2 | szl-forge |
| szl.receiptagent-v3-curriculum-spec/v1 | szl-forge |
| szl.receiptagent-v3-receipt-signing-trust-policy/v1 | szl-forge |
| szl.receiptagent-v3-release-manifest/v1 | szl-forge |
| szl.receiptagent-v3-supervision-policy/v2 | szl-forge |
| szl.receiptagent-v3-training-bundle/v1 | szl-forge |
| szl.research-evidence-contract.v1 | a11oy |
| szl.resilience.ship.receipt/v1 | .github |
| szl.resilience.skip.receipt/v1 | .github |
| szl.restore_drill.receipt/v1 | .github |
| szl.rosie_companion.receipt/v1 | a11oy, killinchu, szl-substrate |
| szl.router-receipt/v1 | a11oy, szl-build-env |
| szl.run-receipt/v1 | szl-command-lab |
| szl.sentra.receipt/v1 | a11oy |
| szl.series-a-receipt-recovery-miss/v1 | a11oy |
| szl.series-a-receipt-recovery/v1 | a11oy |
| szl.series-a-receipts/v1 | a11oy |
| szl.sorry-closer-receipt/v1 | lutar-lean |
| szl.static-deployment-source-evidence/v1 | killinchu |
| szl.training.receipt.v1 | killinchu |
| szl.training.runtime.receipt.v1 | a11oy |
| szl.training_receipt.v1 | szl-forge, szl-khipu |
| szl.training_receipt.v2 | a11oy, a11oy-net, szl-atelier |
| szl.vertical-decision-receipt.v1 | vertical-services |
| szl.vertical-decision-receipt.v2 | vertical-services |
| szl.vertical-forge.receipt/v3 | a11oy, szl-vertical-forge |
| szl.vertical-intelligence-invocation-receipt/v1 | vertical-services |
| szl.vertical-intelligence-live-evidence/v1 | vertical-services |
| szl.vertical-intelligence-plan-receipt/v1 | vertical-services |
| szl.vertical-receipt/v1 | vertical-services |
| szl.vessels-proof-receipt/v8 | a11oy-net |
| szl.wave26.lambda-attnres-evidence/v1 | a11oy |
| szl.wire_d.hop_receipt/v1 | a11oy, killinchu |
| urn:szl:governance:evidence:v1 | a11oy |
| urn:szl:governance:receipt:v1 | a11oy |
| urn:szl:khipu-command-system:v1 | szl-brand |

### Version skew within an estate schema family (distinct version numbers only)

| family | versions | ids | repos |
|---|---|---|---|
| DecisionReceipt | 2, 3 | DecisionReceipt.v2, DecisionReceipt.v3 | a11oy |
| szl.training_receipt | 1, 2 | szl.training_receipt.v1, szl.training_receipt.v2 | a11oy, a11oy-net, szl-atelier, szl-forge, szl-khipu |
| szl.vertical-decision-receipt | 1, 2 | szl.vertical-decision-receipt.v1, szl.vertical-decision-receipt.v2 | vertical-services |

## Public inventory recount vs stated counts

HF anonymous listing at 2026-09-25T16:34:27Z: models 49, datasets 35, spaces 22. GitHub: 118 public of 118 discovered repos (authenticated org listing at 2026-09-25T17:35:31Z).

| location | private source | claim | verdict | evidence |
|---|---|---|---|---|
| github:szl-holdings/governance-as-code/README.md:18 | no | \| Estate \| `tools/spaces_audit.py` \| READ_ONLY audit of all 45 Spaces; signs a receipt for its own run \| | CONTRADICTED | undated claim 45 != live public 22 (authenticated total 28) |
| github:szl-holdings/szl-constellation/README.md:61 | no | …ale check: [SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 49 models, 41 datasets, and 27 Spaces (p | STALE | claimed 41 observed 2026-09-23; live 35 observed 2026-09-25T16:34:27Z; drift -6 |
| github:szl-holdings/szl-constellation/README.md:61 | no | …LDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 49 models, 41 datasets, and 27 Spaces (public inventory s | STALE | claimed 27 observed 2026-09-23; live 22 observed 2026-09-25T16:34:27Z; drift -5 |
| github:szl-holdings/szl-gov/README.md:44 | no | 100 GitHub repos (59 active public · 36 archived public · 5 private — GitHub API census 2026-08-30) · 45 HF Spaces (28 D | STALE | claimed 43 observed 2026-08-30; live 49 observed 2026-09-25T16:34:27Z; drift +6 |
| github:szl-holdings/szl-gov/README.md:44 | no | 100 GitHub repos (59 active public · 36 archived public · 5 private — GitHub API census 2026-08-30) · 45 HF Spaces (28 D | STALE | claimed 36 observed 2026-08-30; live 35 observed 2026-09-25T16:34:27Z; drift -1 |
| github:szl-holdings/szl-gov/README.md:51 | no | - All 7 public Spaces probed RUNNING with HEAD SHA (`audit_data/probes/`) | STALE | claimed 7 observed 2026-08-30; live 22 observed 2026-09-25T16:34:27Z; drift +15 |
| github:szl-holdings/szl-gov/README.md:52 | no | - 45 Spaces tiered: 5 FLAGSHIP (recommended), 38 LAB, 1 SUPPORTING, 1 ORG_CARD | STALE | claimed 45 observed 2026-08-30; live 22 observed 2026-09-25T16:34:27Z; drift -23 |
| github:szl-holdings/szl-gov/README.md:55 | no | - Backlink coverage measured at 10/43 models; 3 patches staged, 30 Spaces still need `models:` lines | STALE | claimed 43 observed 2026-08-30; live 49 observed 2026-09-25T16:34:27Z; drift +6 |
| hf:dataset:SZLHOLDINGS/thesis-v18-formal-verification/README.md:109 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · Doctrine v11 LOCKED* | CONTRADICTED | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/thesis-v18-formal-verification/README.md:109 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · Doctrine v11 LOCKED* | CONTRADICTED | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | no | …*SZLHOLDINGS · 13 Spaces / 28 datasets / 3 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 13 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | no | …*SZLHOLDINGS · 13 Spaces / 28 datasets / 3 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 28 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-spans-receipts/README.md:133 | no | …*SZLHOLDINGS · 13 Spaces / 28 datasets / 3 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 3 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 25 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 27 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/uds-governance-receipts/README.md:115 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · [HF org](https://huggingface.co/SZLHOL | CONTRADICTED | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · [HF org](https://huggingface.co/SZLHOL | CONTRADICTED | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/ouroboros-arxiv-preprint/README.md:106 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · [HF org](https://huggingface.co/SZLHOL | CONTRADICTED | undated claim 8 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 25 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 27 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/szl-artifacts/README.md:144 | no | …*SZLHOLDINGS · 25 Spaces / 27 datasets / 9 models · Lean 749 declarations · 163 sorries (112 baseline + 51 Putnam) · 12 | CONTRADICTED | undated claim 9 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/lean-theorem-tree/README.md:111 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · Doctrine v11 LOCKED* | CONTRADICTED | undated claim 17 != live public 22 (authenticated total 28) |
| hf:dataset:SZLHOLDINGS/lean-theorem-tree/README.md:111 | no | *SZL Holdings · 17 Spaces / 29 datasets / 8 models · Lean 749/14/163 @ c7c0ba17 · Doctrine v11 LOCKED* | CONTRADICTED | undated claim 29 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:12 | no | Canonical CycloneDX 1.5 Model BOM registry for all 44 public models under the | CONTRADICTED | undated claim 44 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:60 | no | 44/44 public models. The new BOM follows the same CycloneDX 1.5 schema | STALE | claimed 44 observed 2026-08-31; live 49 observed 2026-09-25T16:34:27Z; drift +5 |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:66 | no | extended 28 → 30 rows so the register covers **all 30 public datasets**. | STALE | claimed 30 observed 2026-08-31; live 35 observed 2026-09-25T16:34:27Z; drift +5 |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:70 | no | time, read via the HF API and connector listing: **44 models / 30 datasets / | CONTRADICTED | undated claim 44 != live public 49 (authenticated total 49) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:70 | no | time, read via the HF API and connector listing: **44 models / 30 datasets / | CONTRADICTED | undated claim 30 != live public 35 (authenticated total 43) |
| hf:dataset:SZLHOLDINGS/model-bom/README.md:71 | no | 47 Spaces**. Register sha256 at this refresh: | CONTRADICTED | undated claim 47 != live public 22 (authenticated total 28) |
| hf:space:SZLHOLDINGS/README/README.md:83 | no | …**21 public Spaces, 46 models, 35 datasets**, observed **2026-09-10T03:20:41Z** under anonymous public-only `hf-public- | STALE | claimed 21 observed 2026-09-10T03:20:41Z; live 22 observed 2026-09-25T16:34:27Z; drift +1 |
| hf:space:SZLHOLDINGS/README/README.md:83 | no | …**21 public Spaces, 46 models, 35 datasets**, observed **2026-09-10T03:20:41Z** under anonymous public-only `hf-public- | STALE | claimed 46 observed 2026-09-10T03:20:41Z; live 49 observed 2026-09-25T16:34:27Z; drift +3 |
