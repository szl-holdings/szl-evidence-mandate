# Changelog

## Unreleased (on `main`, not in a PyPI release)

- Secret-scanning alerts are requested with `hide_secret=true`, and the HTTP cache drops JSON
  `secret` members before writing `raw/` (a leaked credential was previously cached verbatim).
- `github --clone` (including `--stream`) without `--allow-effects` is refused before any API
  collection instead of at the first clone.
- CI installs from a hash-locked closure (`requirements/ci/test.txt`) and also tests Python 3.13;
  new `test` extra for the full suite.
- OpenIslet numerical evidence workbench (`szl-audit openislet workbench|replay`, `openislet`
  extra): pinned upstream solver excerpts against a synthetic manufactured solution (#23).
- Audit fixes: guarded `git clean` contained to its registered clone (#22); `lean_facts` gated
  behind explicit effects (#21); malformed pagination evidence rejected (#20); duplicate manifest
  inputs that resolve to one path rejected (#19); malformed Crossref responses abstain (#18).
- The publish workflow adds a CycloneDX SBOM artifact (#17).

## 0.1.2 — 2026-10-30

- Add the optional `sign` dependency extra and test it in CI.
- Emit schema-conformant `SIGNED` Ed25519 receipts when a usable key is configured;
  self-check the signature before writing and retain `UNSIGNED` on failure.
- Add `engine verify --require-signed` so an unsigned result exits 3 while keeping
  the engine receipt and its scientific result for audit. This is a local signing
  requirement; independent signer trust still requires a trusted public key.
- Align the receipt tool version with package metadata.
- Effectful audit steps (clone, install, import, test, `git clean`) fail closed unless
  `--allow-effects` is passed (#13).
- Final reports and CLI output are redacted safely, and the secret scanner and `redact()` share
  one set of credential patterns (#8, #9).
- Installed-wheel release checks no longer import the source checkout (#16).

## 0.1.1 — 2026-10-01

- Release through the canonical PyPI Trusted Publishing path (`publish-pypi.yml` and the
  release gate) (#2, #3, #4); Python classifiers and PyPI badges added.

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
