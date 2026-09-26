# 00 — Executive summary

```text
STATUS: FAIL
WHAT WAS EXPECTED: engine verification + full GitHub and HF audits + reconciliation + zoom-out
WHAT WAS EXAMINED: 118 repos, 107 HF artifacts, 707 claims
WHAT ACTUALLY RAN: all stages (see receipts/); CRITICAL/HIGH findings adversarially verified by two independent reviewers each
WHAT PASSED: 19 engine fixtures; 57 repos smoke-tested; 168 claims VERIFIED
WHAT FAILED: 0 CRITICAL, 4 HIGH, 129 MEDIUM findings
WHAT ABSTAINED: 61 repos and 41 HF artifacts not functionally tested (reasons in 02/03)
WHAT REMAINS UNRESOLVED: engine blind spots P02, P03; 5 UNRESOLVED test outcomes (interim harness); 71 STALE claims
WHAT THIS RESULT DOES NOT PROVE: product quality, security, scientific validity, or business value
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

| item | measured |
|---|---|
| Engine fixtures matching declared outcome | 19/19 |
| Mutation blind spots (published) | P02, P03 |
| GitHub repos discovered / cloned / smoke-tested | 118 / 87 / 57 |
| HF artifacts discovered / functionally tested | 107 / 83 |
| Claims VERIFIED / STALE / CONTRADICTED / UNVERIFIABLE | 168 / 71 / 24 / 444 |
| Findings by severity | HIGH 4, MEDIUM 129, LOW 36 |

## Critical and high findings
- [HIGH] killinchu: Documented install `pip install -r requirements.txt` fails: internal dependency vsp-otel is not on PyPI
- [HIGH] SZLHOLDINGS/lean-theorem-tree: Dataset fails to load via the Hub datasets server
- [HIGH] SZLHOLDINGS/szl-1-doctrine-sft: Dataset fails to load via the Hub datasets server
- [HIGH] SZLHOLDINGS/governed-receipts-bench: Bench labels as valid/PASS a fixture the current spec designates a negative example (verifier HEAD 2c82320a rejects 1/7; card-pinned 007106bc passes 7/7)

## Fix first (highest-ranked finding per category)
1. F-0079 SZLHOLDINGS/lean-theorem-tree: Dataset fails to load via the Hub datasets server
2. F-0010 killinchu: Documented install `pip install -r requirements.txt` fails: internal dependency vsp-otel is not on PyPI
3. F-0096 SZLHOLDINGS/governed-receipts-bench: Bench labels as valid/PASS a fixture the current spec designates a negative example (verifier HEAD 2c82320a rejects 1/7; card-pinned 007106bc passes 7/7)
4. F-0156 .github: README links a Hugging Face target that does not exist
5. F-0127 15 documents: Dated lean count '14 axioms' has drifted (STALE, not false)
