# 03 — Hugging Face estate audit: SZLHOLDINGS

```text
STATUS: FAIL
WHAT WAS EXPECTED: every model, dataset and Space authored by SZLHOLDINGS (120 in the authenticated listing)
WHAT WAS EXAMINED: 107 artifacts (metadata, card, file list)
WHAT ACTUALLY RAN: Hub API enumeration; card scoring; Space runtime + read-only HTTP probes; config/header/array loads; datasets-server slices; conformance replay (2 corpora)
WHAT PASSED: 22 Spaces responded; 22 dataset slices loaded; 10 small-array models loaded
WHAT FAILED: 7 dataset loads failed; 1 conformance fixture mismatch(es); 1 model(s) with an invalid weights-extension file; 4 model(s) with file-set/framework coherence issues
WHAT ABSTAINED: 41 artifacts not functionally tested (reasons listed)
WHAT REMAINS UNRESOLVED: large-weight inference quality; private Space behaviour; sleeping Spaces (not woken)
WHAT THIS RESULT DOES NOT PROVE: model quality, safety, or that any card claim is true beyond the checks listed
```

## Coverage accounting

```text
artifacts_expected: 120
artifacts_discovered: 107 (authenticated listing; 0 private)
artifacts_examined: 107
artifacts_functionally_tested: 83
artifacts_not_tested: 41
denominator_state: OBSERVED
# not tested (artifact: reason)
#   dataset:SZLHOLDINGS/killinchu-osint-corpus: slice SOURCE_UNAVAILABLE
#   model:SZLHOLDINGS/A11OY-MINI: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 2.85 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/KHIPU-R2: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 6.32 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.24 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/SZL-Khipu-1.5B: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.24 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/SZL-Khipu-1.5B-GGUF: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 6.85 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/SZL-Khipu-1.5B-abstain: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.24 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/SZLHOLDINGS: full load not performed (NOT_A_MODEL_REPO): DOCS_OR_CONFIG_ONLY
#   model:SZLHOLDINGS/WILLAY: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 2.00 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/YARQA-ATTN: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/a11oy-v19-substrate: full load not performed (NOT_A_MODEL_REPO): DOCS_OR_CONFIG_ONLY
#   model:SZLHOLDINGS/brain-navigator-r2: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.04 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/chaski: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 1.77 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/chaski-5050: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.06 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/chaski-r2: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.04 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/governed-inference-meter: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/khipu-r3: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.04 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/oac-clinical-transport-health-v1: full load not performed (NOT_A_MODEL_REPO): CODE_ONLY
#   model:SZLHOLDINGS/oac-system-health-v1: full load not performed (NOT_A_MODEL_REPO): CODE_ONLY
#   model:SZLHOLDINGS/szl-block-kv: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-blocked: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-energy-attest: full load not performed (NOT_A_MODEL_REPO): DOCS_OR_CONFIG_ONLY
#   model:SZLHOLDINGS/szl-formulas: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-governed-norm: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-govsign: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-invariants: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-kernels: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-khipu-kernels: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-lambda-gate: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-maskmod: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-nemo: full load not performed (NOT_A_MODEL_REPO): CODE_ONLY
#   model:SZLHOLDINGS/szl-ouroboros: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-provctl: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-receipt-attn: full load not performed (NOT_A_MODEL_REPO): software kernel (code), not trained weights
#   model:SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.46 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v2-merged: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.41 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-v3: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 3.04 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/szl-training-scripts: full load not performed (NOT_A_MODEL_REPO): CODE_ONLY
#   model:SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 0.03 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   model:SZLHOLDINGS/szl-triage-qwen3.5-0.8b-lora-study5: full load not performed (RUNTIME_UNAVAILABLE_NOT_TESTED): 0.35 GB of weights; no torch runtime in audit env; headers validated by range request instead
#   space:SZLHOLDINGS/a11oy: runtime RUNNING_APP_STARTING; not requested (would wake/restart the Space)
```

Org `SZLHOLDINGS` · authenticated listing: model 49 (OBSERVED), dataset 43 (OBSERVED), space 28 (OBSERVED) · anonymous public counts: models 49, datasets 35, spaces 22 (at 2026-09-25T16:34:27Z)

Reconciliation: 23 non-private Spaces in the authenticated listing vs 22 in the anonymous listing — SZLHOLDINGS/README (org card Space) is public but absent from the anonymous author listing.

