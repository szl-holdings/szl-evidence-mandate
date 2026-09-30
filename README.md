# szl-evidence-mandate

A Scientific Evidence Gate engine plus evidence-backed, read-only audits of the
`szl-holdings` GitHub organisation and the `SZLHOLDINGS` Hugging Face estate.

> A passing check must emit enough evidence to prove it had the opportunity to fail.
> The system producing an answer must not be the sole authority certifying that its own
> verification occurred.

**Maturity:** research prototype (v0.1.0). **Licence:** Apache-2.0 (org standard; see `LICENSE`).

## What it does

| Component | What it verifies |
|---|---|
| `szl_evidence` engine | Manifest-declared inputs are present, opened and fully examined; every required check ran (hash-chained invocation ledger); claims are registered, replayable and numerically correct; dependency staleness blocks publication; receipts are canonical and content-bound. Exit codes: PASS 0, FAIL 1, ABSTAIN 2, ERROR 3. |
| Mutation harness | 19 mandated mutations + 4 blind-spot probes; undetected mutations are reported as `BLIND_SPOT`, never hidden. |
| `audit.github` | Every repo (all pages), shallow clones, file-class presence, licence consistency, secret scan (locations only), risky-code patterns, CI/release/protection state, clean-venv install/import/--help/tests, 12-axis scorecard. |
| `audit.huggingface` | Every model/dataset/Space, card scorecard, Space runtime + read-only probes, weight-header checks by HTTP range, small-array loads without pickle, dataset slices, conformance-corpus replay against the paired verifier. |
| `reconcile` / `zoomout` | Cross-surface links, orphans, version drift, schema skew, recomputed inventories vs every stated count; band-aid detection with root cause and structural fix. |

## Quick start (under ten minutes)

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"          # Windows: .venv\Scripts\pip
szl-audit engine verify fixtures/valid      # exit 0
szl-audit engine verify fixtures/empty-input  # exit 2 (ABSTAIN: nothing examined)
szl-audit engine mutate fixtures/valid      # prints BLIND_SPOTS
python -m pytest -q
```

Full audit (read-only; uses `GITHUB_TOKEN`/`gh auth token` and `HF_TOKEN`/HF cache token if present, never printed):

```bash
szl-audit engine report --output reports
szl-audit github --org szl-holdings --clone --stream --deep --output reports   # --stream: one repo on disk at a time
szl-audit hf --org SZLHOLDINGS --functional --output reports
szl-audit reconcile --output reports
szl-audit zoomout --output reports      # also renders reports/00..11
```

Every command writes a receipt under `reports/receipts/` and supports `--dry-run`.

## Evidence boundary

- **Integrity:** receipts bind content by SHA-256 and chain invocations. Receipts are
  `UNSIGNED` unless a real key is configured; no signature is ever fabricated.
- **Performance:** not measured by this tool beyond wall-clock durations of smoke tests.
- **Validity:** not established. A receipt supports integrity, provenance, and
  replayability. It does not establish scientific truth, accuracy, safety, or fitness for use.

## What this does not prove

- That audited repositories or models are correct, secure, or fit for any purpose.
- That the engine catches defect classes outside its mutation set (see published blind spots).
- That a claim marked `UNVERIFIABLE` is false, or that a `STALE` claim was ever wrong.
- That install failures observed on the (Windows) audit host reproduce on Linux.

## Layout

`src/szl_evidence/` engine and audits · `fixtures/` 19 generated fixtures (regenerate
with `szl_evidence.fixturegen.build_all`) · `schemas/` receipt and manifest JSON Schemas ·
`tests/` · `reports/` generated output · `examples/`.
