# szl-evidence-mandate

<!-- szl:header v1 -->
<!-- Native identity: szl-brand@4309f6fce89179331b0b3ed8c99494e76c5be256; Orbit v2 icon. -->
<p>
  <a href="https://github.com/szl-holdings">
    <img src="https://raw.githubusercontent.com/szl-holdings/szl-brand/4309f6fce89179331b0b3ed8c99494e76c5be256/kit/logos/orbit-v2/suite/szl-icon-32.svg" alt="SZL Holdings — Orbit v2" width="32" height="32" />
  </a>
</p>

**Control before action. Evidence after.**

[Product](https://a-11-oy.com) · [Proof](https://a11oy.net) · [GitHub organization](https://github.com/szl-holdings)
<!-- /szl:header -->

## Scope and data boundary

This repository is not a clinical tool: its evidence engine and audits must
never receive patient data, PHI or clinical records. It audits repositories and
Hugging Face assets of the SZL Holdings estate, and its engine reads the project
files that a manifest declares.

[![PyPI](https://img.shields.io/pypi/v/szl-evidence-mandate)](https://pypi.org/project/szl-evidence-mandate/) [![Python](https://img.shields.io/pypi/pyversions/szl-evidence-mandate)](https://pypi.org/project/szl-evidence-mandate/)

A Scientific Evidence Gate engine plus evidence-backed, read-only audits of the
`szl-holdings` GitHub organisation and the `SZLHOLDINGS` Hugging Face estate.

> A passing check must emit enough evidence to prove it had the opportunity to fail.
> The system producing an answer must not be the sole authority certifying that its own
> verification occurred.

**Maturity:** research prototype (0.1.2 source candidate; the last PyPI release may differ).
**Licence:** Apache-2.0 (org standard; see `LICENSE`).

## OpenIslet numerical evidence workbench (source candidate)

An optional, local Python backend and plain HTML/CSS/JavaScript frontend replay
the **actual pinned OpenIslet peroxide solver function excerpts** against an
independent sine manufactured solution. This is software verification for the
selected synthetic fixture only, **not** biological validation, a clinical tool,
a formal proof, a reported defect, a novel treatment, or an OpenIslet partnership.
The feature is a source candidate; the existing PyPI release does not contain it.

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev,sign,openislet]"
.venv/bin/szl-audit openislet workbench --host 127.0.0.1 --port 8000
# Open http://127.0.0.1:8000, select a synthetic amplitude/kinetics, then Run.
# For an explicitly exposed sandbox preview only, bind --host 0.0.0.0.
```

No authentication, upload, data ingestion, URL proxy, arbitrary code/path,
model call, MCP connection, account, or external submission is present. Do not
use this local research server as an Internet production service. It binds to
loopback by default. Exposing it shares only the fixed research fixture API;
it does not grant access to the estate audit API or local files.

**Flow:** `GET /api/openislet/meta` supplies the fixed contract and attribution;
`POST /api/openislet/replay` accepts only
`{"amplitude_uM":25000,"kinetics":"nonlinear"}`. Amplitudes are restricted to
`1`, `25000`, or `250000` µM, kinetics to `linear` or `nonlinear`.
Unknown keys, strings instead of numbers, booleans, NaN/Infinity, duplicate
keys, cross-origin browser POSTs, ambiguous framing, and bodies over 1024 bytes
are refused. There are no patient records, paper extracts or third-party
database payloads in this feature.

Every replay uses four fixed meshes (16, 32, 64, 128 intervals), plus two
deliberately faulty finest-grid controls. Work is bounded by those meshes and
the upstream solver's 80 Newton iterations; one fresh worker handles a replay
with a 15-second wall limit, and POSIX adds 10 CPU seconds and a 2 GiB address
space limit. Windows uses the wall/work bounds without POSIX resource limits.
The single-request server uses a 5-second socket timeout and does not provide
a production multi-tenant scheduling or denial-of-service guarantee.

The response includes raw-precision errors, ratios and observed orders,
independent continuum reference, mesh profiles, acceptance checks, fault-control
results, provenance, runtime versions, and `biological_validation:false`.
`PASS` means the declared checks held **for that synthetic fixture only**.
`FAIL` means a declared numerical acceptance check failed; HTTP 503 means no
completed result was established. The frontend displays loading and errors,
invalidates results when settings change, and downloads the **exact backend
response text**, not a JavaScript reconstruction of Python floating-point
receipt bytes. Display rounding is never used to decide acceptance.

### Reproduce without the browser

```bash
.venv/bin/szl-audit openislet replay --amplitude-um 25000 --kinetics nonlinear > receipt.json
# Repeat for amplitudes 1 / 25000 / 250000 and linear / nonlinear (six fixtures).
.venv/bin/ruff check src tests --no-cache
.venv/bin/python -m pytest tests/test_openislet.py -q
.venv/bin/python -m pytest -q
```

The full six-fixture test evaluates 24 valid mesh cases and 12 deliberate
fault controls. It does not label the synthetic cases as upstream measured
success. The upstream code already tests discrete mass balance and quadratic
manufactured fields with scalar coefficients; this narrow additional test
uses a sine continuum field, nodewise clearance arrays, and refinement/fault
controls. No numerical defect is asserted.

The receipt uses the existing `szl_evidence.receipts.receipt_hash` and tool
metadata, with an explicit `UNSIGNED` state; it never uses a browser signing
key or auto-signs from ambient secrets. The hash binds canonical Python sorted
JSON content, **not JCS or a signature**. The new endpoint independently refuses
non-finite inputs/outputs without changing legacy canonicalization or percentage
comparison semantics. Verify content binding on the original downloaded file:

```bash
.venv/bin/python -c "import json; from szl_evidence.receipts import receipt_hash; r=json.load(open('receipt.json')); print('CONTENT MATCH' if r['receipt_sha256']==receipt_hash(r) else 'CONTENT MISMATCH')"
```

This is not the legacy engine receipt's invariant-validation contract:
`szl-audit engine verify-receipt` is for engine-run receipts, not this scoped
audit-style replay receipt. A matching hash establishes internal content
consistency only; anyone able to replace all artifacts can recompute it.
It does not independently establish execution, identity, scientific truth,
authenticity, safety, or fitness for use.

### Attribution and source binding

Copyright © 2026 OpenIslet.org Contributors, <https://openislet.org>.
Source: `OpenIslet/openislet@b63a2418ca1253440cce12519183c5775b61f84a`,
`scripts/run_layer4_tissue_and_metabolic_twin.py` (Apache-2.0).
Two functions and the diffusivity declaration in
`src/szl_evidence/openislet/vendor/peroxide.py` are verbatim; all other upstream
code is omitted and the imports are reduced. `vendor/provenance.json` records
the original full-file SHA-256, Git blob hash, and function source hashes;
the function digests and independent diffusivity are checked before each run.
`vendor/NOTICE.txt` records modifications and attribution. The original file
hash is a provenance anchor, not a claim that the full file is bundled.
The analytical oracle and interface are SZL additions; its source digest
is included separately in each receipt.

Upstream's actual root `LICENSE` assigns `scripts/**` to Apache-2.0; its
documentation/data use CC-BY-4.0 with third-party carve-outs. No upstream
documentation/data or biomedical excerpts are redistributed here.
No upstream service or model is impersonated: the UI explicitly identifies
the local pinned code excerpts and all manufactured inputs.

Source-only changes do not publish to PyPI, Hugging Face, OpenIslet, a proof
site, or production. CI runs on pushes/PRs; release publishing remains the
existing explicit `release: published` gate. No version bump, credentials,
remote writes or deployment workflow were added.

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

### Optional signed engine receipts

Install the `sign` extra to make Ed25519 signing available, then configure
`SZL_RECEIPT_ED25519_KEY` with the path to a protected, unencrypted Ed25519 PEM private key.
Do not put the key or its contents in a repository or receipt. For an engine run that must
produce a signature, use `szl-audit engine verify fixtures/valid --require-signed`.
An absent dependency, key, or usable Ed25519 signature retains an `UNSIGNED` receipt and
returns CLI exit code 3 with `signature_requirement: BLOCKED_UNSIGNED`, even if the engine
checks themselves passed. The receipt keeps the engine result so the signing failure cannot
erase a scientific finding. Without the flag, signing remains optional and honest `UNSIGNED`
receipts keep their existing exit codes. A successful local signature is self-checked before
the receipt is written, but a recipient must independently verify it against a trusted public
key; `engine verify-receipt` currently checks content/ledger integrity, **not** signer identity.

## Evidence boundary

- **Integrity:** receipts bind content by SHA-256 and chain invocations. Receipts are
  `UNSIGNED` unless a usable Ed25519 key and signing dependency are configured; no signature
  is ever fabricated. `SIGNED` identifies local signing, not independent signer trust.
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

Estate on Hugging Face: models, datasets and Spaces are published under the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS) org.