## Card scorecard (P/~/F/NT)

| artifact | kind | private | card_exists | not_a_stub | license | intended_use | out_of_scope | limitations | evaluation | training_data | provenance | reproduction | contact | non_establishment | capability w/o evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a11oy-verifiable-corpus | dataset | no | P | P | ~ | F | F | F | F | F | P | P | P | F | no |
| alloy-sovereign-eval-runs | dataset | no | P | P | ~ | F | F | F | F | F | P | P | P | F | no |
| canonical-formulas-v1 | dataset | no | P | P | P | F | F | F | F | F | P | F | F | F | no |
| david-leads-data | dataset | no | P | P | F | F | F | P | F | F | F | F | P | F | no |
| doctrine-v10-v11 | dataset | no | P | P | P | F | F | P | F | F | P | F | F | F | no |
| energy-attested-runs | dataset | no | P | P | ~ | F | F | F | F | F | P | P | F | P | no |
| governed-agent-bench | dataset | no | P | ~ | P | F | F | F | F | F | P | P | F | F | no |
| governed-receipts-bench | dataset | no | P | P | ~ | F | F | P | F | F | P | P | F | F | no |
| k-verify-benchmark-v1 | dataset | no | P | P | ~ | F | F | F | P | F | P | F | P | F | no |
| killinchu-osint-corpus | dataset | no | P | P | P | F | F | F | F | F | F | F | F | P | no |
| lean-proofs-v1 | dataset | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| lean-theorem-tree | dataset | no | P | P | ~ | F | F | F | F | F | P | F | P | F | no |
| model-bom | dataset | no | P | P | P | F | F | F | F | F | F | F | F | F | no |
| oac-clinical-transport-observability-synthetic | dataset | no | P | P | P | F | F | P | F | F | P | P | F | F | no |
| ouroboros-arxiv-preprint | dataset | no | P | P | ~ | F | F | F | F | F | P | F | P | F | no |
| rag-corpus-v1 | dataset | no | P | P | ~ | F | F | F | F | F | P | F | P | F | no |
| readiness-runs | dataset | no | P | P | ~ | F | F | F | F | F | P | P | P | F | no |
| receipted-unsloth | dataset | no | P | P | ~ | F | F | F | F | F | P | F | F | F | no |
| release-assets | dataset | no | F | F | F | F | F | F | F | F | F | F | F | F | no |
| szl-1-doctrine-sft | dataset | no | P | P | ~ | F | F | F | P | P | P | P | F | F | no |
| szl-artifacts | dataset | no | P | P | ~ | F | F | F | F | F | P | F | P | P | no |
| szl-estate-graph | dataset | no | P | P | F | F | F | F | F | F | F | P | F | P | no |
| szl-frontier-covenant | dataset | no | P | P | ~ | F | F | F | F | F | P | F | F | F | no |
| szl-frontier-evaluation-receipts | dataset | no | P | P | ~ | F | F | F | ~ | F | P | F | F | P | no |
| szl-lake | dataset | no | P | P | P | F | F | F | F | F | P | P | F | F | no |
| szl-quant-sft-v1 | dataset | no | P | P | P | F | F | P | F | F | P | P | F | F | no |
| szl-second-brain-inrepo | dataset | no | P | P | F | F | F | F | F | F | F | F | P | F | no |
| SZLHOLDINGS | dataset | no | P | P | P | P | F | F | F | P | P | F | F | F | yes |
| test-results | dataset | no | P | P | P | F | F | F | ~ | F | P | P | F | F | no |
| thesis-corpus-v18 | dataset | no | P | P | P | F | F | F | F | F | P | F | F | F | no |
| thesis-v18-formal-verification | dataset | no | P | P | ~ | F | F | F | F | F | P | P | P | F | no |
| uds-bundles-v1 | dataset | no | P | P | ~ | F | F | F | F | F | P | F | F | P | no |
| uds-governance-receipts | dataset | no | P | P | P | F | F | F | F | F | P | F | P | F | no |
| uds-spans-receipts | dataset | no | P | P | P | F | F | F | F | F | P | F | P | F | no |
| why-we-lead | dataset | no | P | P | P | F | F | F | F | F | F | F | F | F | no |
| A11OY-MINI | model | no | P | P | ~ | F | F | F | F | F | P | P | F | P | no |
| a11oy-v19-substrate | model | no | P | P | P | P | F | P | F | P | P | F | F | P | no |
| brain-navigator-r2 | model | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| chakana | model | no | P | P | P | P | F | F | F | F | F | P | F | F | no |
| chaski | model | no | P | P | ~ | P | F | P | P | F | P | P | F | F | no |
| chaski-5050 | model | no | P | P | ~ | P | F | P | P | F | P | P | F | P | no |
| chaski-r2 | model | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| governed-inference-meter | model | no | P | P | P | P | P | P | F | F | P | P | P | P | yes |
| KHIPU-R2 | model | no | P | P | ~ | F | F | F | P | F | F | P | F | P | no |
| khipu-r3 | model | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| KILLINCHU-EYE | model | no | P | P | ~ | P | F | P | F | F | P | F | F | F | no |
| MiniEmbed-Nano | model | no | P | P | P | F | F | F | F | F | P | P | F | P | no |
| Moons-Nano | model | no | P | P | P | F | F | F | F | F | P | P | F | P | no |
| oac-clinical-transport-health-v1 | model | no | P | P | P | F | F | F | P | F | P | P | F | F | no |
| oac-system-health-v1 | model | no | P | P | P | F | F | F | P | F | P | P | F | F | no |
| qantu | model | no | P | P | P | P | F | F | F | F | F | P | F | F | no |
| ReceiptAgent-Nano | model | no | P | P | P | P | F | P | F | F | F | P | F | F | no |
| szl-block-kv | model | no | P | P | P | P | F | P | F | F | P | F | F | P | no |
| szl-blocked | model | no | P | P | P | P | F | P | F | F | P | P | F | F | no |
| szl-energy-attest | model | no | P | P | ~ | F | F | F | F | F | P | F | F | F | no |
| SZL-Forge-1.5B-ReceiptAgent | model | no | P | P | P | P | F | P | ~ | F | P | P | F | F | no |
| szl-formulas | model | no | P | P | P | P | F | P | F | F | P | P | F | F | no |
| szl-governed-norm | model | no | P | P | P | P | F | P | P | P | P | P | P | P | no |
| szl-govsign | model | no | P | P | P | P | F | P | F | F | P | F | F | F | no |
| szl-invariants | model | no | P | P | P | P | F | P | F | F | P | P | F | F | no |
| szl-kernels | model | no | P | P | P | P | F | P | F | F | P | P | P | F | yes |
| szl-khipu | model | no | P | P | P | F | F | P | F | F | P | P | P | P | no |
| SZL-Khipu-1.5B | model | no | P | P | P | P | F | F | P | P | P | P | P | P | no |
| SZL-Khipu-1.5B-abstain | model | no | P | P | P | P | F | P | ~ | F | P | F | F | F | yes |
| SZL-Khipu-1.5B-GGUF | model | no | P | P | P | P | F | P | F | F | P | F | F | P | no |
| szl-khipu-kernels | model | no | P | P | P | F | F | F | F | F | P | F | F | F | no |
| szl-lambda-gate | model | no | P | P | P | P | F | P | P | P | P | P | P | P | no |
| szl-maskmod | model | no | P | P | P | P | F | P | F | F | P | F | F | P | no |
| szl-nemo | model | no | P | P | P | P | F | P | F | F | P | F | F | F | no |
| szl-ouroboros | model | no | P | P | P | P | F | P | F | F | P | F | F | F | no |
| szl-provctl | model | no | P | P | P | P | F | P | F | F | P | F | F | F | no |
| szl-receipt-attn | model | no | P | P | P | P | F | P | F | F | P | F | F | P | no |
| szl-receiptagent-qwen35-0.8b-v2 | model | no | P | P | P | P | F | P | F | F | P | F | F | F | no |
| szl-receiptagent-qwen35-0.8b-v2-merged | model | no | P | P | ~ | F | F | F | F | F | P | F | F | F | yes |
| szl-receiptagent-qwen35-0.8b-v3 | model | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| szl-training-scripts | model | no | P | P | P | P | F | P | F | F | F | P | F | F | no |
| szl-triage-qwen3.5-0.8b-lora | model | no | P | P | ~ | P | F | F | ~ | F | P | P | F | P | no |
| szl-triage-qwen3.5-0.8b-lora-study5 | model | no | P | P | F | F | F | P | ~ | F | P | P | F | P | no |
| SZLHOLDINGS | model | no | P | P | ~ | P | F | P | F | F | P | F | F | F | yes |
| tinku | model | no | P | P | P | P | F | F | F | F | F | P | F | F | no |
| TinyKhipu-Nano | model | no | P | P | P | P | F | P | F | F | F | P | F | F | no |
| waman | model | no | P | P | P | P | F | F | F | F | F | P | F | F | no |
| WILLAY | model | no | P | P | P | P | F | P | ~ | P | F | P | F | F | no |
| YARQA-ATTN | model | no | P | P | P | P | F | P | F | F | P | F | F | P | no |
| a11oy | space | no | P | P | ~ | F | F | F | F | F | P | P | F | P | yes |
| ayllu | space | no | P | P | P | F | F | F | F | F | P | P | F | F | no |
| counsel | space | no | P | ~ | ~ | F | F | F | F | F | P | F | F | F | no |
| david-leads | space | no | P | P | ~ | F | F | P | F | F | P | F | P | F | no |
| finance | space | no | P | ~ | ~ | F | F | F | F | F | P | F | F | F | no |
| holographic-unify | space | no | P | ~ | ~ | F | F | F | F | F | F | F | F | F | no |
| immune | space | no | P | P | ~ | F | F | F | F | F | P | F | F | F | no |
| immune-lattice | space | no | P | ~ | ~ | F | F | F | F | F | P | F | F | F | no |
| killinchu | space | no | P | P | ~ | F | F | P | F | F | P | P | P | F | no |
| llm-router-live | space | no | P | P | ~ | F | F | F | F | F | P | P | F | P | yes |
| lyte | space | no | P | P | P | F | F | P | F | F | F | P | F | F | no |
| README | space | no | P | P | ~ | F | F | F | F | F | P | P | F | F | no |
| sentra | space | no | P | ~ | ~ | F | F | F | F | F | P | F | F | F | no |
| szl-atelier | space | no | P | ~ | ~ | F | F | F | F | F | F | F | F | F | no |
| szl-command-lab | space | no | P | P | ~ | F | F | F | F | F | P | P | F | P | no |
| szl-constellation | space | no | P | P | ~ | F | F | F | F | F | P | F | P | F | no |
| szl-constellation-staging | space | no | P | P | ~ | F | F | F | F | F | P | F | P | F | no |
| szl-frontier | space | no | P | P | P | F | F | F | F | F | P | F | F | P | no |
| szl-khipu | space | no | P | P | ~ | F | F | F | F | F | P | F | F | F | no |
| szl-model-inference-lab | space | no | P | P | P | P | F | P | F | F | P | P | F | P | no |
| terra | space | no | P | ~ | ~ | F | F | F | F | F | P | F | F | F | no |
| vertical-services | space | no | P | P | ~ | F | F | P | F | F | P | F | F | F | no |
| yarqa | space | no | P | P | ~ | F | F | F | F | F | P | F | F | P | no |

