# 01 — Engine verification

```text
STATUS: PASS_WITH_BLIND_SPOTS
WHAT WAS EXPECTED: 19 fixtures with declared status/exit/evidence; 23 mutations that must be detected and 1 that must be ignored
WHAT WAS EXAMINED: 19 fixture corpora; 23 mutated corpora/receipts + 1 engine-configuration mutation
WHAT ACTUALLY RAN: engine verify on every fixture; mutation harness; dependency impact + 2 revalidations; 3 hash-seed runs
WHAT PASSED: 19/19 fixtures matched (including 6 whose correct outcome is ABSTAIN); 20/23 required detections; 1 neutral mutation(s) correctly ignored; receipts byte-identical across hash seeds
WHAT FAILED: 0 fixture mismatches; missed detections: P02, P03; false positives: none
WHAT ABSTAINED: fixtures with ABSTAIN verdict (as declared): empty-input, missing-table, partial-execution, narrated-verification, stale-dependency, unresolved; mutations with ABSTAIN verdict: M01, M02, M14, M18
WHAT REMAINS UNRESOLVED: blind spots P02, P03; partial detections none
WHAT THIS RESULT DOES NOT PROVE: that the engine detects defect classes outside the mutation set; that any receipt is authentic (receipts are UNSIGNED)
```

## Fixtures

| fixture | expected | observed | exit exp/obs | evidence ok | primary reason | failure taxonomy | claim not established |
|---|---|---|---|---|---|---|---|
| valid | PASS | PASS | 0/0 | yes | VERIFIED | none | none; all declared claims verified against stored outputs and replayed recipes |
| empty-input | ABSTAIN | ABSTAIN | 2/2 | yes | INSUFFICIENT_EVIDENCE | VACUOUS_PASS | any claim about the corpus |
| missing-table | ABSTAIN | ABSTAIN | 2/2 | yes | INSUFFICIENT_EVIDENCE | none | that every record was reviewed |
| partial-execution | ABSTAIN | ABSTAIN | 2/2 | yes | INSUFFICIENT_EVIDENCE | PARTIAL_EXECUTION | any population-level result |
| narrated-verification | ABSTAIN | ABSTAIN | 2/2 | yes | UNVERIFIED | NARRATED_VERIFICATION | that citation_resolution and human_review ran |
| duplicate-row | FAIL | FAIL | 1/1 | yes | UNVERIFIED | SOURCE_MISMATCH | the stated participant total |
| deleted-row | FAIL | FAIL | 1/1 | yes | SOURCE_MISMATCH | SOURCE_MISMATCH | that the analysed set equals the accepted snapshot |
| unregistered-claim | FAIL | FAIL | 1/1 | yes | UNVERIFIED | EPHEMERAL_CLAIM | C4 (median follow-up) |
| numeric-rounding | FAIL | FAIL | 1/1 | yes | UNVERIFIED | DEFECTIVE_VERIFICATION | C3 (arms equal) |
| comma-tokenization | FAIL | FAIL | 1/1 | yes | UNVERIFIED | none | C1 (participant total) |
| nondeterministic-order | FAIL | FAIL | 1/1 | yes | PROTOCOL_BROKEN | none | that the output is reproducible byte-for-byte |
| timezone-mismatch | FAIL | FAIL | 1/1 | yes | SOURCE_MISMATCH | SOURCE_MISMATCH | that R2 matches its source retrieval |
| wrong-authors | FAIL | FAIL | 1/1 | yes | SOURCE_MISMATCH | SOURCE_MISMATCH | citation K1 attribution |
| nonexistent-doi | FAIL | FAIL | 1/1 | yes | UNVERIFIED | none | citation K2 exists |
| missing-reviewer | FAIL | FAIL | 1/1 | yes | PROTOCOL_BROKEN | PROTOCOL_DRIFT | dual review of R4 |
| protocol-drift | FAIL | FAIL | 1/1 | yes | PROTOCOL_BROKEN | PROTOCOL_DRIFT | that the declared protocol was followed |
| omitted-population | FAIL | FAIL | 1/1 | yes | UNVERIFIED | OMITTED_POPULATION | complete screening |
| stale-dependency | ABSTAIN | ABSTAIN | 2/2 | yes | INSUFFICIENT_EVIDENCE | none | the current conclusion (pending revalidation, not false) |
| unresolved | ABSTAIN | ABSTAIN | 2/2 | yes | REQUIRES_HUMAN_REVIEW | none | final screening counts |

## Mutation testing

Baseline: `PASS`. 24 mutations: 17 input, 6 receipt, 1 engine-configuration. Detected 20; correctly ignored 1; blind spots 2; false positives 0.

