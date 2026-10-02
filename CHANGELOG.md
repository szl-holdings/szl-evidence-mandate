# Changelog

## 0.1.2 — source candidate

- Add the optional `sign` dependency extra and test it in CI.
- Emit schema-conformant `SIGNED` Ed25519 receipts when a usable key is configured;
  self-check the signature before writing and retain `UNSIGNED` on failure.
- Add `engine verify --require-signed` so an unsigned result exits 3 while keeping
  the engine receipt and its scientific result for audit. This is a local signing
  requirement; independent signer trust still requires a trusted public key.
- Align the receipt tool version with package metadata.

## 0.1.0 — 2026-09-25

- Evidence Gate engine: manifest, discovery with accounting closure, 18 versioned checks,
  hash-chained invocation ledger, 16 ledger/receipt invariants, canonical receipts
  (UNSIGNED unless a real ed25519 key is configured), dependency-aware validity with
  impact and revalidation, controlled-local packaging.
- 19 generated fixtures with declared status/exit/evidence.
- Mutation harness: 19 mandated mutations + 4 blind-spot probes.
- Read-only audits: GitHub org, Hugging Face org (with conformance-corpus replay),
  reconciliation, zoom-out, 12 reports with mandatory header and coverage blocks.
- Reviewer roster support (`authorized_reviewers`) added after mutation probe P01 exposed
  unauthorised-reviewer substitution as a blind spot.

### Audit-harness defects found and fixed during the first audit run (interim results discarded)

- pip resolved its cache directory relative to the repository under the stripped
  environment, creating an untracked `pip/` directory that broke setuptools flat-layout
  discovery. Fixed by pinning `PIP_CACHE_DIR`; every interim smoke result was discarded and
  re-run.
- The audit host ran out of disk; "No space left on device" and install timeouts are now
  classified as audit-host `NOT_TESTED`, never as repository failures. A free-disk
  pre-flight and heavy-ML-dependency budget were added; clones are reused when the local
  HEAD equals the API HEAD SHA, and smoke runs `git clean` their clone afterwards.
- Claim extraction: DOI regex swallowed badge `.svg` suffixes (false CONTRADICTED);
  numbers captured trailing commas; Lean-count claims now require Lean context and treat
  scope-qualified statements as UNVERIFIABLE; inventory claims are compared with both the
  public and the authenticated totals.
- Model classification is by weight format, not size (a 25 MB LoRA adapter is trained
  weights); every `.gguf` file is header-checked individually.
- CI axis grades push/PR-triggered test/build workflows; failing scheduled monitors are
  reported separately.
- A rate-limited (UNAVAILABLE) listing no longer overwrites previously observed state.
- `--stream` mode: clone, analyse, smoke-test and delete one repository at a time; every
  downstream input (receipt schema ids, verifier implementations, secret grep gates) is
  persisted by the analysis stage so later stages never depend on ephemeral clones.
- Per-repository free-disk guard before cloning; `rmtree_force` clears read-only git packs
  on Windows.
- Prior smoke evidence is admitted only under the mechanical rules in `audit/admission.py`.