## Spaces — runtime and read-only probes

Latencies were timed with a ~15.6 ms-resolution clock on this host (values are multiples of it; differences below that are not measurable).

| space | private | sdk | hardware | runtime (raw stage) | http | probes | title |
|---|---|---|---|---|---|---|---|
| a11oy | no | docker | cpu-basic | RUNNING_APP_STARTING | NOT_TESTED | runtime RUNNING_APP_STARTING; not requested (would wake/restart the Space) | none |
| README | no | static | UNKNOWN | RUNNING | RESPONDED | / → 200 (375 ms); /health → 404 (31 ms); /api/health → 404 (47 ms) | SZL Holdings - Control before action. Evidence after. |
| killinchu | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (125 ms); /health → 404 (31 ms); /api/health → 200 (31 ms) | killinchu — Governed Counter-UAS &amp; Maritime C2 · SZL Holdings |
| counsel | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (140 ms); /health → 404 (<16 ms); /api/health → 404 (<16 ms) | PRISM Counsel — SZL Holdings |
| terra | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (125 ms); /health → 404 (16 ms); /api/health → 404 (16 ms) | Terra — SZL Holdings |
| sentra | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (125 ms); /health → 404 (<16 ms); /api/health → 404 (16 ms) | Sentra — SZL Holdings |
| finance | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (79 ms); /health → 404 (62 ms); /api/health → 404 (<16 ms) | PURIQ Finance — SZL Holdings |
| lyte | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (157 ms); /health → 404 (<16 ms); /api/health → 404 (16 ms) | Lyte — Business Observability Command |
| vertical-services | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (140 ms); /health → 404 (16 ms); /api/health → 404 (16 ms) | SZL Vertical Services |
| szl-command-lab | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (312 ms); /health → 404 (31 ms); /api/health → 404 (<16 ms) | SZL Atlas — Governed AI Estate |
| david-leads | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (109 ms); /health → 404 (<16 ms); /api/health → 404 (31 ms) | David Leads \| Evidence-Backed Broker Research |
| szl-constellation | no | gradio | cpu-basic | RUNNING | RESPONDED | / → 200 (141 ms); /config → 404 (63 ms); /gradio_api/info → 404 (31 ms) | SZL Constellation |
| szl-frontier | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (328 ms); /health → 404 (47 ms); /api/health → 404 (31 ms) | SZL Frontier |
| szl-model-inference-lab | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (140 ms); /health → 200 (16 ms); /api/health → 404 (16 ms) | SZL Model Inference Lab - Khipu Loom |
| immune-lattice | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (125 ms); /health → 200 (31 ms); /api/health → 404 (16 ms) | IMMUNE — Python kernel |
| immune | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (156 ms); /health → 200 (31 ms); /api/health → 404 (16 ms) | IMMUNE \| Evidence-Scoped AI Defense |
| ayllu | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (78 ms); /health → 200 (32 ms); /api/health → 404 (31 ms) | Ayllu — holographic counsel |
| yarqa | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (172 ms); /health → 404 (16 ms); /api/health → 404 (<16 ms) | yarqa · plug-flow compartments — live or sample, always honest |
| szl-atelier | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (94 ms); /health → 404 (32 ms); /api/health → 404 (16 ms) | SZL Atelier — Governed Artifact Constellation |
| holographic-unify | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (204 ms); /health → 404 (16 ms); /api/health → 404 (16 ms) | SZL Holographic Unify |
| szl-khipu | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (78 ms); /health → 200 (31 ms); /api/health → 404 (16 ms) | SZL KHIPU |
| llm-router-live | no | docker | cpu-basic | RUNNING | RESPONDED | / → 200 (125 ms); /health → 200 (31 ms); /api/health → 404 (31 ms) | SZL Router — Sovereign LLM Gateway |
| szl-constellation-staging | no | gradio | cpu-basic | RUNNING | RESPONDED | / → 200 (141 ms); /config → 404 (<16 ms); /gradio_api/info → 404 (16 ms) | SZL Constellation |