| id | mutation | target | expected detection | detected | engine verdict | status | detecting invariants | missed | note |
|---|---|---|---|---|---|---|---|---|---|
| M01 | remove all inputs | input | yes | yes | ABSTAIN | DETECTED | attested_invocations, child_exit_integrity, citation_metadata, claim_value, dependency_validity, discovery_complete, duplicate_records, inputs_nonempty, inputs_present, output_determinism, population_closure, protocol_conformance, reviewer_protocol, rows_examined_complete, snapshot_rows, source_identity, timestamp_consistency | none | none |
| M02 | delete a table | input | yes | yes | ABSTAIN | DETECTED | citation_metadata, inputs_present | none | none |
| M03 | delete a row | input | yes | yes | FAIL | DETECTED | claim_value:C1, claim_value:C2, snapshot_rows | none | none |
| M04 | duplicate a row | input | yes | yes | FAIL | DETECTED | claim_value:C1, claim_value:C2, duplicate_records:records | none | none |
| M05 | duplicate a verdict | receipt | yes | yes | REJECTED | DETECTED | verdicts_unique_per_invocation | none | none |
| M06 | remove a reviewer | input | yes | yes | FAIL | DETECTED | reviewer_protocol | none | none |
| M07 | change a hash (resealed) | receipt | yes | yes | REJECTED | DETECTED | invocation_input_hashes_match_observed | none | none |
| M08 | change an author | input | yes | yes | FAIL | DETECTED | citation_metadata | none | none |
| M09 | replace a DOI | input | yes | yes | FAIL | DETECTED | citation_metadata | none | none |
| M10 | change a number | input | yes | yes | FAIL | DETECTED | claim_value:C1, claim_value:C2, snapshot_rows | none | none |
| M11 | add a thousands separator (semantically neutral) | input | no | no | PASS | CORRECTLY_IGNORED | none | none | 12480 -> 12,480 is the same number; detection would be a false positive |
| M11b | add a thousands separator and change the number | input | yes | yes | FAIL | DETECTED | claim_value:C1 | none | none |
| M12 | shift a timestamp by an offset | input | yes | yes | FAIL | DETECTED | timestamp_consistency | none | none |
| M13 | remove an invocation record | receipt | yes | yes | REJECTED | DETECTED | every_required_check_has_terminal_state, every_verdict_has_invocation, ledger_chain_intact, ledger_head_and_count_bound, pass_block_derived_from_ledger, pass_requires_complete_required_checks | none | none |
| M14 | inject a PASS summary with no evidence | input | yes | yes | ABSTAIN | DETECTED | attested_invocations | none | none |
| M15 | skip a required checker | engine | yes | yes | ERROR | DETECTED | every_required_check_has_terminal_state, pass_requires_complete_required_checks | none | none |
| M16 | truncate the ledger (re-chained) | receipt | yes | yes | REJECTED | DETECTED | every_required_check_has_terminal_state, pass_block_derived_from_ledger, pass_requires_complete_required_checks | none | none |
| M17 | reorder chained records | receipt | yes | yes | REJECTED | DETECTED | ledger_chain_intact | none | none |
| M18 | bump an upstream design version | input | yes | yes | ABSTAIN | DETECTED | dependency_validity | none | none |
| M19 | replace a stored output | input | yes | yes | FAIL | DETECTED | claim_value:C1, claim_value:C2, claim_value:C3, dependency_validity | none | none |
| P01 | substitute an unauthorised reviewer identity | input | yes | yes | FAIL | DETECTED | reviewer_protocol | none | protocol does not declare an authorised reviewer roster |
| P02 | forge a producer invocation record | input | yes | no | PASS | **BLIND_SPOT** | none | attested_invocations | producer invocation records are unauthenticated |
| P03 | edit evidence and fully reseal an UNSIGNED receipt | receipt | yes | no | ACCEPTED | **BLIND_SPOT** | none | receipt_hash_binds_content | hash binding without a signature cannot authenticate the sealer |
| P04 | near-duplicate record under a new key | input | yes | yes | FAIL | DETECTED_INCIDENTALLY | claim_value:C1, claim_value:C2, reviewer_protocol, snapshot_rows | duplicate_records:records | duplicate detection is exact-match on key/row |

### Blind spots and partial detections (published, not suppressed)

- **P02 forge a producer invocation record** — engine verdict PASS (missed detection). producer invocation records are unauthenticated
- **P03 edit evidence and fully reseal an UNSIGNED receipt** — engine verdict ACCEPTED (missed detection). hash binding without a signature cannot authenticate the sealer

## Dependency-aware validity demo

- Impact of changing `design`: descendants marked stale = admitted-evidence, analysis-run, conclusion, ranking, figure; recomputed = none; declared false = none.
- After design v2→v3: stale = admitted-evidence, analysis-run, conclusion, figure, ranking; publication blocked = admitted-evidence, analysis-run, conclusion, figure, ranking.
- Revalidation with identical output: REVALIDATED_UNCHANGED; still pending: none.
- Revalidation with changed output: REVALIDATED_CHANGED; still pending: analysis-run, conclusion, ranking, figure.

Staleness is not falsity: no stale node was declared false or silently recomputed.

## Determinism across hash seeds

| PYTHONHASHSEED | exit | receipt file sha256 |
|---|---|---|
| 0 | 0 | 8ff328e72e13f209dfaea1479012f107d6bb2567de8741a8407f0176792389b6 |
| 1 | 0 | 8ff328e72e13f209dfaea1479012f107d6bb2567de8741a8407f0176792389b6 |
| 12345 | 0 | 8ff328e72e13f209dfaea1479012f107d6bb2567de8741a8407f0176792389b6 |

Byte-identical: **yes** (clock fixed via SOURCE_DATE_EPOCH).

## Receipt statement

> A receipt supports integrity, provenance, and replayability. It does not establish scientific truth, accuracy, safety, or fitness for use.

Signature state of every fixture receipt: UNSIGNED (no signing key configured; no signature fabricated).
