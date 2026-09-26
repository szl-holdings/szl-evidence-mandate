# Examples

- `fixtures/valid/manifest.yaml` is the reference manifest exercising every check.
- Verify it and inspect the PASS evidence block generated from the ledger:

```bash
szl-audit engine verify fixtures/valid
szl-audit engine impact design --manifest fixtures/valid
szl-audit engine revalidate admitted-evidence --manifest fixtures/stale-dependency --output-sha <sha256-of-new-output>
szl-audit engine package fixtures/valid --output /tmp/valid-package
szl-audit engine verify-receipt reports/receipts/<receipt>.json
```