## Models — artifact class, coherence, load

Load state RUNTIME_UNAVAILABLE_NOT_TESTED = weights present but no torch/llama.cpp runtime in the audit environment (headers validated by HTTP range request instead); it is not a size judgement.

| model | class | library | pipeline | weights (bytes) | config | header check | load | downloads 30d | mistakable-for-trained signals | coherence issues |
|---|---|---|---|---|---|---|---|---|---|---|
| A11OY-MINI | TRAINED_WEIGHTS | llama.cpp | text-generation | 2848815150 | ABSENT | Modelfile.a11oy-r2.gguf: INVALID; a11oy-mini-f16.gguf: HEADER_VALID; a11oy-mini-q4_k_m.gguf: HEADER_VALID; a11oy-mini-r2-BF16-mmproj.gguf: HEADER_VALID; a11oy-mini-r2-Q4_K_M.gguf: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 274 | none | Modelfile.a11oy-r2.gguf: file has .gguf extension but no GGUF magic (142 bytes) |
| a11oy-v19-substrate | DOCS_OR_CONFIG_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 1 | card uses trained-model language | none |
| brain-navigator-r2 | TRAINED_ADAPTER | peft | text-generation | 3035200728 | LOADED | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 118 | none | none |
| chakana | SMALL_ARRAYS | other | NONE | 3219 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| chaski | TRAINED_ADAPTER | transformers | text-generation | 1774701076 | LOADED | adapter-unsloth/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 4585 | none | PEFT adapter declared with library_name=transformers (expected peft) |
| chaski-5050 | TRAINED_ADAPTER | peft | text-generation | 3060789503 | LOADED | adapter-unsloth/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 167 | none | none |
| chaski-r2 | TRAINED_ADAPTER | peft | text-generation | 3037372097 | LOADED | adapter-unsloth/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 188 | none | none |
| governed-inference-meter | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| KHIPU-R2 | TRAINED_ADAPTER | peft | text-generation | 6322666032 | LOADED | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 168 | none | none |
| khipu-r3 | TRAINED_ADAPTER | peft | text-generation | 3035200728 | LOADED | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 123 | none | none |
| KILLINCHU-EYE | SMALL_ARRAYS | other | NONE | 4182 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| MiniEmbed-Nano | SMALL_ARRAYS | numpy | NONE | 6892 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| Moons-Nano | SMALL_ARRAYS | numpy | NONE | 1302 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| oac-clinical-transport-health-v1 | CODE_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| oac-system-health-v1 | CODE_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| qantu | SMALL_ARRAYS | other | NONE | 3842 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| ReceiptAgent-Nano | SMALL_ARRAYS | numpy | NONE | 6014 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| szl-block-kv | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 63 | none | none |
| szl-blocked | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-energy-attest | DOCS_OR_CONFIG_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| SZL-Forge-1.5B-ReceiptAgent | TRAINED_ADAPTER | transformers | text-generation | 3235237640 | LOADED | adapter/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 1727 | none | PEFT adapter declared with library_name=transformers (expected peft) |
| szl-formulas | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-governed-norm | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 299 | card uses trained-model language | none |
| szl-govsign | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-invariants | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-kernels | SOFTWARE_KERNEL | kernels | NONE | 1564835 | LOADED | none | NOT_A_MODEL_REPO | 92 | card uses trained-model language | none |
| szl-khipu | SMALL_ARRAYS | numpy | NONE | 18942 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| SZL-Khipu-1.5B | TRAINED_ADAPTER | transformers | text-generation | 3235237640 | LOADED | adapter/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 2938 | none | PEFT adapter declared with library_name=transformers (expected peft) |
| SZL-Khipu-1.5B-abstain | TRAINED_ADAPTER | NONE | NONE | 3241439328 | ABSENT | khipu-abstain-adapter/adapter_model.safetensors: HEADER_VALID; khipu-f16.gguf: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 17 | none | none |
| SZL-Khipu-1.5B-GGUF | TRAINED_WEIGHTS | llama.cpp | text-generation | 6851338880 | ABSENT | SZL-Khipu-1.5B-F16.gguf: HEADER_VALID; SZL-Khipu-1.5B-Q4_K_M.gguf: HEADER_VALID; SZL-Khipu-1.5B-Q5_K_M.gguf: HEADER_VALID; SZL-Khipu-1.5B-Q8_0.gguf: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 1735 | none | none |
| szl-khipu-kernels | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-lambda-gate | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 54 | card uses trained-model language | none |
| szl-maskmod | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 44 | none | none |
| szl-nemo | CODE_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 5 | card uses trained-model language | none |
| szl-ouroboros | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-provctl | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-receipt-attn | SOFTWARE_KERNEL | kernels | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 42 | none | none |
| szl-receiptagent-qwen35-0.8b-v2 | TRAINED_ADAPTER | peft | text-generation | 3455348640 | ABSENT | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 453 | none | none |
| szl-receiptagent-qwen35-0.8b-v2-merged | TRAINED_WEIGHTS | transformers | text-generation | 3412002208 | LOADED | model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 504 | none | none |
| szl-receiptagent-qwen35-0.8b-v3 | TRAINED_ADAPTER | peft | text-generation | 3035200728 | LOADED | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 155 | none | none |
| szl-training-scripts | CODE_ONLY | other | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| szl-triage-qwen3.5-0.8b-lora | TRAINED_ADAPTER | transformers | text-classification | 25592817 | ABSENT | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 0 | none | PEFT adapter declared with library_name=transformers (expected peft) |
| szl-triage-qwen3.5-0.8b-lora-study5 | TRAINED_ADAPTER | peft | text-generation | 347602067 | ABSENT | adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 440 | none | none |
| SZLHOLDINGS | DOCS_OR_CONFIG_ONLY | NONE | NONE | 0 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |
| tinku | SMALL_ARRAYS | other | NONE | 3063 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| TinyKhipu-Nano | SMALL_ARRAYS | numpy | NONE | 3568 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| waman | SMALL_ARRAYS | other | NONE | 4189 | ABSENT | none | LOADED | 0 | card uses trained-model language | none |
| WILLAY | TRAINED_ADAPTER | peft | text-generation | 1998143274 | LOADED | adapter-unsloth/adapter_model.safetensors: HEADER_VALID | RUNTIME_UNAVAILABLE_NOT_TESTED | 138 | none | none |
| YARQA-ATTN | SOFTWARE_KERNEL | kernels | NONE | 3301 | ABSENT | none | NOT_A_MODEL_REPO | 0 | card uses trained-model language | none |

