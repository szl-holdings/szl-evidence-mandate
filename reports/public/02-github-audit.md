# 02 — GitHub organisation audit: szl-holdings

```text
STATUS: ATTENTION
WHAT WAS EXPECTED: every repository of szl-holdings: public 118 (org metadata, OBSERVED) + private UNAVAILABLE (not exposed by the org API)
WHAT WAS EXAMINED: 118 (authenticated listing, all pages; 0 private) repos listed; 87 shallow-cloned and file-analysed
WHAT ACTUALLY RAN: REST/GraphQL collection; clones; secret + risky-pattern scan; 57 clean-environment install/test runs
WHAT PASSED: 472 axis results PASS across 118 repos
WHAT FAILED: 307 axis results FAIL
WHAT ABSTAINED: 241 axis results NOT_TESTED across 50 repos
WHAT REMAINS UNRESOLVED: 61 repos not functionally tested (per-repo reasons in the coverage block); interim-harness test failures await a re-run under harness fix2
WHAT THIS RESULT DOES NOT PROVE: code correctness, security, or fitness; scores are evidence summaries from heuristics labelled with confidence; Clean-install/test runs executed on a Windows 11 host (Python 3.12 venv, stripped environment, shallow clones with core.symlinks=false); Windows-specific outcomes are attributed HOST_PLATFORM, not to repositories.
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

Org: `szl-holdings` · authenticated: yes · listing: 2 pages, denominator OBSERVED · HTTP requests: 1928

Clean-install/test runs executed on a Windows 11 host (Python 3.12 venv, stripped environment, shallow clones with core.symlinks=false); Windows-specific outcomes are attributed HOST_PLATFORM, not to repositories.

## Scorecard (P=PASS, ~=PARTIAL, F=FAIL, NT=NOT_TESTED)

| repo | identity | license | provenance | tests | ci | release_integrity | security_posture | docs | honest_scoping | evidence_boundary | cross_links | maintenance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| .github | ~ | P | F | ~ | P | F | ~ | F | F | F | F | P |
| a11oy | P | P | P | ~ | P | P | ~ | F | P | ~ | F | P |
| <private> | ~ | P | P | P | P | F | ~ | ~ | F | ~ | ~ | P |
| a11oy-net | ~ | P | NT | ~ | P | F | P | F | P | ~ | P | P |
| anatomy | ~ | P | ~ | P | P | F | P | ~ | P | ~ | F | P |
| ayllu | ~ | P | F | ~ | P | F | ~ | P | F | F | P | P |
| ayllu-hf-space | ~ | P | NT | F | F | F | ~ | F | F | F | P | P |
| david-leads | ~ | P | ~ | F | P | F | ~ | F | F | ~ | P | P |
| evidence-doctrine | ~ | P | F | ~ | P | F | ~ | ~ | F | F | P | P |
| evidence-studio | ~ | P | NT | ~ | P | F | ~ | F | F | F | P | P |
| frontier-bench | ~ | P | F | P | P | F | ~ | F | F | ~ | ~ | P |
| governance-as-code | ~ | P | NT | ~ | P | F | P | ~ | P | ~ | P | P |
| governed-receipt-spec | P | P | ~ | ~ | P | F | P | ~ | P | ~ | F | P |
| hatun-mcp | ~ | P | F | P | P | ~ | P | P | F | ~ | P | P |
| holographic-unify | P | P | F | ~ | ~ | F | ~ | ~ | P | ~ | F | P |
| immune | ~ | P | P | P | P | F | P | ~ | F | ~ | P | P |
| khipu-consensus | ~ | P | NT | ~ | P | F | P | P | F | F | F | P |
| khipu-sda-core | ~ | P | F | ~ | P | F | ~ | ~ | F | F | P | P |
| khipu-x1 | P | P | F | P | P | F | ~ | P | P | ~ | ~ | P |
| killinchu | ~ | P | F | ~ | F | ~ | ~ | P | F | ~ | F | P |
| lutar-lean | ~ | P | ~ | ~ | P | ~ | P | P | F | F | F | P |
| lyte-lattice | ~ | P | P | P | F | F | P | ~ | F | ~ | F | P |
| lyte-services | ~ | P | ~ | P | ~ | F | P | P | F | ~ | P | P |
| nexus | ~ | P | P | ~ | ~ | F | ~ | ~ | F | F | F | P |
| platform | ~ | ~ | NT | NT | ~ | ~ | NT | NT | NT | NT | NT | P |
| puriq-live | ~ | P | ~ | ~ | P | F | ~ | P | F | F | ~ | P |
| quant-curve | ~ | P | F | ~ | P | F | ~ | F | F | ~ | P | P |
| retrieval-bench | ~ | P | F | ~ | P | F | ~ | F | F | ~ | P | P |
| sda | P | P | NT | ~ | P | F | ~ | P | P | ~ | F | P |
| szl-atelier | ~ | P | F | ~ | P | F | ~ | F | F | F | P | P |
| szl-block-kv | ~ | P | F | F | P | F | P | F | P | F | P | P |
| szl-blocked | P | P | F | P | ~ | F | P | F | P | ~ | P | P |
| szl-brand | ~ | P | F | ~ | P | ~ | P | P | F | ~ | F | P |
| szl-build-env | P | P | F | ~ | P | F | ~ | ~ | P | F | P | P |
| szl-calibration | ~ | P | F | P | P | F | ~ | ~ | P | P | ~ | P |
| szl-ci-witness | ~ | P | F | P | P | F | ~ | P | F | F | ~ | P |
| szl-command-lab | P | P | P | P | P | F | P | P | P | ~ | F | P |
| szl-constellation | ~ | P | NT | ~ | ~ | F | ~ | ~ | F | ~ | P | P |
| szl-crosscheck | ~ | P | F | P | P | F | ~ | P | F | P | ~ | P |
| szl-doctrine | P | P | NT | ~ | P | F | ~ | F | P | F | P | P |
| szl-drift | ~ | P | NT | ~ | P | F | ~ | F | F | F | P | P |
| szl-eclipse | ~ | P | F | P | P | F | ~ | P | F | ~ | ~ | P |
| szl-energy-attest | P | P | F | ~ | P | F | ~ | P | P | ~ | P | P |
| szl-engine-bench | P | P | F | P | P | F | ~ | P | P | ~ | ~ | P |
| szl-evidence-litellm | ~ | P | F | ~ | P | ~ | ~ | P | F | F | P | P |
| szl-forge | P | P | P | ~ | P | F | F | ~ | P | ~ | P | P |
| szl-formulas | ~ | P | F | ~ | ~ | F | P | F | P | F | P | P |
| szl-frontier | P | P | P | ~ | P | ~ | P | ~ | P | F | P | P |
| szl-gov | ~ | P | NT | ~ | P | F | P | F | F | ~ | P | P |
| szl-govsign | ~ | P | F | P | ~ | F | P | F | F | F | F | P |
| szl-gpu-bridge | ~ | P | NT | ~ | ~ | F | ~ | F | P | F | ~ | P |
| szl-guardrail-receipt | ~ | P | F | P | P | F | ~ | P | F | F | F | P |
| szl-holdings.github.io | ~ | P | NT | ~ | P | F | P | F | F | F | P | P |
| szl-invariants | ~ | P | F | P | P | F | P | F | P | F | P | P |
| szl-kernels | ~ | P | F | ~ | P | F | P | P | F | ~ | F | P |
| szl-khipu | P | P | F | P | P | P | P | P | P | ~ | F | P |
| szl-lake | ~ | P | NT | ~ | P | F | P | F | F | ~ | P | P |
| szl-lambda-gate | P | P | F | ~ | P | P | ~ | ~ | P | F | P | P |
| szl-maskmod | ~ | P | F | ~ | ~ | F | ~ | F | F | F | ~ | P |
| szl-mesh | P | P | F | F | P | ~ | P | P | P | ~ | P | P |
| szl-nemo | P | P | F | P | ~ | F | ~ | P | P | ~ | P | P |
| szl-ouroboros | ~ | P | F | P | P | F | P | F | P | F | P | P |
| szl-papers | ~ | P | NT | F | P | P | P | F | F | F | F | P |
| szl-pin | ~ | ~ | NT | NT | P | F | NT | NT | NT | NT | NT | P |
| szl-platform | ~ | P | F | ~ | P | ~ | ~ | ~ | F | F | ~ | P |
| szl-provctl | ~ | P | F | P | ~ | F | P | F | P | F | F | P |
| szl-quant | P | P | F | ~ | P | F | ~ | ~ | P | ~ | P | P |
| szl-quant-bench | ~ | P | F | P | P | F | ~ | P | F | F | ~ | P |
| szl-quant-witness | ~ | P | NT | ~ | P | F | ~ | F | F | ~ | P | P |
| szl-real-estate | ~ | P | F | P | F | F | P | F | F | F | P | P |
| szl-receipt | ~ | P | F | P | P | P | P | P | F | F | P | P |
| szl-receipt-attn | ~ | P | F | F | P | F | P | ~ | F | F | P | P |
| szl-retrieval-bench | ~ | P | F | P | P | F | ~ | P | F | ~ | ~ | P |
| szl-router | ~ | P | F | P | P | F | P | ~ | P | ~ | F | P |
| szl-runbook-catalog | ~ | P | NT | ~ | ~ | F | ~ | F | F | ~ | ~ | P |
| szl-second-brain | ~ | P | F | F | ~ | F | ~ | F | F | F | ~ | P |
| szl-seismic-review | P | P | ~ | F | P | F | ~ | P | P | ~ | P | P |
| szl-serve | P | P | F | ~ | P | F | ~ | ~ | P | ~ | F | P |
| szl-sovereign-os | P | P | F | P | P | F | P | ~ | P | ~ | P | P |
| szl-substrate | ~ | P | F | P | P | F | P | P | F | F | P | P |
| szl-trust | P | P | NT | ~ | P | F | P | ~ | P | ~ | P | P |
| szl-typesafe-triage | ~ | ~ | NT | NT | P | F | NT | NT | NT | NT | NT | P |
| szl-vertical-forge | ~ | P | F | P | P | F | ~ | P | P | ~ | ~ | P |
| szl-wave1-report | ~ | P | F | P | P | F | ~ | P | F | ~ | P | P |
| the-grid | ~ | P | NT | ~ | ~ | F | ~ | ~ | F | F | ~ | P |
| uds-bundles | ~ | P | NT | ~ | P | P | ~ | ~ | F | F | F | ~ |
| vertical-services | ~ | P | ~ | ~ | P | F | ~ | F | F | F | P | P |
| vsp-otel | ~ | P | P | P | P | ~ | P | ~ | F | ~ | P | P |
| yarqa | ~ | P | P | F | P | F | ~ | P | P | ~ | P | P |
| YARQA-ATTN | ~ | P | F | F | P | F | ~ | ~ | F | F | P | P |
| cosmos (archived) | ~ | NT | NT | NT | F | F | NT | NT | NT | NT | NT | ~ |
| counsel (archived) | ~ | NT | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| developers (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| docs-site (archived) | ~ | ~ | NT | NT | P | F | NT | NT | NT | NT | NT | ~ |
| energy-attest-holo (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| evidence-typed-formula-governance (archived) | ~ | NT | NT | NT | F | ~ | NT | NT | NT | NT | NT | ~ |
| fail-closed-governed-ai-services (archived) | ~ | NT | NT | NT | F | ~ | NT | NT | NT | NT | NT | ~ |
| governed-inference-meter (archived) | ~ | ~ | NT | NT | F | ~ | NT | NT | NT | NT | NT | ~ |
| governed-norm-holo (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| immune-lattice (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| khipu-lab (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| khipu-pages (archived) | ~ | NT | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| lambda-gate-holo (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| lean-kernel (archived) | ~ | ~ | NT | NT | P | ~ | NT | NT | NT | NT | NT | ~ |
| ouroboros (archived) | ~ | ~ | NT | NT | P | ~ | NT | NT | NT | NT | NT | ~ |
| receipt-chain-live (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-cookbook (archived) | ~ | ~ | NT | NT | P | ~ | NT | NT | NT | NT | NT | ~ |
| szl-experiments (archived) | ~ | ~ | NT | NT | P | F | NT | NT | NT | NT | NT | ~ |
| szl-fleet-overlay (archived) | ~ | ~ | NT | NT | P | ~ | NT | NT | NT | NT | NT | ~ |
| szl-formula-ledger (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-governed-norm (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-kernels-live (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-organ-integrity (archived) | ~ | ~ | NT | NT | F | F | NT | NT | NT | NT | NT | ~ |
| szl-otel-mesh (archived) | ~ | ~ | NT | NT | ~ | ~ | NT | NT | NT | NT | NT | ~ |
| szl-provctl-live (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-telemetry (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |
| szl-uds-deployment (archived) | ~ | ~ | NT | NT | ~ | ~ | NT | NT | NT | NT | NT | ~ |
| warhacker-demo (archived) | ~ | ~ | NT | NT | ~ | F | NT | NT | NT | NT | NT | ~ |

Axis-state totals: PASS 472, PARTIAL 396, FAIL 307, NOT_TESTED 241.

## Installability smoke tests

Test attribution: REPO_DEFECT (cause identified in the repository), REPO_DEFECT_UNCONFIRMED (no harness/host cause recognised; confirm on Linux CI), HOST_LIMITED (Windows host limitation), UNRESOLVED / POSSIBLE_HARNESS (recorded under the interim harness; not charged to the repository), NOT_TESTED (not run or harness failure). Time-to-first-run = seconds from venv creation to the first successful import, --help, quickstart command or passing test suite; NOT_TESTED when none was attempted.

| repo | kind | install | build | import | --help | quickstart | tests | test counts | attribution | reason | time-to-first-run (s) | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| YARQA-ATTN | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | ERROR | UNKNOWN (not parsed) | REPO_DEFECT | repo: tests import torch but it is not declared in the installed dependency set | NOT_TESTED | admitted from interim run (HEAD at test bb15b7da; unchanged) |
| a11oy | python | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | install failed | NOT_TESTED | admitted from interim run (HEAD at test f613fb7b; changed since) |
| <private> | python | yes | NOT_TESTED | yes | yes | NOT_TESTED | PASSED | 89 passed | none | none | 19 | admitted from interim run (HEAD at test f3c01663; changed since) |
| anatomy | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 117 passed | none | none | 34 | fresh (pip-cache fix; pre-fix2 clone) |
| ayllu | python | no | NOT_TESTED | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | no tests directory | NEVER_SUCCEEDED | fresh (pip-cache fix; pre-fix2 clone) |
| david-leads | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | FAILED | 3 error | REPO_DEFECT | repo: test dependency httpx not declared (starlette TestClient) | NOT_TESTED | fresh (pip-cache fix; pre-fix2 clone) |
| frontier-bench | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 102 passed, 1 skipped | none | none | 38.3 | fresh (pip-cache fix; pre-fix2 clone) |
| governed-receipt-spec | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | HOST_LIMITED | 2 failed, 136 passed, 7 error | HOST_PLATFORM | host: Windows symlink privilege (WinError 1314); failing tests not attributed to the repository | NOT_TESTED | fresh (pip-cache fix; pre-fix2 clone) |
| hatun-mcp | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 303 passed | none | none | 67.6 | fresh (pip-cache fix; pre-fix2 clone) |
| holographic-unify | node | yes | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | HOST_LIMITED | UNKNOWN (not parsed) | HOST_PLATFORM | host: POSIX glob in npm test script not expanded by cmd.exe; failing tests not attributed to the repository | NOT_TESTED | fresh (pip-cache fix; pre-fix2 clone) |
| immune | node | yes | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 44 | admitted from interim run (HEAD at test cb5768dd; changed since) |
| khipu-x1 | python | yes | NOT_TESTED | yes | yes | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 57.5 | admitted from interim run (HEAD at test 360bb6c5; changed since) |
| killinchu | python | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | install failed | NOT_TESTED | admitted from interim run (HEAD at test 12a3d988; changed since) |
| lyte-lattice | node | yes | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 42.7 | admitted from interim run (HEAD at test 309d759c; unchanged) |
| lyte-services | python | yes | NOT_TESTED | no | no | NOT_TESTED | PASSED | 270 passed, 7 skipped | none | none | 82.1 | admitted from interim run (HEAD at test 9ce4e6b5; changed since) |
| nexus | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | no tests directory | NOT_TESTED | admitted from interim run (HEAD at test d0876940; unchanged) |
| quant-curve | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | AUDIT_HARNESS | harness: pytest could not be installed in the audit venv | NOT_TESTED | admitted from interim run (HEAD at test 26135bcc; unchanged) |
| retrieval-bench | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | AUDIT_HARNESS | harness: pytest could not be installed in the audit venv | NOT_TESTED | admitted from interim run (HEAD at test 0a84d06d; unchanged) |
| szl-atelier | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | AUDIT_HARNESS | harness: pytest could not be installed in the audit venv | NOT_TESTED | admitted from interim run (HEAD at test 508ec899; changed since) |
| szl-block-kv | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | FAILED | 3 error | REPO_DEFECT | repo: tests import torch but it is not declared in the installed dependency set | NOT_TESTED | admitted from interim run (HEAD at test 27ef2f71; unchanged) |
| szl-blocked | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 58 passed | none | none | 22.3 | admitted from interim run (HEAD at test 5873409a; changed since) |
| szl-calibration | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 41 passed | none | none | 55.8 | admitted from interim run (HEAD at test 6a7973aa; changed since) |
| szl-ci-witness | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 58 passed | none | none | 17.7 | admitted from interim run (HEAD at test fd50310f; changed since) |
| szl-command-lab | node | yes | no | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 50.5 | admitted from interim run (HEAD at test 88dc7c6c; unchanged) |
| szl-crosscheck | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 51 passed | none | none | 27.9 | admitted from interim run (HEAD at test 998fd8b3; changed since) |
| szl-eclipse | python | yes | NOT_TESTED | yes | NOT_TESTED | yes | PASSED | 15 passed | none | none | 34.2 | admitted from interim run (HEAD at test 8739668a; changed since) |
| szl-energy-attest | python | yes | NOT_TESTED | yes | yes | NOT_TESTED | UNRESOLVED | 1 failed, 96 passed, 3 skipped | POSSIBLE_HARNESS | failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required | 35.9 | admitted from interim run (HEAD at test 217ba7d5; unchanged) |
| szl-engine-bench | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 119 passed | none | none | 33.9 | admitted from interim run (HEAD at test c5ec41b9; unchanged) |
| szl-forge | python | yes | NOT_TESTED | no | NOT_TESTED | NOT_TESTED | UNRESOLVED | 50 failed, 968 passed, 3 skipped | POSSIBLE_HARNESS | failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required | 76.2 | admitted from interim run (HEAD at test 26ae8bfc; changed since) |
| szl-frontier | python | yes | NOT_TESTED | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | no tests directory | 24.4 | admitted from interim run (HEAD at test d24d7a22; changed since) |
| szl-govsign | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 11 passed | none | none | 27.8 | admitted from interim run (HEAD at test 1eba876a; unchanged) |
| szl-guardrail-receipt | python | yes | NOT_TESTED | yes | no | NOT_TESTED | PASSED | 24 passed | none | none | 33.5 | admitted from interim run (HEAD at test e7ef3d79; changed since) |
| szl-invariants | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 63 passed, 2 skipped | none | none | 25.9 | admitted from interim run (HEAD at test a88731a0; unchanged) |
| szl-khipu | python | yes | NOT_TESTED | yes | no | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 87 | admitted from interim run (HEAD at test ef7e85a1; changed since) |
| szl-maskmod | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | AUDIT_HARNESS | harness: pytest could not be installed in the audit venv | NOT_TESTED | admitted from interim run (HEAD at test 8c22afce; changed since) |
| szl-mesh | python | yes | NOT_TESTED | no | no | NOT_TESTED | FAILED | 3 error, 1 skipped | REPO_DEFECT | repo: tests import undeclared module 'fastapi' | 28.3 | admitted from interim run (HEAD at test 4f72f452; unchanged) |
| szl-nemo | python | yes | NOT_TESTED | yes | yes | NOT_TESTED | PASSED | 85 passed | none | none | 33.8 | admitted from interim run (HEAD at test f7cce8e4; unchanged) |
| szl-ouroboros | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 40 passed | none | none | 20.1 | admitted from interim run (HEAD at test 209a6439; changed since) |
| szl-platform | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | none | no tests directory | NOT_TESTED | admitted from interim run (HEAD at test 53c3f3d8; unchanged) |
| szl-provctl | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASSED | 3 passed | none | none | 18.1 | admitted from interim run (HEAD at test 7e416471; unchanged) |
| szl-quant | node | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | UNRESOLVED | UNKNOWN (not parsed) | POSSIBLE_HARNESS | failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required | NOT_TESTED | admitted from interim run (HEAD at test 4014c640; changed since) |
| szl-quant-bench | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 40 passed | none | none | 16.8 | admitted from interim run (HEAD at test 9364ee78; unchanged) |
| szl-real-estate | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 16 passed | none | none | 18.3 | admitted from interim run (HEAD at test 8961ba7e; changed since) |
| szl-receipt | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 71 passed | none | none | 34 | admitted from interim run (HEAD at test c3ad652f; unchanged) |
| szl-receipt-attn | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | ERROR | UNKNOWN (not parsed) | REPO_DEFECT | repo: tests import torch but it is not declared in the installed dependency set | NOT_TESTED | admitted from interim run (HEAD at test dd0b8c8f; unchanged) |
| szl-retrieval-bench | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 28 passed | none | none | 22.8 | admitted from interim run (HEAD at test 54f5dd96; unchanged) |
| szl-router | python | yes | NOT_TESTED | no | no | NOT_TESTED | PASSED | 258 passed, 3 skipped | none | none | 44.7 | admitted from interim run (HEAD at test 00b07f17; changed since) |
| szl-second-brain | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | FAILED | 4 error | REPO_DEFECT | repo: test dependency httpx not declared (starlette TestClient) | 53.7 | admitted from interim run (HEAD at test 25c12301; unchanged) |
| szl-seismic-review | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | FAILED | 2 error | REPO_DEFECT | repo: test dependency httpx not declared (starlette TestClient) | NOT_TESTED | admitted from interim run (HEAD at test 8eb74d53; unchanged) |
| szl-serve | python | yes | NOT_TESTED | yes | yes | NOT_TESTED | UNRESOLVED | UNKNOWN (not parsed) | POSSIBLE_HARNESS | failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required | 38.8 | admitted from interim run (HEAD at test 201a7b3d; unchanged) |
| szl-sovereign-os | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 11 passed | none | none | 23.2 | admitted from interim run (HEAD at test a18f76e9; changed since) |
| szl-substrate | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 206 passed | none | none | 65.2 | admitted from interim run (HEAD at test 5b4d0d5b; unchanged) |
| szl-vertical-forge | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 17 passed | none | none | 28.5 | admitted from interim run (HEAD at test 6a05a170; changed since) |
| szl-wave1-report | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | PASSED | 41 passed | none | none | 28.5 | admitted from interim run (HEAD at test f5370d55; unchanged) |
| vertical-services | python | yes | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | UNRESOLVED | 4 error | POSSIBLE_HARNESS | failure recorded under the interim harness (no repository cause recognised); re-run under harness fix2 required | NOT_TESTED | admitted from interim run (HEAD at test f487dc0f; changed since) |
| vsp-otel | python | yes | NOT_TESTED | no | NOT_TESTED | NOT_TESTED | PASSED | UNKNOWN (not parsed) | none | none | 68.9 | admitted from interim run (HEAD at test b88ec43a; changed since) |
| yarqa | python | yes | NOT_TESTED | yes | NOT_TESTED | NOT_TESTED | FAILED | 2 error, 2 skipped | REPO_DEFECT | repo: tests import undeclared module 'fastapi' | 67.3 | admitted from interim run (HEAD at test 99e16ae4; unchanged) |

## Per-repository evidence

### .github

- https://github.com/szl-holdings/.github · visibility public · archived no · default main · HEAD 07a8f17683f2 · pushed 2026-09-25T16:39:14Z · size 13204 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 50 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets deletion, non_fast_forward, required_linear_history, required_signatures, pull_request, required_status_checks, merge_queue, commit_message_pattern
  - **identity**: PARTIAL — description present (112 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=98, static test functions=1477, dirs=['.github/tests', 'tests']; execution NOT_TESTED in this run
  - **ci**: PASS — >=100 (first page only) workflows; gate workflows latest (grouped by workflow): SZL Doctrine Check=success, Tests=success, ci=success; newest gate run 0d ago; failing non-gate workflows: ['Control-Plane Effect Gate', 'Estate dead-man supervisor', 'FORGE-9 attest and approve', 'HF Living Constellation Operator', 'Hugging Face organization front door (central)', 'Protected Merge Queue Enqueue', 'Publish Nexus Space', 'SZL Responsive Estate v3']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'shell_true': 2, 'tar_extractall_unfiltered': 2}; traversal-defense seen=True
  - **docs**: FAIL — README (10547 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 25 links checked; broken=['https://github.com/szl-holdings/uds-mesh', 'https://huggingface.co/datasets/SZLHOLDINGS/doctrine-v11']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 105d; abandoned branches (>90d) 0

### a11oy

- https://github.com/szl-holdings/a11oy · visibility public · archived no · default main · HEAD 53366a17087c · pushed 2026-09-25T17:22:46Z · size 48389 KB · language Python · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 3 · code scanning open >=100 (first page only) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-xpb63tal\env` → 0 (10.88 s); `--disable-pip-version-check -q -r requirements.txt` → 1 (2.7 s); `<tmp>\szl-smoke-xpb63tal\env\Scripts\python.exe -c import a11oy` → 1 (0.06 s); `<tmp>\szl-smoke-xpb63tal\env\Scripts\python.exe -c import a11oy_code` → 1 (0.05 s); `<tmp>\szl-smoke-xpb63tal\env\Scripts\python.exe -c import ayllu` → 1 (0.06 s)
  - **identity**: PASS — description present (107 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['docs/site/package-lock.json', 'formal/LutarPolicy/lake-manifest.json', 'package-lock.json']; build path=['Containerfile', 'Dockerfile']
  - **tests**: PARTIAL — test files=686, static test functions=7283, dirs=['__tests__', 'anatomy-ledger/tests', 'payloads/tests']; execution NOT_TESTED in this run
  - **ci**: PASS — >=100 (first page only) workflows; gate workflows latest (grouped by workflow): Container build + GHCR push=success, Docs CI=success, GHCR Build + Push (uds-v0.3.0)=success, HF Corpus Guards — Self-test=success, Lockfile Registry Check=success, Private-IP Leak Check=success, README frontmatter check=success, Tests=success; newest gate run 0d ago; failing non-gate workflows: ['HF Ecosystem manifest drift', 'HF tooling product integration', 'npm_and_yarn in /., /docs/site, /runtime/ouroboros, /web/console - Update #1592119908']
  - **release_integrity**: PASS — latest=v1.0.0; notes=3768 chars; assets=1 hashed=1; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'yaml_unsafe_load': 2}; traversal-defense seen=True
  - **docs**: FAIL — README (12655 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 25 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/anatomy', 'https://huggingface.co/spaces/SZLHOLDINGS/cosmos', 'https://huggingface.co/spaces/SZLHOLDINGS/sda']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 88d; abandoned branches (>90d) 0

### <private>

- https://github.com/szl-holdings/<private> · visibility public · archived no · default main · HEAD 45d125b39785 · pushed 2026-09-25T15:53:00Z · size 620 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-x2ue_l1d\env` → 0 (8.91 s); `install --disable-pip-version-check -q .` → 0 (9.86 s); `<tmp>\szl-smoke-x2ue_l1d\env\Scripts\python.exe -c import a11oy_factory` → 0 (0.22 s); `<tmp>\szl-smoke-x2ue_l1d\env\Scripts\<private>.exe --help` → 0 (0.33 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.92 s)
  - **identity**: PARTIAL — description present (85 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['package-lock.json']; build path=['Dockerfile']
  - **tests**: PASS — test files=24, static test functions=334, dirs=['tests']; executed: {'passed': 89}
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: ['factory-supply-chain-assurance']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=19.0s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### a11oy-net

- https://github.com/szl-holdings/a11oy-net · visibility public · archived no · default main · HEAD d662690611af · pushed 2026-09-25T16:38:29Z · size 2578 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (88 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=14, static test functions=81, dirs=['spec', 'tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 55 workflows; gate workflows latest (grouped by workflow): Link & Asset Check=success, base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (13373 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'not a proof'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 25 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### anatomy

- https://github.com/szl-holdings/anatomy · visibility public · archived no · default main · HEAD f555688556fe · pushed 2026-09-24T22:14:21Z · size 875 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 28 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-ij1pfz4r\env` → 0 (11.16 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (14.17 s); `-q -p no:cacheprovider --maxfail=50` → 0 (8.64 s)
  - **identity**: PARTIAL — description present (237 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 3, 'requirements_pinned_eq': 3}; no reproducible build definition
  - **tests**: PASS — test files=15, static test functions=117, dirs=['tests']; executed: {'passed': 117}
  - **ci**: PASS — 24 workflows; gate workflows latest (grouped by workflow): Pin Check=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=34.0s
  - **honest_scoping**: PASS — scoping statement: 'does not prove'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 30 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg', 'https://huggingface.co/spaces/SZLHOLDINGS/cosmos', 'https://huggingface.co/spaces/SZLHOLDINGS/governed-receipt-verifier', 'https://huggingface.co/spaces/SZLHOLDINGS/holographic', 'https://huggingface.co/spaces/SZLHOLDINGS/sda']
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### ayllu

- https://github.com/szl-holdings/ayllu · visibility public · archived no · default main · HEAD ae8ff0809231 · pushed 2026-09-14T02:00:42Z · size 532 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-7_gxs3hr\env` → 0 (11.16 s); `install --disable-pip-version-check -q .[test]` → 1 (9.45 s); `<tmp>\szl-smoke-7_gxs3hr\env\Scripts\python.exe -c import ayllu` → 1 (0.05 s)
  - **identity**: PARTIAL — description present (214 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 3, 'requirements_pinned_eq': 0, 'pyproject_deps': 3, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=13, static test functions=65, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 5 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 11d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=NEVER_SUCCEEDEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 4 links checked; broken=[]
  - **maintenance**: PASS — last push 11d ago; oldest open issue none open; abandoned branches (>90d) 0

### ayllu-hf-space

- https://github.com/szl-holdings/ayllu-hf-space · visibility public · archived no · default main · HEAD 4ab0f246e6cf · pushed 2026-09-20T11:42:50Z · size 15 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (84 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: FAIL — no test files found
  - **ci**: FAIL — no GitHub Actions workflows
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (1300 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 4 links checked; broken=[]
  - **maintenance**: PASS — last push 5d ago; oldest open issue none open; abandoned branches (>90d) 0

### cosmos

- https://github.com/szl-holdings/cosmos · visibility public · archived yes · default main · HEAD af6ff5ec87e2 · pushed 2026-08-29T16:15:45Z · size 218 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata none · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (79 chars); maturity stated=True; non-claims stated=False
  - **license**: NOT_TESTED — metadata: none; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: FAIL — no GitHub Actions workflows
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### counsel

- https://github.com/szl-holdings/counsel · visibility public · archived yes · default main · HEAD f2c3e3ccf053 · pushed 2026-08-29T16:57:45Z · size 32 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata none · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (77 chars); maturity stated=True; non-claims stated=False
  - **license**: NOT_TESTED — metadata: none; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 4 workflows; no push/PR-triggered test/build run among the last 20 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### david-leads

- https://github.com/szl-holdings/david-leads · visibility public · archived no · default main · HEAD 523fbee7b5fa · pushed 2026-09-25T12:35:56Z · size 3849 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-of5u_xy2\env` → 0 (11.16 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (57.7 s); `<tmp>\szl-smoke-of5u_xy2\env\Scripts\python.exe -c import app` → 1 (0.06 s); `-q -p no:cacheprovider --maxfail=50` → 2 (2.58 s)
  - **identity**: PARTIAL — description present (137 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 5, 'requirements_pinned_eq': 5}; no reproducible build definition
  - **tests**: FAIL — test files=31, static test functions=414, dirs=['tests']; executed: {'error': 3}; attribution REPO_DEFECT: repo: test dependency httpx not declared (starlette TestClient)
  - **ci**: PASS — 26 workflows; gate workflows latest (grouped by workflow): CI — operational safety=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (11374 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 5 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### developers

- https://github.com/szl-holdings/developers · visibility public · archived yes · default main · HEAD dde99af0564c · pushed 2026-07-29T23:07:25Z · size 141 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (81 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 4 workflows; gate workflows latest (grouped by workflow): Pin Check=success; newest gate run 58d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 58d ago; oldest open issue none open; abandoned branches (>90d) 7

### docs-site

- https://github.com/szl-holdings/docs-site · visibility public · archived yes · default main · HEAD 83664f8b8924 · pushed 2026-08-28T15:41:19Z · size 6078 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets required_status_checks, deletion
  - **identity**: PARTIAL — description present (81 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 17 workflows; gate workflows latest (grouped by workflow): Lockfile Registry Check=success, Pin Check=success; newest gate run 28d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 28d ago; oldest open issue 38d; abandoned branches (>90d) 2

### energy-attest-holo

- https://github.com/szl-holdings/energy-attest-holo · visibility public · archived yes · default main · HEAD 6851c00110b2 · pushed 2026-08-18T00:23:33Z · size 281 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows, required_signatures, pull_request, non_fast_forward, required_linear_history, required_status_checks
  - **identity**: PARTIAL — description present (89 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 3 default-branch runs; failing non-gate workflows: ['Governed static Space release']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 39d ago; oldest open issue none open; abandoned branches (>90d) 0

### evidence-doctrine

- https://github.com/szl-holdings/evidence-doctrine · visibility public · archived no · default main · HEAD 0ce92dfab23b · pushed 2026-09-24T17:52:09Z · size 58 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `install --ignore-scripts --no-audit --no-fund` → 1 (12.92 s)
  - **identity**: PARTIAL — description present (88 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=2, static test functions=29, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PASS — 1 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### evidence-studio

- https://github.com/szl-holdings/evidence-studio · visibility public · archived no · default main · HEAD 777c3bf16e7c · pushed 2026-09-25T09:32:01Z · size 37 KB · language Python · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (94 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=3, static test functions=36, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 1 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (2954 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### evidence-typed-formula-governance

- https://github.com/szl-holdings/evidence-typed-formula-governance · visibility public · archived yes · default main · HEAD 775ee23b5d4c · pushed 2026-07-21T03:28:34Z · size 6 KB · language UNAVAILABLE · stars 0 · forks 0 · watchers 0 · licence metadata none · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (122 chars); maturity stated=False; non-claims stated=False
  - **license**: NOT_TESTED — metadata: none; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: FAIL — no GitHub Actions workflows
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=422 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 66d ago; oldest open issue none open; abandoned branches (>90d) 0

### fail-closed-governed-ai-services

- https://github.com/szl-holdings/fail-closed-governed-ai-services · visibility public · archived yes · default main · HEAD 40d1b710ac89 · pushed 2026-07-21T03:28:38Z · size 3 KB · language UNAVAILABLE · stars 0 · forks 0 · watchers 0 · licence metadata none · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (107 chars); maturity stated=False; non-claims stated=False
  - **license**: NOT_TESTED — metadata: none; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: FAIL — no GitHub Actions workflows
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=422 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 66d ago; oldest open issue none open; abandoned branches (>90d) 0

### frontier-bench

- https://github.com/szl-holdings/frontier-bench · visibility public · archived no · default main · HEAD 6a813593e466 · pushed 2026-09-20T11:43:00Z · size 220 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-70791g71\env` → 0 (12.12 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (15.22 s); `<tmp>\szl-smoke-70791g71\env\Scripts\python.exe -c import harness` → 1 (0.06 s); `-q -p no:cacheprovider --maxfail=50` → 0 (10.86 s)
  - **identity**: PARTIAL — description present (281 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 2, 'requirements_pinned_eq': 0}
  - **tests**: PASS — test files=9, static test functions=103, dirs=['tests']; executed: {'passed': 102, 'skipped': 1}
  - **ci**: PASS — 3 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 5d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=True
  - **docs**: FAIL — README (2664 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 5d ago; oldest open issue none open; abandoned branches (>90d) 0

### governance-as-code

- https://github.com/szl-holdings/governance-as-code · visibility public · archived no · default main · HEAD f16df42e52e6 · pushed 2026-09-23T15:57:36Z · size 422 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (127 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=3, static test functions=18, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 8 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 2d ago; failing non-gate workflows: ['hf-consolidate-one-shot']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: PASS — scoping statement: 'does not prove'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### governed-inference-meter

- https://github.com/szl-holdings/governed-inference-meter · visibility public · archived yes · default main · HEAD aee6466ecaaa · pushed 2026-08-30T13:35:31Z · size 170 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (190 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: FAIL — 6 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success, hf-mirror-drift-check=failure; newest gate run 26d ago; failing non-gate workflows: ['hf-mirror']
  - **release_integrity**: PARTIAL — latest=v0.3.0; notes=534 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 26d ago; oldest open issue none open; abandoned branches (>90d) 0

### governed-norm-holo

- https://github.com/szl-holdings/governed-norm-holo · visibility public · archived yes · default main · HEAD 05b87ab4d00e · pushed 2026-08-29T01:32:19Z · size 224 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows, required_signatures, pull_request, non_fast_forward, required_linear_history, required_status_checks
  - **identity**: PARTIAL — description present (87 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 6 workflows; no push/PR-triggered test/build run among the last 7 default-branch runs; failing non-gate workflows: ['Governed static Space release']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 28d ago; oldest open issue none open; abandoned branches (>90d) 0

### governed-receipt-spec

- https://github.com/szl-holdings/governed-receipt-spec · visibility public · archived no · default main · HEAD 2c82320a9946 · pushed 2026-09-24T18:56:41Z · size 208 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets required_status_checks
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-s4s65heq\env` → 0 (11.44 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (7.12 s); `-q -p no:cacheprovider --maxfail=50` → 1 (1.94 s)
  - **identity**: PASS — description present (235 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 2, 'requirements_pinned_eq': 2}; no reproducible build definition
  - **tests**: PARTIAL — test files=9, static test functions=145, dirs=['tests']; executed: {'failed': 2, 'passed': 136, 'error': 7}; HOST_LIMITED: host: Windows symlink privilege (WinError 1314); failing tests not attributed to the repository
  - **ci**: PASS — 7 workflows; gate workflows latest (grouped by workflow): base-python-ci=success, verify=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: PASS — scoping statement: 'NOT a proof'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: FAIL — 4 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/governed-receipt-verifier']
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### hatun-mcp

- https://github.com/szl-holdings/hatun-mcp · visibility public · archived no · default main · HEAD e2f7fe931980 · pushed 2026-09-24T13:03:26Z · size 528 KB · language Python · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 8 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-pqu89u8z\env` → 0 (10.66 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (46.62 s); `<tmp>\szl-smoke-pqu89u8z\env\Scripts\python.exe -c import hatun_mcp` → 1 (0.06 s); `-q -p no:cacheprovider --maxfail=50` → 0 (10.28 s)
  - **identity**: PARTIAL — description present (162 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 8, 'requirements_pinned_eq': 0}
  - **tests**: PASS — test files=14, static test functions=174, dirs=['tests']; executed: {'passed': 303}
  - **ci**: PASS — 24 workflows; gate workflows latest (grouped by workflow): Pin Check=success, ci=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=mirror-2026-06-01; notes=214 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=67.6s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 7 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 2

### holographic-unify

- https://github.com/szl-holdings/holographic-unify · visibility public · archived no · default main · HEAD 7d03a8c45f97 · pushed 2026-09-12T09:33:38Z · size 202 KB · language TypeScript · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `install --ignore-scripts --no-audit --no-fund` → 0 (72.2 s); `C:\Program Files\nodejs\npm.CMD run build` → 1 (0.56 s); `C:\Program Files\nodejs\npm.CMD test --silent` → 1 (0.61 s)
  - **identity**: PASS — description present (114 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=3, static test functions=38, dirs=['tests']; executed: {}; HOST_LIMITED: host: POSIX glob in npm test script not expanded by cmd.exe; failing tests not attributed to the repository
  - **ci**: PARTIAL — 2 workflows; no push/PR-triggered test/build run among the last 17 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: PASS — scoping statement: 'What it is not'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 7 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg']
  - **maintenance**: PASS — last push 13d ago; oldest open issue none open; abandoned branches (>90d) 0

### immune

- https://github.com/szl-holdings/immune · visibility public · archived no · default main · HEAD 24d3da298ecc · pushed 2026-09-25T16:28:29Z · size 1157 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 2 · code scanning open 32 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
- smoke commands: `install --ignore-scripts --no-audit --no-fund` → 0 (26.28 s); `C:\Program Files\nodejs\npm.CMD run build` → 1 (1.59 s); `C:\Program Files\nodejs\npm.CMD test --silent` → 0 (16.14 s)
  - **identity**: PARTIAL — description present (201 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['pnpm-lock.yaml']; build path=['frontend/deploy/Dockerfile', 'python/Dockerfile']
  - **tests**: PASS — test files=13, static test functions=145, dirs=['python/tests', 'tests']; executed: {}
  - **ci**: PASS — 31 workflows; gate workflows latest (grouped by workflow): CI=success, Lockfile Registry Check=success, base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: ['npm_and_yarn in /. - Update #1592062762']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=44.0s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 7 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### immune-lattice

- https://github.com/szl-holdings/immune-lattice · visibility public · archived yes · default main · HEAD bcee352e584f · pushed 2026-08-29T16:49:22Z · size 602 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata NOASSERTION · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (78 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=NOASSERTION; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 1 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### khipu-consensus

- https://github.com/szl-holdings/khipu-consensus · visibility public · archived no · default main · HEAD 18869473d8ff · pushed 2026-09-24T13:03:40Z · size 182 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 8 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (211 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=7, static test functions=46, dirs=['python/tests', 'typescript/test']; execution NOT_TESTED in this run
  - **ci**: PASS — 10 workflows; gate workflows latest (grouped by workflow): Pin Check=success, khipu-consensus-ci=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 11 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/khipu-constellation']
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### khipu-lab

- https://github.com/szl-holdings/khipu-lab · visibility public · archived yes · default main · HEAD d0a3a20bdbc7 · pushed 2026-08-29T17:20:40Z · size 640 KB · language TypeScript · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (81 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 15 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### khipu-pages

- https://github.com/szl-holdings/khipu-pages · visibility public · archived yes · default main · HEAD f56e5327b61c · pushed 2026-08-29T16:08:16Z · size 9 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata none · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (81 chars); maturity stated=True; non-claims stated=False
  - **license**: NOT_TESTED — metadata: none; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 3 default-branch runs; failing non-gate workflows: ['pages']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### khipu-sda-core

- https://github.com/szl-holdings/khipu-sda-core · visibility public · archived no · default main · HEAD ebd0ae2749cc · pushed 2026-09-24T12:56:22Z · size 121 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 5 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (227 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 8, 'requirements_pinned_eq': 0}
  - **tests**: PARTIAL — test files=7, static test functions=38, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 8 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### khipu-x1

- https://github.com/szl-holdings/khipu-x1 · visibility public · archived no · default main · HEAD c0e41f0b471e · pushed 2026-09-25T16:08:20Z · size 154 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-f4f8zk82\env` → 0 (14.09 s); `install --disable-pip-version-check -q .[dev]` → 0 (42.41 s); `<tmp>\szl-smoke-f4f8zk82\env\Scripts\python.exe -c import khipu_x1` → 0 (1.01 s); `<tmp>\szl-smoke-f4f8zk82\env\Scripts\khipu-x1.exe --help` → 0 (0.31 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.83 s)
  - **identity**: PASS — description present (121 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=1, static test functions=7, dirs=['spec', 'tests']; executed: {}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=57.5s
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### killinchu

- https://github.com/szl-holdings/killinchu · visibility public · archived no · default main · HEAD f5b568adb264 · pushed 2026-09-25T16:54:02Z · size 16262 KB · language Python · stars 0 · forks 1 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 44 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-6vkkr0mf\env` → 0 (10.88 s); `--disable-pip-version-check -q -r requirements.txt` → 1 (10.22 s); `<tmp>\szl-smoke-6vkkr0mf\env\Scripts\python.exe -c import killinchu` → 1 (0.09 s); `<tmp>\szl-smoke-6vkkr0mf\env\Scripts\python.exe -c import szl_connectors` → 1 (0.06 s); `<tmp>\szl-smoke-6vkkr0mf\env\Scripts\python.exe -c import szl_shared_formulas` → 1 (0.08 s)
  - **identity**: PARTIAL — description present (138 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 3, 'requirements_pinned_eq': 1}
  - **tests**: PARTIAL — test files=106, static test functions=977, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: FAIL — >=100 (first page only) workflows; gate workflows latest (grouped by workflow): CI=success, Dockerfile build-file guard=success, GHCR Build + Push (immutable commit SHA)=failure, README frontmatter check=success, base-python-ci=success, vendor-sync-check=success; newest gate run 0d ago; failing non-gate workflows: ['Sync to HuggingFace Space']
  - **release_integrity**: PARTIAL — latest=v1.0.0; notes=3741 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'os_system': 3}; traversal-defense seen=True
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 37 links checked; broken=['https://github.com/szl-holdings/killinchu}', 'https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 2

### lambda-gate-holo

- https://github.com/szl-holdings/lambda-gate-holo · visibility public · archived yes · default main · HEAD 0303c8ae0d81 · pushed 2026-08-29T00:08:48Z · size 131 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows, required_signatures, pull_request, non_fast_forward, required_linear_history, required_status_checks
  - **identity**: PARTIAL — description present (87 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 6 workflows; no push/PR-triggered test/build run among the last 6 default-branch runs; failing non-gate workflows: ['Governed static Space release']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 28d ago; oldest open issue none open; abandoned branches (>90d) 0

### lean-kernel

- https://github.com/szl-holdings/lean-kernel · visibility public · archived yes · default main · HEAD 5be5d1450242 · pushed 2026-08-28T04:49:20Z · size 160 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (82 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 12 workflows; gate workflows latest (grouped by workflow): Pin Check=success, ci=success, kernel-build-verify=success; newest gate run 28d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=mirror-2026-06-01; notes=216 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 28d ago; oldest open issue none open; abandoned branches (>90d) 0

### lutar-lean

- https://github.com/szl-holdings/lutar-lean · visibility public · archived no · default main · HEAD 75a4a3112287 · pushed 2026-09-25T13:45:12Z · size 4213 KB · language Lean · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 17 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks yes) · rulesets deletion, non_fast_forward, required_linear_history, pull_request
  - **identity**: PARTIAL — description present (238 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=['lake-manifest.json']; pinning={}; no reproducible build definition
  - **tests**: PARTIAL — test files=5, static test functions=35, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 36 workflows; gate workflows latest (grouped by workflow): CI=success, Lake build (gate + numbers)=success, Lean kernel check=success, Pin Check=success, Tests=success, base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=lutar-v18.0.0; notes=2755 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 20 links checked; broken=['https://github.com/szl-holdings/lambda-bounty', 'https://huggingface.co/spaces/SZLHOLDINGS/lambda-aggregator-live']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 2d; abandoned branches (>90d) 3

### lyte-lattice

- https://github.com/szl-holdings/lyte-lattice · visibility public · archived no · default main · HEAD 309d759c26ca · pushed 2026-09-24T12:45:49Z · size 756 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `ci --ignore-scripts --no-audit --no-fund` → 0 (37.56 s); `C:\Program Files\nodejs\npm.CMD run build` → 127 (0.52 s); `C:\Program Files\nodejs\npm.CMD test --silent` → 0 (4.62 s)
  - **identity**: PARTIAL — description present (107 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['package-lock.json']; build path=['Dockerfile', 'space/Dockerfile']
  - **tests**: PASS — test files=15, static test functions=259, dirs=[]; executed: {}
  - **ci**: FAIL — 4 workflows; gate workflows latest (grouped by workflow): CI=success, Verify canonical Lyte publication ownership=success, Verify central Hugging Face publication ownership=failure; newest gate run 1d ago; failing non-gate workflows: ['Hugging Face publication pipeline']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=42.7s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 10 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg']
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### lyte-services

- https://github.com/szl-holdings/lyte-services · visibility public · archived no · default main · HEAD 38894296c6e7 · pushed 2026-09-25T16:07:56Z · size 2485 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets deletion, non_fast_forward, required_linear_history, required_signatures, pull_request, required_status_checks
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-frvy8gdp\env` → 0 (9.86 s); `install --disable-pip-version-check -q .[test]` → 0 (72.02 s); `<tmp>\szl-smoke-frvy8gdp\env\Scripts\python.exe -c import a11oy_factory` → 1 (0.11 s); `<tmp>\szl-smoke-frvy8gdp\env\Scripts\python.exe -c import benchmarks` → 1 (0.08 s); `<tmp>\szl-smoke-frvy8gdp\env\Scripts\python.exe -c import lyte` → 0 (0.06 s); `<tmp>\szl-smoke-frvy8gdp\env\Scripts\lyte.exe --help` → TIMEOUT (120.09 s); `-q -p no:cacheprovider --maxfail=50` → 0 (20.5 s)
  - **identity**: PARTIAL — description present (87 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 14, 'requirements_pinned_eq': 14, 'pyproject_deps': 14, 'pyproject_deps_pinned_eq': 14}; no reproducible build definition
  - **tests**: PASS — test files=20, static test functions=153, dirs=['tests']; executed: {'passed': 270, 'skipped': 7}
  - **ci**: PARTIAL — 4 workflows; no push/PR-triggered test/build run among the last 42 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=82.1s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### nexus

- https://github.com/szl-holdings/nexus · visibility public · archived no · default main · HEAD d08769408825 · pushed 2026-09-22T14:08:39Z · size 784 KB · language TypeScript · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-6tm77vau\env` → 0 (9.73 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (2.16 s)
  - **identity**: PARTIAL — description present (208 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['package-lock.json']; build path=['Dockerfile', 'space/Dockerfile']
  - **tests**: PARTIAL — test files=15, static test functions=301, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 2 workflows; no push/PR-triggered test/build run among the last 32 default-branch runs; failing non-gate workflows: ['Hugging Face publication pipeline']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 4 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg']
  - **maintenance**: PASS — last push 3d ago; oldest open issue none open; abandoned branches (>90d) 0

### ouroboros

- https://github.com/szl-holdings/ouroboros · visibility public · archived yes · default main · HEAD 0f030741f567 · pushed 2026-08-28T04:40:58Z · size 1286 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets deletion, non_fast_forward, required_linear_history, pull_request, required_status_checks
  - **identity**: PARTIAL — description present (162 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 16 workflows; gate workflows latest (grouped by workflow): CI=success, Lockfile Registry Check=success, Pin Check=success, Tests=success; newest gate run 28d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v6.4.1; notes=353 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 28d ago; oldest open issue none open; abandoned branches (>90d) 0

### platform

- https://github.com/szl-holdings/platform · visibility public · archived no · default main · HEAD e3ef7a9e07c7 · pushed 2026-09-25T17:17:26Z · size 695191 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata NOASSERTION · bus factor 1
- Dependabot open 7 · code scanning open 19 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets deletion, non_fast_forward, required_signatures, pull_request, required_status_checks
  - **identity**: PARTIAL — description present (143 chars); maturity stated=False; non-claims stated=False
  - **license**: PARTIAL — metadata license=NOASSERTION; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 100 workflows; no push/PR-triggered test/build run among the last 60 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v1.0.1-codex-kernel; notes=5583 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PASS — last push 0d ago; oldest open issue 14d; abandoned branches (>90d) 1

### puriq-live

- https://github.com/szl-holdings/puriq-live · visibility public · archived no · default main · HEAD 3972a0ed5fd1 · pushed 2026-09-23T14:12:32Z · size 227 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (172 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 5, 'requirements_pinned_eq': 5, 'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}; no reproducible build definition
  - **tests**: PARTIAL — test files=8, static test functions=61, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 8 workflows; gate workflows latest (grouped by workflow): PURIQ Market Chamber CI=success; newest gate run 2d ago; failing non-gate workflows: ['Publish PURIQ Hugging Face Space']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### quant-curve

- https://github.com/szl-holdings/quant-curve · visibility public · archived no · default main · HEAD 26135bcc03e9 · pushed 2026-09-23T14:12:45Z · size 37 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-dxzh3rx_\env` → 0 (10.11 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (16.03 s); `<tmp>\szl-smoke-dxzh3rx_\env\Scripts\python.exe -c import quant_curve` → 1 (0.06 s); `-q -p no:cacheprovider --maxfail=50` → 1 (0.06 s)
  - **identity**: PARTIAL — description present (297 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 2, 'requirements_pinned_eq': 0}
  - **tests**: PARTIAL — test files=2, static test functions=17, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 3 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 2d ago; failing non-gate workflows: ['bench-pipeline']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (2701 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 3 links checked; broken=[]
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### receipt-chain-live

- https://github.com/szl-holdings/receipt-chain-live · visibility public · archived yes · default main · HEAD 787891967b41 · pushed 2026-08-26T16:17:28Z · size 251 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows, required_signatures, pull_request, non_fast_forward, required_linear_history, required_status_checks
  - **identity**: PARTIAL — description present (83 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 3 default-branch runs; failing non-gate workflows: ['Governed static Space release']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 30d ago; oldest open issue none open; abandoned branches (>90d) 0

### retrieval-bench

- https://github.com/szl-holdings/retrieval-bench · visibility public · archived no · default main · HEAD 0a84d06de594 · pushed 2026-09-23T13:48:58Z · size 55 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-8wlo0jow\env` → 0 (11.81 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (17.34 s); `<tmp>\szl-smoke-8wlo0jow\env\Scripts\python.exe -c import api` → 1 (0.12 s); `<tmp>\szl-smoke-8wlo0jow\env\Scripts\python.exe -c import retrieval` → 1 (0.09 s); `-q -p no:cacheprovider --maxfail=50` → 1 (0.09 s)
  - **identity**: PARTIAL — description present (274 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 2, 'requirements_pinned_eq': 0}
  - **tests**: PARTIAL — test files=3, static test functions=29, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 3 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 2d ago; failing non-gate workflows: ['bench-pipeline']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (3275 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 3 links checked; broken=[]
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### sda

- https://github.com/szl-holdings/sda · visibility public · archived no · default main · HEAD b12cedf02fc3 · pushed 2026-09-24T17:51:54Z · size 328 KB · language CSS · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PASS — description present (154 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=6, static test functions=23, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 17d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: PASS — scoping statement: 'does not establish'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 6 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg']
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-atelier

- https://github.com/szl-holdings/szl-atelier · visibility public · archived no · default main · HEAD bc7d972bf087 · pushed 2026-09-25T16:13:28Z · size 328 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-65p5ikny\env` → 0 (8.08 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (27.62 s); `-q -p no:cacheprovider --maxfail=50` → 1 (0.08 s)
  - **identity**: PARTIAL — description present (114 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 2, 'requirements_pinned_eq': 0}
  - **tests**: PARTIAL — test files=7, static test functions=67, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 6 workflows; gate workflows latest (grouped by workflow): Archive Revival Showcase CI=success, ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=True
  - **docs**: FAIL — README (3145 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 5 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-block-kv

- https://github.com/szl-holdings/szl-block-kv · visibility public · archived no · default main · HEAD 27ef2f710069 · pushed 2026-09-23T13:48:39Z · size 75 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-suct71n6\env` → 0 (9.23 s); `install --disable-pip-version-check -q .` → 0 (13.36 s); `-q -p no:cacheprovider --maxfail=50` → 2 (0.78 s)
  - **identity**: PARTIAL — description present (133 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: FAIL — test files=4, static test functions=27, dirs=['tests']; executed: {'error': 3}; attribution REPO_DEFECT: repo: tests import torch but it is not declared in the installed dependency set
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 2d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (5685 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'not a proof'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-blocked

- https://github.com/szl-holdings/szl-blocked · visibility public · archived no · default main · HEAD 1efe1a30a1da · pushed 2026-09-25T16:47:08Z · size 88 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-715mjkk3\env` → 0 (10.3 s); `install --disable-pip-version-check -q .` → 0 (11.19 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.84 s)
  - **identity**: PASS — description present (147 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=5, static test functions=24, dirs=['tests']; executed: {'passed': 58}
  - **ci**: PARTIAL — 4 workflows; no push/PR-triggered test/build run among the last 15 default-branch runs; failing non-gate workflows: ['Hub joblib quarantine PR']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (1231 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-brand

- https://github.com/szl-holdings/szl-brand · visibility public · archived no · default main · HEAD ea80c36fe6ca · pushed 2026-09-22T14:08:31Z · size 13985 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata CC-BY-4.0 · bus factor 1
- Dependabot open 0 · code scanning open 1 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets deletion, non_fast_forward, required_linear_history, pull_request
  - **identity**: PARTIAL — description present (129 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (CC-BY-4.0); metadata CC-BY-4.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 2, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=12, static test functions=154, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 16 workflows; gate workflows latest (grouped by workflow): Pin Check=success, Tests=success, ci=success; newest gate run 3d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=91 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=True
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 2 links checked; broken=['https://github.com/szl-holdings/szl-brand}']
  - **maintenance**: PASS — last push 3d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-build-env

- https://github.com/szl-holdings/szl-build-env · visibility public · archived no · default main · HEAD 883b63bd56b8 · pushed 2026-09-25T16:20:59Z · size 155 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 7 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PASS — description present (143 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=4, static test functions=51, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): Pin Check=success; newest gate run 5d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'yaml_unsafe_load': 1}; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: PASS — scoping statement: 'limitations'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 11 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-calibration

- https://github.com/szl-holdings/szl-calibration · visibility public · archived no · default main · HEAD b606f26aa9f5 · pushed 2026-09-25T16:12:59Z · size 64 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-bh3ob31k\env` → 0 (8.0 s); `install --disable-pip-version-check -q .[dev]` → 0 (47.67 s); `<tmp>\szl-smoke-bh3ob31k\env\Scripts\python.exe -c import szl_calibration` → 0 (0.12 s); `-q -p no:cacheprovider --maxfail=50` → 0 (3.08 s)
  - **identity**: PARTIAL — description present (236 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=7, static test functions=62, dirs=['tests']; executed: {'passed': 41}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=55.8s
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: PASS — boundary categories named: ['integrity', 'performance', 'validity']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-ci-witness

- https://github.com/szl-holdings/szl-ci-witness · visibility public · archived no · default main · HEAD f1661e8941a5 · pushed 2026-09-25T16:23:39Z · size 81 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-0gefoa_k\env` → 0 (7.39 s); `install --disable-pip-version-check -q .` → 0 (10.14 s); `<tmp>\szl-smoke-0gefoa_k\env\Scripts\python.exe -c import szl_ci_witness` → 0 (0.16 s); `verify # linkage recompute` → 2 (0.31 s); `runs, green/red, regressions, fixes` → 2 (0.23 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.62 s)
  - **identity**: PARTIAL — description present (251 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=6, static test functions=53, dirs=['tests']; executed: {'passed': 58}
  - **ci**: PASS — 3 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=17.7s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-command-lab

- https://github.com/szl-holdings/szl-command-lab · visibility public · archived no · default main · HEAD 88dc7c6c253a · pushed 2026-09-12T09:09:28Z · size 840 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `ci --ignore-scripts --no-audit --no-fund` → 0 (44.44 s); `C:\Program Files\nodejs\npm.CMD run build` → 127 (0.66 s); `C:\Program Files\nodejs\npm.CMD test --silent` → 0 (5.45 s)
  - **identity**: PASS — description present (94 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['package-lock.json']; build path=['Dockerfile', 'space/Dockerfile']
  - **tests**: PASS — test files=13, static test functions=246, dirs=['tests']; executed: {}
  - **ci**: PASS — 7 workflows; gate workflows latest (grouped by workflow): Verify central Hugging Face publication ownership=success, base-python-ci=success; newest gate run 13d ago; failing non-gate workflows: ['Deploy to HuggingFace Space', 'Hugging Face publication pipeline']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=50.5s
  - **honest_scoping**: PASS — scoping statement: 'does not establish'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 5 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-command-system.svg']
  - **maintenance**: PASS — last push 13d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-constellation

- https://github.com/szl-holdings/szl-constellation · visibility public · archived no · default main · HEAD 93db23287465 · pushed 2026-09-25T00:44:27Z · size 253 KB · language Python · stars 0 · forks 0 · watchers 1 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (312 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=4, static test functions=40, dirs=['space/tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 8 workflows; no push/PR-triggered test/build run among the last 48 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 12 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue 19d; abandoned branches (>90d) 0

### szl-cookbook

- https://github.com/szl-holdings/szl-cookbook · visibility public · archived yes · default main · HEAD 5eb303b4d611 · pushed 2026-08-31T01:32:26Z · size 8526 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets deletion, non_fast_forward, required_linear_history, pull_request
  - **identity**: PARTIAL — description present (81 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 15 workflows; gate workflows latest (grouped by workflow): Lockfile Registry Check=success, Pin Check=success, Tests=success, anatomy-evolved-ci=success, ci=success; newest gate run 26d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=91 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 26d ago; oldest open issue none open; abandoned branches (>90d) 1

### szl-crosscheck

- https://github.com/szl-holdings/szl-crosscheck · visibility public · archived no · default main · HEAD 20bb10ceb63d · pushed 2026-09-25T16:23:35Z · size 63 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-97ipiunc\env` → 0 (14.88 s); `install --disable-pip-version-check -q .` → 0 (12.92 s); `<tmp>\szl-smoke-97ipiunc\env\Scripts\python.exe -c import szl_crosscheck` → 0 (0.12 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.77 s)
  - **identity**: PARTIAL — description present (220 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=6, static test functions=37, dirs=['tests']; executed: {'passed': 51}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=27.9s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PASS — boundary categories named: ['integrity', 'performance', 'validity']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue 20d; abandoned branches (>90d) 0

### szl-doctrine

- https://github.com/szl-holdings/szl-doctrine · visibility public · archived no · default main · HEAD 8e04117cd39a · pushed 2026-09-25T16:41:44Z · size 420 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 5 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets deletion, non_fast_forward, required_linear_history, required_signatures, pull_request, required_status_checks
  - **identity**: PASS — description present (66 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=2, static test functions=79, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PASS — 14 workflows; gate workflows latest (grouped by workflow): Pin Check=success; newest gate run 5d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'yaml_unsafe_load': 1}; traversal-defense seen=False
  - **docs**: FAIL — README (8847 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'does not prove'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 9 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 1d; abandoned branches (>90d) 0

### szl-drift

- https://github.com/szl-holdings/szl-drift · visibility public · archived no · default main · HEAD 35c395450c71 · pushed 2026-09-23T13:47:59Z · size 23 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (106 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=1, static test functions=11, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 2d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (1005 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 3 links checked; broken=[]
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-eclipse

- https://github.com/szl-holdings/szl-eclipse · visibility public · archived no · default main · HEAD cce9e172651f · pushed 2026-09-25T16:23:31Z · size 33 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-qw0e8r5f\env` → 0 (14.2 s); `install --disable-pip-version-check -q .` → 0 (19.92 s); `<tmp>\szl-smoke-qw0e8r5f\env\Scripts\python.exe -c import szl_eclipse` → 0 (0.11 s); `szl_eclipse.eclipse # reference self-report` → 0 (0.11 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.06 s)
  - **identity**: PARTIAL — description present (295 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=3, static test functions=15, dirs=['tests']; executed: {'passed': 15}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=34.2s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-energy-attest

- https://github.com/szl-holdings/szl-energy-attest · visibility public · archived no · default main · HEAD 217ba7d58bef · pushed 2026-09-24T13:04:10Z · size 202 KB · language Python · stars 0 · forks 0 · watchers 1 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 6 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-dw0yy2kz\env` → 0 (10.69 s); `install --disable-pip-version-check -q .[test]` → 0 (24.84 s); `<tmp>\szl-smoke-dw0yy2kz\env\Scripts\python.exe -c import szl_energy_attest` → 0 (0.33 s); `<tmp>\szl-smoke-dw0yy2kz\env\Scripts\szl-energy-attest.exe --help` → 0 (0.58 s); `-q -p no:cacheprovider --maxfail=50` → 1 (2.58 s)
  - **identity**: PASS — description present (294 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=11, static test functions=112, dirs=['energy_core/tests', 'tests']; executed: {'failed': 1, 'passed': 96, 'skipped': 3}; UNRESOLVED: failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=35.9s
  - **honest_scoping**: PASS — scoping statement: 'does not establish'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 5 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-engine-bench

- https://github.com/szl-holdings/szl-engine-bench · visibility public · archived no · default main · HEAD c5ec41b9c1df · pushed 2026-09-23T13:45:14Z · size 81 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-eyd5xegr\env` → 0 (12.69 s); `install --disable-pip-version-check -q .` → 0 (14.69 s); `-q -p no:cacheprovider --maxfail=50` → 0 (6.55 s)
  - **identity**: PASS — description present (214 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=3, static test functions=52, dirs=['tests']; executed: {'passed': 119}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 2d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=33.9s
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 2d ago; oldest open issue 22d; abandoned branches (>90d) 0

### szl-evidence-litellm

- https://github.com/szl-holdings/szl-evidence-litellm · visibility public · archived no · default main · HEAD 578228481c6e · pushed 2026-09-20T11:42:50Z · size 251 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (131 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=14, static test functions=195, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 5d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=1741 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 5d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-experiments

- https://github.com/szl-holdings/szl-experiments · visibility public · archived yes · default main · HEAD 2d2980ce7f00 · pushed 2026-08-29T16:16:52Z · size 119 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (77 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 27d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-fleet-overlay

- https://github.com/szl-holdings/szl-fleet-overlay · visibility public · archived yes · default main · HEAD 79ec6351daf9 · pushed 2026-08-26T14:25:23Z · size 214 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (149 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 13 workflows; gate workflows latest (grouped by workflow): Bundle Reference Check=success, CI=success, Pin Check=success, Zarf Package Build + Sign=success; newest gate run 30d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0-rc.1; notes=1683 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 30d ago; oldest open issue none open; abandoned branches (>90d) 3

### szl-forge

- https://github.com/szl-holdings/szl-forge · visibility public · archived no · default main · HEAD 5fe4491ecb07 · pushed 2026-09-25T16:54:30Z · size 64231 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 1 · code scanning open 0 · secret scanning open 1 [mistral_ai_api_key] · branch protection not protected (HTTP 404 'Branch not protected') · rulesets deletion, non_fast_forward, pull_request, required_status_checks
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-46k0dm09\env` → 0 (25.16 s); `install --disable-pip-version-check -q .[test]` → 0 (50.66 s); `<tmp>\szl-smoke-46k0dm09\env\Scripts\python.exe -c import frontier_completion` → 1 (0.08 s); `<tmp>\szl-smoke-46k0dm09\env\Scripts\python.exe -c import gmb` → 1 (0.06 s); `<tmp>\szl-smoke-46k0dm09\env\Scripts\python.exe -c import inference` → 0 (0.23 s); `-q -p no:cacheprovider --maxfail=50` → 1 (19.31 s)
  - **identity**: PASS — description present (161 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['agent-forge/requirements.lock', 'clinical-gateway/requirements.lock']; build path=['spaces/szl-model-inference-lab/Dockerfile']
  - **tests**: PARTIAL — test files=219, static test functions=3097, dirs=['agent-forge/tests', 'clinical-gateway/tests', 'model-lab/tests']; executed: {'failed': 50, 'passed': 968, 'skipped': 3}; UNRESOLVED: failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required
  - **ci**: PASS — 69 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: FAIL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=1 ['mistral_ai_api_key']; risky patterns={'tar_extractall_unfiltered': 1, 'yaml_unsafe_load': 2}; traversal-defense seen=True
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=76.2s
  - **honest_scoping**: PASS — scoping statement: 'does not prove'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 9 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 23d; abandoned branches (>90d) 0

### szl-formula-ledger

- https://github.com/szl-holdings/szl-formula-ledger · visibility public · archived yes · default main · HEAD ceaef540eba6 · pushed 2026-07-22T03:31:12Z · size 34 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (82 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; gate workflows latest (grouped by workflow): ledger-check=success; newest gate run 65d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 65d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-formulas

- https://github.com/szl-holdings/szl-formulas · visibility public · archived no · default main · HEAD d0e8110ac815 · pushed 2026-09-25T05:32:36Z · size 91 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (167 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=3, static test functions=26, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 6 workflows; no push/PR-triggered test/build run among the last 10 default-branch runs; failing non-gate workflows: ['Hub joblib quarantine PR']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (1212 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-frontier

- https://github.com/szl-holdings/szl-frontier · visibility public · archived no · default main · HEAD 9f45feaecd6b · pushed 2026-09-25T17:06:42Z · size 1839 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-gal3vex8\env` → 0 (8.88 s); `install --disable-pip-version-check -q .` → 0 (15.2 s); `<tmp>\szl-smoke-gal3vex8\env\Scripts\szl-frontier.exe --help` → 0 (0.36 s)
  - **identity**: PASS — description present (164 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['package-lock.json']; build path=['Dockerfile']
  - **tests**: PARTIAL — test files=157, static test functions=994, dirs=['python/tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 0d ago; failing non-gate workflows: ['Estate outside-seat verifier', 'Hugging Face frontier watch']
  - **release_integrity**: PARTIAL — latest=v0.4.0; notes=415 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=24.4s
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 7 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 18d; abandoned branches (>90d) 0

### szl-gov

- https://github.com/szl-holdings/szl-gov · visibility public · archived no · default main · HEAD 706361d6997b · pushed 2026-09-24T14:53:00Z · size 238 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (98 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=3, static test functions=5, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (3817 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-governed-norm

- https://github.com/szl-holdings/szl-governed-norm · visibility public · archived yes · default main · HEAD c68d06d35058 · pushed 2026-08-08T23:49:00Z · size 104 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (173 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 4 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success; newest gate run 48d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 48d ago; oldest open issue none open; abandoned branches (>90d) 1

### szl-govsign

- https://github.com/szl-holdings/szl-govsign · visibility public · archived no · default main · HEAD 1eba876accde · pushed 2026-09-23T19:41:12Z · size 54 KB · language Python · stars 0 · forks 0 · watchers 1 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-a83n1hmy\env` → 0 (11.58 s); `install --disable-pip-version-check -q .` → 0 (14.97 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.23 s)
  - **identity**: PARTIAL — description present (154 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=3, static test functions=6, dirs=['tests']; executed: {'passed': 11}
  - **ci**: PARTIAL — 3 workflows; no push/PR-triggered test/build run among the last 8 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (899 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 2 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/govsign-live']
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-gpu-bridge

- https://github.com/szl-holdings/szl-gpu-bridge · visibility public · archived no · default main · HEAD 71d86099536d · pushed 2026-09-14T16:05:58Z · size 695 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (127 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=34, static test functions=275, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 10 workflows; no push/PR-triggered test/build run among the last 60 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (22904 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'limitations'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 11d ago; oldest open issue 58d; abandoned branches (>90d) 0

### szl-guardrail-receipt

- https://github.com/szl-holdings/szl-guardrail-receipt · visibility public · archived no · default main · HEAD de97625516f2 · pushed 2026-09-25T15:53:13Z · size 54 KB · language Python · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-ievmch19\env` → 0 (12.55 s); `install --disable-pip-version-check -q .[dev]` → 0 (20.42 s); `<tmp>\szl-smoke-ievmch19\env\Scripts\python.exe -c import szl_guardrail_receipt` → 0 (0.52 s); `<tmp>\szl-smoke-ievmch19\env\Scripts\szl-guardrail-receipt.exe --help` → 2 (0.26 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.75 s)
  - **identity**: PARTIAL — description present (254 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=4, static test functions=30, dirs=['tests']; executed: {'passed': 24}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=33.5s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 4 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/guardrail-receipt']
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-holdings.github.io

- https://github.com/szl-holdings/szl-holdings.github.io · visibility public · archived no · default main · HEAD f716a58d1075 · pushed 2026-09-05T16:08:37Z · size 1115 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (77 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=2, static test functions=16, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 12 workflows; gate workflows latest (grouped by workflow): Link & Asset Check=success; newest gate run 20d ago; failing non-gate workflows: ['.github/workflows/apply-root-relative-link-fix.yml']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (2912 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 20d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-invariants

- https://github.com/szl-holdings/szl-invariants · visibility public · archived no · default main · HEAD a88731a0b937 · pushed 2026-09-13T00:01:40Z · size 110 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-rrzhjq5y\env` → 0 (10.81 s); `install --disable-pip-version-check -q .[dev]` → 0 (13.64 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.44 s)
  - **identity**: PARTIAL — description present (155 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=9, static test functions=43, dirs=['tests']; executed: {'passed': 63, 'skipped': 2}
  - **ci**: PASS — 6 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 13d ago; failing non-gate workflows: ['Hub joblib quarantine PR']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (3064 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 4 links checked; broken=[]
  - **maintenance**: PASS — last push 13d ago; oldest open issue 2d; abandoned branches (>90d) 0

### szl-kernels

- https://github.com/szl-holdings/szl-kernels · visibility public · archived no · default main · HEAD 02c33cb37405 · pushed 2026-09-25T16:19:23Z · size 995 KB · language TeX · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (83 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 2, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=20, static test functions=140, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 7 workflows; gate workflows latest (grouped by workflow): Verify SZL kernels (non-promotional dry run)=success, base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: FAIL — 31 links checked; broken=['https://doi.org/10.5281/zenodo.19944926}', 'https://huggingface.co/spaces/SZLHOLDINGS/README/resolve/main/assets/estate-banner-v2.svg', 'https://huggingface.co/spaces/SZLHOLDINGS/holographic']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 23d; abandoned branches (>90d) 0

### szl-kernels-live

- https://github.com/szl-holdings/szl-kernels-live · visibility public · archived yes · default main · HEAD 6c48224a8e8a · pushed 2026-08-18T00:24:31Z · size 474 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows
  - **identity**: PARTIAL — description present (83 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 2 workflows; no push/PR-triggered test/build run among the last 46 default-branch runs; failing non-gate workflows: ['hf-space-deploy', 'kernel-contracts']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 39d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-khipu

- https://github.com/szl-holdings/szl-khipu · visibility public · archived no · default main · HEAD aa585fb4711b · pushed 2026-09-25T16:12:54Z · size 616 KB · language Python · stars 1 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-1o7so2_4\env` → 0 (10.64 s); `install --disable-pip-version-check -q .[test]` → 0 (73.22 s); `<tmp>\szl-smoke-1o7so2_4\env\Scripts\python.exe -c import szl_khipu` → 0 (3.16 s); `<tmp>\szl-smoke-1o7so2_4\env\Scripts\szl-khipu.exe --help` → 1 (0.38 s); `-q -p no:cacheprovider --maxfail=50` → 0 (5.14 s)
  - **identity**: PASS — description present (137 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=24, static test functions=198, dirs=['tests']; executed: {}
  - **ci**: PASS — 16 workflows; gate workflows latest (grouped by workflow): Pin Check=success, base-python-ci=success, ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: PASS — latest=v0.1.0; notes=764 chars; assets=5 hashed=5; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=87.0s
  - **honest_scoping**: PASS — scoping statement: 'What it is NOT'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: FAIL — 9 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/anatomy']
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### szl-lake

- https://github.com/szl-holdings/szl-lake · visibility public · archived no · default main · HEAD e23171e10bac · pushed 2026-09-25T12:56:20Z · size 3533 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata CC-BY-4.0 · bus factor 1
- Dependabot open 0 · code scanning open 14 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
  - **identity**: PARTIAL — description present (188 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (CC-BY-4.0); metadata CC-BY-4.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=6, static test functions=76, dirs=[]; execution NOT_TESTED in this run
  - **ci**: PASS — 25 workflows; gate workflows latest (grouped by workflow): Pin Check=success, Verify Anchor Receipts (real cosign)=success, Verify Anchor Receipts (self-test)=success, base-python-ci=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=True
  - **docs**: FAIL — README (10597 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 13 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-lambda-gate

- https://github.com/szl-holdings/szl-lambda-gate · visibility public · archived no · default main · HEAD 79460594aa3a · pushed 2026-09-25T16:52:35Z · size 194 KB · language Python · stars 0 · forks 0 · watchers 1 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 7 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
  - **identity**: PASS — description present (274 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=5, static test functions=84, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 10 workflows; gate workflows latest (grouped by workflow): Pin Check=success, ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: PASS — latest=v0.1.0; notes=5369 chars; assets=2 hashed=2; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=True, install command=False
  - **honest_scoping**: PASS — scoping statement: 'NOT a proof'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 8 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-maskmod

- https://github.com/szl-holdings/szl-maskmod · visibility public · archived no · default main · HEAD 21f5c9a430e1 · pushed 2026-09-25T16:47:11Z · size 52 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-z_uotl57\env` → 0 (20.05 s); `install --disable-pip-version-check -q .` → 0 (25.58 s); `-q -p no:cacheprovider --maxfail=50` → 1 (0.09 s)
  - **identity**: PARTIAL — description present (140 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=7, static test functions=33, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 3 workflows; no push/PR-triggered test/build run among the last 12 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (555 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-mesh

- https://github.com/szl-holdings/szl-mesh · visibility public · archived no · default main · HEAD 4f72f452fe84 · pushed 2026-09-24T13:21:50Z · size 346 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 15 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-_38blkd5\env` → 0 (12.73 s); `install --disable-pip-version-check -q .` → 0 (15.05 s); `<tmp>\szl-smoke-_38blkd5\env\Scripts\python.exe -c import szl_mesh` → 0 (0.53 s); `<tmp>\szl-smoke-_38blkd5\env\Scripts\python.exe -c import lab` → 1 (0.05 s); `<tmp>\szl-smoke-_38blkd5\env\Scripts\python.exe -c import mesh_command` → 1 (0.06 s); `<tmp>\szl-smoke-_38blkd5\env\Scripts\szl-mesh-demo.exe --help` → 1 (0.28 s); `-q -p no:cacheprovider --maxfail=50` → 2 (1.24 s)
  - **identity**: PASS — description present (101 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: FAIL — test files=9, static test functions=58, dirs=['lab/tests', 'spec', 'tests']; executed: {'error': 3, 'skipped': 1}; attribution REPO_DEFECT: repo: tests import undeclared module 'fastapi'
  - **ci**: PASS — 14 workflows; gate workflows latest (grouped by workflow): CI=success, Mesh Convergence Lab CI=success, Pin Check=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0-rc.1; notes=1417 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=28.3s
  - **honest_scoping**: PASS — scoping statement: 'not a proof'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 15 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 1

### szl-nemo

- https://github.com/szl-holdings/szl-nemo · visibility public · archived no · default main · HEAD f7cce8e41594 · pushed 2026-09-25T10:49:45Z · size 118 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-5a7mo14n\env` → 0 (11.31 s); `install --disable-pip-version-check -q .[test]` → 0 (22.3 s); `<tmp>\szl-smoke-5a7mo14n\env\Scripts\python.exe -c import szl_nemo` → 0 (0.14 s); `<tmp>\szl-smoke-5a7mo14n\env\Scripts\szl-nemo.exe --help` → 0 (0.22 s); `-q -p no:cacheprovider --maxfail=50` → 0 (2.94 s)
  - **identity**: PASS — description present (128 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=11, static test functions=85, dirs=['tests']; executed: {'passed': 85}
  - **ci**: PARTIAL — 2 workflows; no push/PR-triggered test/build run among the last 17 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=33.8s
  - **honest_scoping**: PASS — scoping statement: 'limitations'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-organ-integrity

- https://github.com/szl-holdings/szl-organ-integrity · visibility public · archived yes · default main · HEAD 029403510ae6 · pushed 2026-08-29T03:11:59Z · size 21 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (77 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: FAIL — 2 workflows; gate workflows latest (grouped by workflow): ci=failure; newest gate run 27d ago; failing non-gate workflows: ['pages']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-otel-mesh

- https://github.com/szl-holdings/szl-otel-mesh · visibility public · archived yes · default main · HEAD 172f52ecfc2c · pushed 2026-07-17T15:11:02Z · size 441 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks yes) · rulesets deletion, non_fast_forward, required_linear_history, pull_request
  - **identity**: PARTIAL — description present (143 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 13 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success, Tests=success; newest gate run 70d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v1.0.0; notes=9859 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 70d ago; oldest open issue none open; abandoned branches (>90d) 1

### szl-ouroboros

- https://github.com/szl-holdings/szl-ouroboros · visibility public · archived no · default main · HEAD 417beb1a159c · pushed 2026-09-25T16:47:06Z · size 176 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-ggu7z_nx\env` → 0 (8.95 s); `install --disable-pip-version-check -q .` → 0 (10.2 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.91 s)
  - **identity**: PARTIAL — description present (149 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=7, static test functions=55, dirs=['tests']; executed: {'passed': 40}
  - **ci**: PASS — 7 workflows; gate workflows latest (grouped by workflow): base-python-ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (5644 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 8 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-papers

- https://github.com/szl-holdings/szl-papers · visibility public · archived no · default main · HEAD 2fe78204088a · pushed 2026-09-25T12:36:38Z · size 2931 KB · language TeX · stars 0 · forks 0 · watchers 0 · licence metadata CC-BY-4.0 · bus factor 1
- Dependabot open 0 · code scanning open 4 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (129 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (CC-BY-4.0); metadata CC-BY-4.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: FAIL — no test files found
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): Pin Check=success; newest gate run 0d ago; failing non-gate workflows: ['zenodo-metadata-gate']
  - **release_integrity**: PASS — latest=typesafe-triage-v1.0.0; notes=187 chars; assets=2 hashed=2; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (4533 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 6 links checked; broken=['https://doi.org/10.5281/zenodo.19944926}']
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 1

### szl-pin

- https://github.com/szl-holdings/szl-pin · visibility public · archived no · default main · HEAD 936d8916be65 · pushed 2026-09-25T16:23:28Z · size 23 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (229 chars); maturity stated=False; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### szl-platform

- https://github.com/szl-holdings/szl-platform · visibility public · archived no · default main · HEAD 53c3f3d808db · pushed 2026-09-23T11:06:33Z · size 782 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-1rsh0wwz\env` → 0 (8.26 s); `install --disable-pip-version-check -q .` → 0 (8.92 s)
  - **identity**: PARTIAL — description present (178 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=66, static test functions=772, dirs=['alignment/tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 6 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 2d ago; failing non-gate workflows: ['pages']
  - **release_integrity**: PARTIAL — latest=v14.0.0-gar00; notes=369 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 2d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-provctl

- https://github.com/szl-holdings/szl-provctl · visibility public · archived no · default main · HEAD 7e416471e268 · pushed 2026-09-06T11:16:28Z · size 55 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-69_u8hv9\env` → 0 (8.12 s); `install --disable-pip-version-check -q .` → 0 (9.2 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.77 s)
  - **identity**: PARTIAL — description present (154 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=2, static test functions=3, dirs=['tests']; executed: {'passed': 3}
  - **ci**: PARTIAL — 3 workflows; no push/PR-triggered test/build run among the last 9 default-branch runs; failing non-gate workflows: ['Hub joblib quarantine PR']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (1316 chars) has no quick start or install command
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 3 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/szl-provctl-live']
  - **maintenance**: PASS — last push 19d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-provctl-live

- https://github.com/szl-holdings/szl-provctl-live · visibility public · archived yes · default main · HEAD bf0903cdad0a · pushed 2026-08-18T00:23:15Z · size 228 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets workflows, required_signatures, pull_request, non_fast_forward, required_linear_history, required_status_checks
  - **identity**: PARTIAL — description present (83 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 3 default-branch runs; failing non-gate workflows: ['Governed static Space release']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 39d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-quant

- https://github.com/szl-holdings/szl-quant · visibility public · archived no · default main · HEAD f5fcc4fcc730 · pushed 2026-09-25T15:53:01Z · size 10187 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `install --ignore-scripts --no-audit --no-fund` → 0 (1.61 s); `C:\Program Files\nodejs\npm.CMD test --silent` → 1 (1.48 s)
  - **identity**: PASS — description present (126 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={}
  - **tests**: PARTIAL — test files=12, static test functions=162, dirs=['test']; executed: {}; UNRESOLVED: failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: ['Nemo v3 Exact Engine-Signing Handoff']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=True, install command=False; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: PASS — scoping statement: 'what it does NOT'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 7 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-quant-bench

- https://github.com/szl-holdings/szl-quant-bench · visibility public · archived no · default main · HEAD 9364ee783b05 · pushed 2026-09-23T13:44:56Z · size 30 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-4hpo5tuq\env` → 0 (7.75 s); `install --disable-pip-version-check -q .` → 0 (8.95 s); `<tmp>\szl-smoke-4hpo5tuq\env\Scripts\python.exe -c import szl_quant_bench` → 0 (0.05 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.98 s)
  - **identity**: PARTIAL — description present (224 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=3, static test functions=21, dirs=['tests']; executed: {'passed': 40}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 2d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=16.8s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 2d ago; oldest open issue 22d; abandoned branches (>90d) 0

### szl-quant-witness

- https://github.com/szl-holdings/szl-quant-witness · visibility public · archived no · default main · HEAD df92499a40bd · pushed 2026-09-25T15:53:00Z · size 1114 KB · language JavaScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (194 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=1, static test functions=5, dirs=['test']; execution NOT_TESTED in this run
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (6218 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-real-estate

- https://github.com/szl-holdings/szl-real-estate · visibility public · archived no · default main · HEAD 9c7d37262aa3 · pushed 2026-09-25T15:53:01Z · size 90 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-tlb6asnj\env` → 0 (9.0 s); `install --disable-pip-version-check -q .` → 0 (9.11 s); `<tmp>\szl-smoke-tlb6asnj\env\Scripts\python.exe -c import szl_re` → 0 (0.19 s); `-q -p no:cacheprovider --maxfail=50` → 0 (2.09 s)
  - **identity**: PARTIAL — description present (146 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 0, 'requirements_pinned_eq': 0, 'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=2, static test functions=18, dirs=['tests']; executed: {'passed': 16}
  - **ci**: FAIL — 5 workflows; gate workflows latest (grouped by workflow): Verify canonical Terra publication ownership=success, Verify central Hugging Face publication ownership=failure, ci=success; newest gate run 0d ago; failing non-gate workflows: ['Hugging Face publication pipeline', 'hf-space']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (2531 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 6 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-receipt

- https://github.com/szl-holdings/szl-receipt · visibility public · archived no · default main · HEAD c3ad652f20f2 · pushed 2026-09-24T12:58:46Z · size 183 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 15 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-5uzxp3uv\env` → 0 (10.56 s); `install --disable-pip-version-check -q .[dev]` → 0 (22.81 s); `<tmp>\szl-smoke-5uzxp3uv\env\Scripts\python.exe -c import szl_receipt` → 0 (0.62 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.78 s)
  - **identity**: PARTIAL — description present (147 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 2, 'pyproject_deps_pinned_eq': 2}
  - **tests**: PASS — test files=7, static test functions=71, dirs=['tests']; executed: {'passed': 71}
  - **ci**: PASS — 12 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success, base-python-ci=success; newest gate run 1d ago; failing non-gate workflows: ['scorecard']
  - **release_integrity**: PASS — latest=v0.3.0; notes=2347 chars; assets=8 hashed=8; tag signed=True
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=34.0s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 8 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-receipt-attn

- https://github.com/szl-holdings/szl-receipt-attn · visibility public · archived no · default main · HEAD dd0b8c8f08b2 · pushed 2026-09-06T11:16:25Z · size 72 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-viot81eb\env` → 0 (8.42 s); `install --disable-pip-version-check -q .` → 0 (10.14 s); `-q -p no:cacheprovider --maxfail=50` → 4 (0.58 s)
  - **identity**: PARTIAL — description present (150 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: FAIL — test files=4, static test functions=16, dirs=['tests']; executed: {}; attribution REPO_DEFECT: repo: tests import torch but it is not declared in the installed dependency set
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): base-python-ci=success, cpu-tests=success; newest gate run 19d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 2 links checked; broken=[]
  - **maintenance**: PASS — last push 19d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-retrieval-bench

- https://github.com/szl-holdings/szl-retrieval-bench · visibility public · archived no · default main · HEAD 54f5dd963825 · pushed 2026-09-23T13:46:21Z · size 34 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-121dyhfd\env` → 0 (10.22 s); `install --disable-pip-version-check -q .` → 0 (12.55 s); `<tmp>\szl-smoke-121dyhfd\env\Scripts\python.exe -c import szl_retrieval_bench` → 0 (0.06 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.61 s)
  - **identity**: PARTIAL — description present (170 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=1, static test functions=23, dirs=['tests']; executed: {'passed': 28}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 2d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=22.8s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 2d ago; oldest open issue 22d; abandoned branches (>90d) 0

### szl-router

- https://github.com/szl-holdings/szl-router · visibility public · archived no · default main · HEAD 9b43aafeec61 · pushed 2026-09-25T16:12:58Z · size 476 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 21 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-795lv9ic\env` → 0 (10.3 s); `install --disable-pip-version-check -q .[test]` → 0 (34.09 s); `<tmp>\szl-smoke-795lv9ic\env\Scripts\python.exe -c import router_control` → 1 (0.06 s); `<tmp>\szl-smoke-795lv9ic\env\Scripts\python.exe -c import szl_router` → 0 (0.22 s); `<tmp>\szl-smoke-795lv9ic\env\Scripts\szl-router.exe --help` → TIMEOUT (120.08 s); `<tmp>\szl-smoke-795lv9ic\env\Scripts\szl-router-verify.exe --help` → 0 (0.48 s); `-q -p no:cacheprovider --maxfail=50` → 0 (50.22 s)
  - **identity**: PARTIAL — description present (127 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 2, 'requirements_pinned_eq': 0, 'pyproject_deps': 2, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=27, static test functions=231, dirs=['space/tests', 'tests']; executed: {'passed': 258, 'skipped': 3}
  - **ci**: PASS — 12 workflows; gate workflows latest (grouped by workflow): CI=success, SZL Sovereign Router CI=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=44.7s
  - **honest_scoping**: PASS — scoping statement: 'does not establish'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: FAIL — 9 links checked; broken=['https://github.com/szl-holdings/szl-receipt.git@v0.2.0']
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-runbook-catalog

- https://github.com/szl-holdings/szl-runbook-catalog · visibility public · archived no · default main · HEAD 0377faa91464 · pushed 2026-09-20T11:43:00Z · size 23 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (267 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=1, static test functions=12, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 5 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=True
  - **docs**: FAIL — README (1975 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 5d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-second-brain

- https://github.com/szl-holdings/szl-second-brain · visibility public · archived no · default main · HEAD 25c12301e2fd · pushed 2026-09-24T18:33:30Z · size 775 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-s43q9esj\env` → 0 (11.31 s); `install --disable-pip-version-check -q .[test]` → 0 (42.25 s); `<tmp>\szl-smoke-s43q9esj\env\Scripts\python.exe -c import data` → 0 (0.12 s); `<tmp>\szl-smoke-s43q9esj\env\Scripts\python.exe -c import second_brain` → 0 (0.38 s); `-q -p no:cacheprovider --maxfail=50` → 2 (2.2 s)
  - **identity**: PARTIAL — description present (107 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 3, 'requirements_pinned_eq': 0, 'pyproject_deps': 2, 'pyproject_deps_pinned_eq': 0}
  - **tests**: FAIL — test files=11, static test functions=70, dirs=['tests']; executed: {'error': 4}; attribution REPO_DEFECT: repo: test dependency httpx not declared (starlette TestClient)
  - **ci**: PARTIAL — 9 workflows; no push/PR-triggered test/build run among the last 60 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (7315 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 1d ago; oldest open issue 20d; abandoned branches (>90d) 0

### szl-seismic-review

- https://github.com/szl-holdings/szl-seismic-review · visibility public · archived no · default main · HEAD 8eb74d5319bb · pushed 2026-09-25T12:39:28Z · size 49 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-xvqhd3td\env` → 0 (9.78 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (15.81 s); `-q -p no:cacheprovider --maxfail=50` → 2 (1.81 s)
  - **identity**: PASS — description present (116 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 2, 'requirements_pinned_eq': 2}; no reproducible build definition
  - **tests**: FAIL — test files=1, static test functions=2, dirs=['tests']; executed: {'error': 2}; attribution REPO_DEFECT: repo: test dependency httpx not declared (starlette TestClient)
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: PASS — scoping statement: 'limitations'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 3 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-serve

- https://github.com/szl-holdings/szl-serve · visibility public · archived no · default main · HEAD 201a7b3dd450 · pushed 2026-09-21T23:09:44Z · size 69 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-t_4p7iem\env` → 0 (10.83 s); `install --disable-pip-version-check -q .[test]` → 0 (27.36 s); `<tmp>\szl-smoke-t_4p7iem\env\Scripts\python.exe -c import szl_serve` → 0 (0.66 s); `<tmp>\szl-smoke-t_4p7iem\env\Scripts\szl-serve.exe --help` → 0 (0.42 s); `-q -p no:cacheprovider --maxfail=50` → 1 (1.34 s)
  - **identity**: PASS — description present (224 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PARTIAL — test files=7, static test functions=50, dirs=['tests']; executed: {}; UNRESOLVED: failure recorded under the interim harness (byte/hash comparison on a core.autocrlf=true clone); re-run under harness fix2 required
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): CI=success; newest gate run 4d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=38.8s
  - **honest_scoping**: PASS — scoping statement: 'What this is NOT'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: FAIL — 6 links checked; broken=['https://huggingface.co/spaces/SZLHOLDINGS/szl-forge-lab']
  - **maintenance**: PASS — last push 4d ago; oldest open issue 11d; abandoned branches (>90d) 0

### szl-sovereign-os

- https://github.com/szl-holdings/szl-sovereign-os · visibility public · archived no · default main · HEAD 1a8ab240501e · pushed 2026-09-25T15:53:13Z · size 76 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-u_ewtcvk\env` → 0 (11.38 s); `install --disable-pip-version-check -q .` → 0 (11.7 s); `<tmp>\szl-smoke-u_ewtcvk\env\Scripts\python.exe -c import szl_os` → 0 (0.14 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.49 s)
  - **identity**: PASS — description present (178 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'requirements_total': 0, 'requirements_pinned_eq': 0, 'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=1, static test functions=12, dirs=['tests']; executed: {'passed': 11}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: ['Hugging Face publication pipeline', 'hf-space']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=23.2s
  - **honest_scoping**: PASS — scoping statement: 'does not claim'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 6 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-substrate

- https://github.com/szl-holdings/szl-substrate · visibility public · archived no · default main · HEAD 5b4d0d5b8bd0 · pushed 2026-09-22T06:25:24Z · size 2390 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-439jif02\env` → 0 (15.62 s); `install --disable-pip-version-check -q .[dev]` → 0 (49.12 s); `<tmp>\szl-smoke-439jif02\env\Scripts\python.exe -c import szl_substrate` → 0 (0.45 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.66 s)
  - **identity**: PARTIAL — description present (269 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 1, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=13, static test functions=82, dirs=['tests']; executed: {'passed': 206}
  - **ci**: PASS — 9 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success, base-python-ci=success; newest gate run 3d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=65.2s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 8 links checked; broken=[]
  - **maintenance**: PASS — last push 3d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-telemetry

- https://github.com/szl-holdings/szl-telemetry · visibility public · archived yes · default main · HEAD ef519c090c9e · pushed 2026-08-29T06:37:05Z · size 81 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (85 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 47 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 27d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-trust

- https://github.com/szl-holdings/szl-trust · visibility public · archived no · default main · HEAD d1f425393341 · pushed 2026-09-24T13:04:47Z · size 248 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata CC-BY-4.0 · bus factor 1
- Dependabot open 0 · code scanning open 7 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets none
  - **identity**: PASS — description present (137 chars); maturity stated=True; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (CC-BY-4.0); metadata CC-BY-4.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=3, static test functions=24, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PASS — 10 workflows; gate workflows latest (grouped by workflow): Pin Check=success, base-python-ci=success, ci=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=True, install command=False
  - **honest_scoping**: PASS — scoping statement: 'does not establish'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 20 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### szl-typesafe-triage

- https://github.com/szl-holdings/szl-typesafe-triage · visibility public · archived no · default main · HEAD f51c817837b1 · pushed 2026-09-25T17:06:47Z · size 87160 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (275 chars); maturity stated=False; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PASS — 4 workflows; gate workflows latest (grouped by workflow): ci=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PASS — last push 0d ago; oldest open issue 2d; abandoned branches (>90d) 0

### szl-uds-deployment

- https://github.com/szl-holdings/szl-uds-deployment · visibility public · archived yes · default main · HEAD 341b79deda90 · pushed 2026-07-01T22:05:30Z · size 4484 KB · language Shell · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks no) · rulesets required_status_checks, deletion
  - **identity**: PARTIAL — description present (145 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — >=100 (first page only) workflows; gate workflows latest (grouped by workflow): Box Scripts Drift-Check Guard=success, Box Scripts Self-tests=success, DNS Drift Check Guard=success, File Key-Custody Gate — Self-test=success, Lockfile Registry Check=success, Organ Image Presence Guard Self-Test=success, Organ Pin Drift Guard Self-Test=success, Pin Drift Guard Self-Test=success, ; newest gate run 87d ago; failing non-gate workflows: ['Box Fallback Superset Guard']
  - **release_integrity**: PARTIAL — latest=v0.3.2; notes=1069 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 86d ago; oldest open issue none open; abandoned branches (>90d) 14

### szl-vertical-forge

- https://github.com/szl-holdings/szl-vertical-forge · visibility public · archived no · default main · HEAD 16e64cc006b1 · pushed 2026-09-25T16:23:44Z · size 66 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-1md27eb7\env` → 0 (14.24 s); `install --disable-pip-version-check -q .` → 0 (14.11 s); `<tmp>\szl-smoke-1md27eb7\env\Scripts\python.exe -c import szl_vertical_forge` → 0 (0.12 s); `-q -p no:cacheprovider --maxfail=50` → 0 (1.73 s)
  - **identity**: PARTIAL — description present (294 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=1, static test functions=17, dirs=['tests']; executed: {'passed': 17}
  - **ci**: PASS — 3 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=28.5s
  - **honest_scoping**: PASS — scoping statement: 'does not prove'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue 2d; abandoned branches (>90d) 0

### szl-wave1-report

- https://github.com/szl-holdings/szl-wave1-report · visibility public · archived no · default main · HEAD f5370d5536d0 · pushed 2026-09-08T04:11:18Z · size 33 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-nrd273n3\env` → 0 (15.11 s); `install --disable-pip-version-check -q .` → 0 (13.11 s); `<tmp>\szl-smoke-nrd273n3\env\Scripts\python.exe -c import szl_wave1_report` → 0 (0.28 s); `-m pytest tests/ -q` → 1 (0.11 s); `--format bundle --output wave.zip` → 2 (0.33 s); `-q -p no:cacheprovider --maxfail=50` → 0 (0.77 s)
  - **identity**: PARTIAL — description present (177 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: PASS — test files=2, static test functions=32, dirs=['tests']; executed: {'passed': 41}
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): tests=success; newest gate run 17d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=28.5s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity', 'performance']
  - **cross_links**: PASS — 4 links checked; broken=[]
  - **maintenance**: PASS — last push 17d ago; oldest open issue 22d; abandoned branches (>90d) 0

### the-grid

- https://github.com/szl-holdings/the-grid · visibility public · archived no · default main · HEAD 55cb078ab4cf · pushed 2026-09-25T15:53:12Z · size 32 KB · language HTML · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
  - **identity**: PARTIAL — description present (180 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=1, static test functions=5, dirs=['tests']; execution NOT_TESTED in this run
  - **ci**: PARTIAL — 1 workflows; no push/PR-triggered test/build run among the last 1 default-branch runs; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PARTIAL — no source/HF/product/proof links in README
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### uds-bundles

- https://github.com/szl-holdings/uds-bundles · visibility public · archived no · default main · HEAD fe6dee2fac7e · pushed 2026-09-25T16:25:22Z · size 755 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 14 · secret scanning open 0 · branch protection enabled (required reviews UNAVAILABLE, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (186 chars); maturity stated=True; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: NOT_TESTED — no package manifest (not a buildable package)
  - **tests**: PARTIAL — test files=7, static test functions=125, dirs=['mesh/tests', 'observatory/tests', 'test']; execution NOT_TESTED in this run
  - **ci**: PASS — 25 workflows; gate workflows latest (grouped by workflow): Pin Check=success, Zarf Package Build + Sign (Keyless)=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: PASS — latest=v0.2.0; notes=2062 chars; assets=1 hashed=1; tag signed=False
  - **security_posture**: PARTIAL — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns={'yaml_unsafe_load': 1}; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=True, install command=False
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: FAIL — 11 links checked; broken=['https://github.com/szl-holdings/uds-mesh']
  - **maintenance**: PARTIAL — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 18

### vertical-services

- https://github.com/szl-holdings/vertical-services · visibility public · archived no · default main · HEAD ed2b49d985b0 · pushed 2026-09-25T16:22:18Z · size 694 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 0 · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-bovvoim1\env` → 0 (13.77 s); `--disable-pip-version-check -q -r requirements.txt` → 0 (23.08 s); `<tmp>\szl-smoke-bovvoim1\env\Scripts\python.exe -c import frontier_fabric` → 1 (0.08 s); `-q -p no:cacheprovider --maxfail=50` → 2 (4.76 s)
  - **identity**: PARTIAL — description present (280 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PARTIAL — lockfiles=[]; pinning={'requirements_total': 4, 'requirements_pinned_eq': 4}; no reproducible build definition
  - **tests**: PARTIAL — test files=20, static test functions=202, dirs=['frontier/tests', 'tests']; executed: {'error': 4}; UNRESOLVED: failure recorded under the interim harness (no repository cause recognised); re-run under harness fix2 required
  - **ci**: PASS — 19 workflows; gate workflows latest (grouped by workflow): CI=success, Vertical Services — test, publish, probe, and attest=success; newest gate run 0d ago; failing non-gate workflows: ['Uptime Monitor', 'Vertical intelligence live evidence']
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: FAIL — README (6849 chars) has no quick start or install command
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue 21d; abandoned branches (>90d) 0

### vsp-otel

- https://github.com/szl-holdings/vsp-otel · visibility public · archived no · default main · HEAD c85aa0ee2b6f · pushed 2026-09-25T16:09:18Z · size 490 KB · language TypeScript · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 1 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks no) · rulesets deletion, non_fast_forward, required_linear_history, pull_request, required_status_checks
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-6tr0xnez\env` → 0 (12.19 s); `install --disable-pip-version-check -q .[test]` → 0 (56.48 s); `<tmp>\szl-smoke-6tr0xnez\env\Scripts\python.exe -c import vsp_otel` → 0 (0.23 s); `<tmp>\szl-smoke-6tr0xnez\env\Scripts\python.exe -c import collector` → 1 (0.08 s); `-q -p no:cacheprovider --maxfail=50` → 0 (9.95 s)
  - **identity**: PARTIAL — description present (136 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['pnpm-lock.yaml']; build path=['Dockerfile']
  - **tests**: PASS — test files=11, static test functions=116, dirs=['test', 'tests']; executed: {}
  - **ci**: PASS — 14 workflows; gate workflows latest (grouped by workflow): CI=success, Lockfile Registry Check=success, Pin Check=success, Python CI=success, Tests=success; newest gate run 0d ago; failing non-gate workflows: none
  - **release_integrity**: PARTIAL — latest=v0.1.0; notes=91 chars; assets=0 hashed=0; tag signed=False
  - **security_posture**: PASS — SECURITY.md=yes; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=68.9s
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: PARTIAL — boundary categories named: ['performance']
  - **cross_links**: PASS — 12 links checked; broken=[]
  - **maintenance**: PASS — last push 0d ago; oldest open issue none open; abandoned branches (>90d) 1

### warhacker-demo

- https://github.com/szl-holdings/warhacker-demo · visibility public · archived yes · default main · HEAD 0c68abbc41f9 · pushed 2026-07-21T03:28:30Z · size 84 KB · language Shell · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot UNAVAILABLE (HTTP 403) · code scanning UNAVAILABLE (HTTP 403) · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
  - **identity**: PARTIAL — description present (153 chars); maturity stated=True; non-claims stated=False
  - **license**: PARTIAL — metadata license=Apache-2.0; LICENSE file NOT_TESTED (not cloned)
  - **provenance**: NOT_TESTED — not cloned
  - **tests**: NOT_TESTED — not cloned
  - **ci**: PARTIAL — 3 workflows; gate workflows latest (grouped by workflow): CI=success, Pin Check=success; newest gate run 79d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: NOT_TESTED — not cloned
  - **docs**: NOT_TESTED — not cloned
  - **honest_scoping**: NOT_TESTED — not cloned
  - **evidence_boundary**: NOT_TESTED — not cloned
  - **cross_links**: NOT_TESTED — links not resolved
  - **maintenance**: PARTIAL — archived; last push 66d ago; oldest open issue none open; abandoned branches (>90d) 0

### yarqa

- https://github.com/szl-holdings/yarqa · visibility public · archived no · default main · HEAD 99e16ae447d7 · pushed 2026-09-24T13:00:16Z · size 707 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning open 11 · secret scanning open 0 · branch protection enabled (required reviews 0, status checks yes) · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-4p94ubi3\env` → 0 (14.36 s); `install --disable-pip-version-check -q .[test]` → 0 (50.7 s); `<tmp>\szl-smoke-4p94ubi3\env\Scripts\python.exe -c import yarqa` → 0 (2.28 s); `-q -p no:cacheprovider --maxfail=50` → 2 (1.59 s)
  - **identity**: PARTIAL — description present (207 chars); maturity stated=False; non-claims stated=True
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: PASS — lockfiles=['space/requirements.lock']; build path=['space/Dockerfile']
  - **tests**: FAIL — test files=15, static test functions=142, dirs=['space/tests', 'tests']; executed: {'error': 2, 'skipped': 2}; attribution REPO_DEFECT: repo: tests import undeclared module 'fastapi'
  - **ci**: PASS — 17 workflows; gate workflows latest (grouped by workflow): Pin Check=success, Space CI=success; newest gate run 1d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PASS — quick-start section and install command present; measured time-to-first-run=67.3s
  - **honest_scoping**: PASS — scoping statement: 'not a proof'
  - **evidence_boundary**: PARTIAL — boundary categories named: ['integrity']
  - **cross_links**: PASS — 6 links checked; broken=[]
  - **maintenance**: PASS — last push 1d ago; oldest open issue none open; abandoned branches (>90d) 0

### YARQA-ATTN

- https://github.com/szl-holdings/YARQA-ATTN · visibility public · archived no · default main · HEAD bb15b7da92ad · pushed 2026-09-06T11:16:26Z · size 45 KB · language Python · stars 0 · forks 0 · watchers 0 · licence metadata Apache-2.0 · bus factor 1
- Dependabot open 0 · code scanning UNAVAILABLE (HTTP 404) · secret scanning open 0 · branch protection not protected (HTTP 404 'Branch not protected') · rulesets none
- smoke commands: `-3.12 -m venv <tmp>\szl-smoke-yh1r20cx\env` → 0 (9.73 s); `install --disable-pip-version-check -q .` → 0 (9.59 s); `-q -p no:cacheprovider --maxfail=50` → 4 (0.48 s)
  - **identity**: PARTIAL — description present (224 chars); maturity stated=False; non-claims stated=False
  - **license**: PASS — LICENSE LICENSE (Apache-2.0); metadata Apache-2.0
  - **provenance**: FAIL — no lockfile; pinning={'pyproject_deps': 0, 'pyproject_deps_pinned_eq': 0}
  - **tests**: FAIL — test files=6, static test functions=26, dirs=['tests']; executed: {}; attribution REPO_DEFECT: repo: tests import torch but it is not declared in the installed dependency set
  - **ci**: PASS — 2 workflows; gate workflows latest (grouped by workflow): cpu-tests=success; newest gate run 19d ago; failing non-gate workflows: none
  - **release_integrity**: FAIL — no releases published
  - **security_posture**: PARTIAL — SECURITY.md=no; likely-live secret hits=0; open secret-scanning alerts=0; risky patterns=none; traversal-defense seen=False
  - **docs**: PARTIAL — quickstart heading=False, install command=True; measured time-to-first-run=NOT_TESTEDs
  - **honest_scoping**: FAIL — no explicit statement of what is not proven
  - **evidence_boundary**: FAIL — boundary categories named: none
  - **cross_links**: PASS — 1 links checked; broken=[]
  - **maintenance**: PASS — last push 19d ago; oldest open issue none open; abandoned branches (>90d) 0