## Datasets — load, schema, counts, sensitive patterns

| dataset | private | splits | slice | rows loaded | observed rows | card schema match | direct file parse | PII patterns | downloads 30d |
|---|---|---|---|---|---|---|---|---|---|
| a11oy-verifiable-corpus | no | PRESENT | LOADED | 22 | 470 | NOT_DECLARED | NOT_TESTED | 0 hits (first 22 rows) | 3893 |
| alloy-sovereign-eval-runs | no | PRESENT | LOADED | 25 | 25 | NOT_DECLARED | NOT_TESTED | 0 hits (first 25 rows) | 339 |
| canonical-formulas-v1 | no | NO_TABULAR_DATA_FILES | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | PARSED | NOT_TESTED | 401 |
| david-leads-data | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 353 |
| doctrine-v10-v11 | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 436 |
| energy-attested-runs | no | PRESENT | LOADED | 8 | 8 | NOT_DECLARED | NOT_TESTED | 0 hits (first 8 rows) | 332 |
| governed-agent-bench | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 363 |
| governed-receipts-bench | no | PRESENT | LOADED | 7 | 7 | NOT_DECLARED | NOT_TESTED | 0 hits (first 7 rows) | 325 |
| k-verify-benchmark-v1 | no | PRESENT | LOADED | 100 | 100 | NOT_DECLARED | NOT_TESTED | 0 hits (first 100 rows) | 330 |
| killinchu-osint-corpus | no | SOURCE_UNAVAILABLE | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | PARSED | NOT_TESTED | 64044 |
| lean-proofs-v1 | no | PRESENT | LOADED | 1 | 1 | NOT_DECLARED | NOT_TESTED | credit_card_like: 3 (first 1 rows; manual review) | 575 |
| lean-theorem-tree | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 302 |
| model-bom | no | PRESENT | LOADED | 1 | 1 | NOT_DECLARED | NOT_TESTED | 0 hits (first 1 rows) | 378 |
| oac-clinical-transport-observability-synthetic | no | PRESENT | LOADED | 100 | 1200 | NOT_DECLARED | NOT_TESTED | 0 hits (first 100 rows) | 338 |
| ouroboros-arxiv-preprint | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 364 |
| rag-corpus-v1 | no | PRESENT | LOADED | 92 | 762 | NOT_DECLARED | NOT_TESTED | credit_card_like: 2 (first 92 rows; manual review) | 371 |
| readiness-runs | no | PRESENT | LOADED | 78 | 265 | NOT_DECLARED | NOT_TESTED | 0 hits (first 78 rows) | 393 |
| receipted-unsloth | no | PRESENT | LOADED | 1 | UNAVAILABLE | NOT_DECLARED | NOT_TESTED | 0 hits (first 1 rows) | 357 |
| release-assets | no | EMPTY | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | NOT_TESTED | NOT_TESTED | 225 |
| szl-1-doctrine-sft | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 362 |
| szl-artifacts | no | PRESENT | LOADED | 52 | 52 | NOT_DECLARED | NOT_TESTED | 0 hits (first 52 rows) | 760 |
| szl-estate-graph | no | PRESENT | LOADED | 100 | 193 | NOT_DECLARED | NOT_TESTED | 0 hits (first 100 rows) | 338 |
| szl-frontier-covenant | no | PRESENT | LOAD_FAILED_SCHEMA_INCONSISTENT | NOT_TESTED | UNAVAILABLE | NOT_DECLARED | PARSED | NOT_TESTED | 372 |
| szl-frontier-evaluation-receipts | no | PRESENT | LOADED | 14 | 14 | NOT_DECLARED | NOT_TESTED | 0 hits (first 14 rows) | 485 |
| szl-lake | no | PRESENT | LOADED | 16 | 16 | NOT_DECLARED | NOT_TESTED | 0 hits (first 16 rows) | 6981 |
| szl-quant-sft-v1 | no | PRESENT | LOADED | 90 | 2693 | NOT_DECLARED | NOT_TESTED | credit_card_like: 421 (first 90 rows; manual review) | 357 |
| szl-second-brain-inrepo | no | PRESENT | LOADED | 85 | 575 | NOT_DECLARED | NOT_TESTED | email: 1 (first 85 rows; manual review) | 335 |
| SZLHOLDINGS | no | ABSENT | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | NOT_TESTED | NOT_TESTED | 345 |
| test-results | no | ABSENT | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | NOT_TESTED | NOT_TESTED | 364 |
| thesis-corpus-v18 | no | PRESENT | LOADED | 100 | 358 | NOT_DECLARED | NOT_TESTED | 0 hits (first 100 rows) | 470 |
| thesis-v18-formal-verification | no | PRESENT | LOADED | 11 | 11 | NOT_DECLARED | NOT_TESTED | 0 hits (first 11 rows) | 514 |
| uds-bundles-v1 | no | NO_TABULAR_DATA_FILES | NOT_TESTED | NOT_TESTED | UNAVAILABLE | UNAVAILABLE | PARSED | NOT_TESTED | 386 |
| uds-governance-receipts | no | PRESENT | LOADED | 5 | 5 | NOT_DECLARED | NOT_TESTED | 0 hits (first 5 rows) | 710 |
| uds-spans-receipts | no | PRESENT | LOADED | 5 | 155 | NOT_DECLARED | NOT_TESTED | 0 hits (first 5 rows) | 518 |
| why-we-lead | no | PRESENT | LOADED | 11 | 11 | NOT_DECLARED | NOT_TESTED | 0 hits (first 11 rows) | 435 |

## Conformance corpora (most important functional test)

### SZLHOLDINGS/governed-receipts-bench (fixture_corpus)
Declared fixtures: 7 · paired verifier: `szl-holdings/governed-receipt-spec` · card-pinned commit: `007106bcb0212138345e19eb5efba8bb69327d57`
- **szl-holdings/governed-receipt-spec@007106bcb021 (pinned)** → 7/7 declared outcomes reproduced; mismatched: none
| fixture | declared | observed | exit | exit consistent | match |
|---|---|---|---|---|---|
| valid/a11oy-khipu-chain.json | PASS | PASS | 0 | yes | yes |
| valid/a11oy-khipu-genesis.json | PASS | PASS | 0 | yes | yes |
| valid/lake-inference-receipt.json | PASS | PASS | 0 | yes | yes |
| valid/readiness-audit-receipt.json | PASS | PASS | 0 | yes | yes |
| valid/daily-activity-receipt.json | PASS | PASS | 0 | yes | yes |
| invalid/tampered-payload.json | FAIL | FAIL | 1 | yes | yes |
| invalid/broken-chain.json | FAIL | FAIL | 1 | yes | yes |
- **szl-holdings/governed-receipt-spec@2c82320a9946 (default-branch HEAD)** → 6/7 declared outcomes reproduced; mismatched: valid/lake-inference-receipt.json
| fixture | declared | observed | exit | exit consistent | match |
|---|---|---|---|---|---|
| valid/a11oy-khipu-chain.json | PASS | PASS | 0 | yes | yes |
| valid/a11oy-khipu-genesis.json | PASS | PASS | 0 | yes | yes |
| valid/lake-inference-receipt.json | PASS | FAIL | 1 | yes | no |
| valid/readiness-audit-receipt.json | PASS | PASS | 0 | yes | yes |
| valid/daily-activity-receipt.json | PASS | PASS | 0 | yes | yes |
| invalid/tampered-payload.json | FAIL | FAIL | 1 | yes | yes |
| invalid/broken-chain.json | FAIL | FAIL | 1 | yes | yes |

### SZLHOLDINGS/governed-agent-bench (bundled_scorer)
- `python score.py submissions/reference-conformance.jsonl --strict` → exit 0 in 0.17 s
- all exit zero: yes
