"""Deterministic generator for the engine fixture corpus (fixtures/<name>/).

All data are synthetic. DOIs use the Crossref test prefix 10.5555 and are resolved only
against the fixture's own closed-world registry snapshot; they are not real publications.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path
from typing import Any, Callable

import yaml

from .claims import RECIPE_INTERPRETER, input_manifest_sha256
from .dependencies import DependencyGraph
from .models import sha256_file, sha256_json

RECORDS = [
    {"record_id": "R1", "source_id": "S1", "title": "Trial one, arm comparison", "source_retrieved_at": "2026-01-10T09:00:00Z", "n": "2400", "effect": "0.41"},
    {"record_id": "R2", "source_id": "S2", "title": "Trial two", "source_retrieved_at": "2026-01-11T10:30:00Z", "n": "3100", "effect": "0.38"},
    {"record_id": "R3", "source_id": "S3", "title": "Cohort three, \"extended\"", "source_retrieved_at": "2026-01-12T08:15:00Z", "n": "1980", "effect": "0.47"},
    {"record_id": "R4", "source_id": "S1", "title": "Trial four", "source_retrieved_at": "2026-01-10T09:00:00Z", "n": "2800", "effect": "0.44"},
    {"record_id": "R5", "source_id": "S2", "title": "Trial five", "source_retrieved_at": "2026-01-11T10:30:00Z", "n": "2200", "effect": "0.40"},
]
SOURCES = [
    {"source_id": "S1", "url": "https://example.org/source/1", "retrieved_at": "2026-01-10T09:00:00Z"},
    {"source_id": "S2", "url": "https://example.org/source/2", "retrieved_at": "2026-01-11T10:30:00Z"},
    {"source_id": "S3", "url": "https://example.org/source/3", "retrieved_at": "2026-01-12T08:15:00Z"},
]
ARMS = [
    {"arm": "A", "trial": "1", "score": "0.84"},
    {"arm": "A", "trial": "2", "score": "0.86"},
    {"arm": "B", "trial": "1", "score": "0.8508"},
    {"arm": "B", "trial": "2", "score": "0.8500"},
]
REVIEWERS = ["rev-alpha", "rev-beta"]
CITATIONS = [
    {"citation_id": "K1", "doi": "10.5555/szl.fixture.0001", "authors": "Quispe; Mamani", "year": "2024"},
    {"citation_id": "K2", "doi": "10.5555/szl.fixture.0002", "authors": "Huaman", "year": "2025"},
]
DOI_REGISTRY = {
    "source": "synthetic fixture registry snapshot (not a live registry)",
    "retrieved_at": "2026-01-15T00:00:00Z",
    "closed_world": True,
    "records": {
        "10.5555/szl.fixture.0001": {"authors": ["Quispe", "Mamani"], "year": 2024},
        "10.5555/szl.fixture.0002": {"authors": ["Huaman"], "year": 2025},
    },
}
STEPS = ["search", "screen", "extract", "review", "analyze"]

INPUTS = [
    ("records", "inputs/records.csv", "table", "record_id"),
    ("sources", "inputs/sources.csv", "table", "source_id"),
    ("arm_results", "inputs/arm_results.csv", "table", None),
    ("reviews", "inputs/reviews.csv", "table", None),
    ("candidates", "inputs/candidates.csv", "table", "record_id"),
    ("screening", "inputs/screening.csv", "table", "record_id"),
    ("citations", "inputs/citations.csv", "table", "citation_id"),
    ("doi_registry", "inputs/doi_registry.json", "json", None),
    ("snapshot", "inputs/snapshot.json", "json", None),
    ("claims", "inputs/claims.yaml", "yaml", None),
    ("registry", "inputs/registry.yaml", "yaml", None),
    ("protocol_log", "inputs/protocol_log.yaml", "yaml", None),
    ("dag", "inputs/dag.yaml", "yaml", None),
    ("attestation", "inputs/attestation.yaml", "yaml", None),
    ("producer_invocations", "inputs/producer_invocations.jsonl", "jsonl", None),
    ("replicate_a", "inputs/replicate_a.csv", "table", None),
    ("replicate_b", "inputs/replicate_b.csv", "table", None),
]


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields or list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="")


def read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="")


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="")


def manifest_doc(name: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "1.0",
        "name": name,
        "access": "open",
        "inputs_dir": "inputs",
        "inputs": [{"id": i, "path": p, "kind": k, **({"key": key} if key else {})} for i, p, k, key in INPUTS],
        "snapshot": {"input": "snapshot", "table": "records"},
        "reviews": {"table": "reviews", "target_table": "records", "record_field": "record_id", "reviewer_field": "reviewer", "required_per_record": 2, "authorized_reviewers": REVIEWERS},
        "sources": {"table": "sources", "key": "source_id", "records_table": "records", "records_field": "source_id"},
        "timestamps": {"table": "records", "field": "source_retrieved_at", "join": {"table": "sources", "key": "source_id", "field": "retrieved_at"}},
        "protocol": {"version": "1.0", "steps": STEPS, "execution_log": "protocol_log"},
        "claims": {"input": "claims", "registry": "registry"},
        "dependencies": {"input": "dag"},
        "citations": {"table": "citations", "registry": "doi_registry", "resolver": "offline"},
        "screening": {"candidates": "candidates", "decisions": "screening", "key": "record_id"},
        "attestations": {"input": "attestation", "invocations": "producer_invocations"},
        "determinism": {"replicates": [{"input": "replicate_a", "hash_seed": 0}, {"input": "replicate_b", "hash_seed": 12345}]},
    }
    if extra:
        m.update(extra)
    return m


RECIPES = {
    "total_n": {"metric": "total_n", "op": "sum", "table": "records", "field": "n"},
    "mean_effect": {"metric": "mean_effect", "op": "mean", "table": "records", "field": "effect"},
    "acc_a": {"metric": "acc_a", "op": "mean", "table": "arm_results", "field": "score", "where": {"arm": "A"}},
    "acc_b": {"metric": "acc_b", "op": "mean", "table": "arm_results", "field": "score", "where": {"arm": "B"}},
}

CLAIMS = [
    {"id": "C1", "text": "Total participants across admitted studies: 12480", "value": "12480", "metric": "total_n"},
    {"id": "C2", "text": "Mean effect size: 0.42", "value": "0.42", "metric": "mean_effect"},
    {"id": "C3", "text": "Arm A and arm B accuracy are equal (0.85)", "relation": "equal", "metrics": ["acc_a", "acc_b"], "value": "0.85", "tolerance": "0.001"},
]
CLAIM_RECIPES = {"C1": ["total_n"], "C2": ["mean_effect"], "C3": ["acc_a", "acc_b"]}


def _stored_output(root: Path) -> None:
    from .claims import run_recipe

    tables = {"records": read_csv(root / "inputs/records.csv"), "arm_results": read_csv(root / "inputs/arm_results.csv")}
    rows = []
    for metric, rcp in RECIPES.items():
        v = run_recipe(rcp, tables)
        rows.append({"metric": metric, "value": format(v.normalize(), "f")})
    write_csv(root / "outputs/summary.csv", rows, ["metric", "value"])


def _derived(root: Path, snapshot: bool = True, registry: bool = True, dag: bool = True, output: bool = True) -> None:
    """Recompute derived artifacts (snapshot, stored output, registry hashes, DAG fingerprints)."""
    if snapshot:
        rows = read_csv(root / "inputs/records.csv")
        dump_json(root / "inputs/snapshot.json", {"table": "records", "key": "record_id", "accepted_at": "2026-01-20T00:00:00Z", "row_sha256": {r["record_id"]: sha256_json(r) for r in rows}})
    if output:
        _stored_output(root)
    if registry:
        claims = yaml.safe_load((root / "inputs/claims.yaml").read_text(encoding="utf-8"))["claims"]
        out_sha = sha256_file(root / "outputs/summary.csv")
        reg = {"claims": {}}
        for c in claims:
            if c["id"] not in CLAIM_RECIPES:
                continue
            reg["claims"][c["id"]] = {
                "recipe": [RECIPES[m] for m in CLAIM_RECIPES[c["id"]]],
                "code_version": RECIPE_INTERPRETER,
                "environment": "szl-evidence recipe interpreter (whitelisted aggregates)",
                "input_manifest_sha256": input_manifest_sha256([RECIPES[m] for m in CLAIM_RECIPES[c["id"]]], {t: sha256_file(root / f"inputs/{t}.csv") for t in ("records", "arm_results")}),
                "stored_output": "outputs/summary.csv",
                "output_sha256": out_sha,
                "review_state": "reviewed",
                "publication": "fixture://valid/report#" + c["id"],
            }
        dump_yaml(root / "inputs/registry.yaml", reg)
    if dag:
        _write_dag(root)


def _write_dag(root: Path, design_version: str = "2") -> None:
    nodes = [
        {"id": "source-snapshot", "kind": "SOURCE_SNAPSHOT", "version": "1", "path": "inputs/snapshot.json"},
        {"id": "design", "kind": "DESIGN", "version": design_version, "depends_on": ["source-snapshot"]},
        {"id": "admitted-evidence", "kind": "ADMITTED_EVIDENCE", "version": "1", "path": "inputs/screening.csv", "depends_on": ["design"]},
        {"id": "analysis-run", "kind": "ANALYSIS_RUN", "version": "1", "path": "outputs/summary.csv", "depends_on": ["admitted-evidence"]},
        {"id": "ranking", "kind": "RANKING", "version": "1", "depends_on": ["analysis-run"]},
        {"id": "figure", "kind": "FIGURE", "version": "1", "depends_on": ["ranking"]},
        {"id": "conclusion", "kind": "CONCLUSION", "version": "1", "depends_on": ["figure", "analysis-run"]},
    ]
    g = DependencyGraph.load({"nodes": nodes}, root)
    for n in nodes:
        n["validated_against"] = {p: g.nodes[p].fingerprint() for p in n.get("depends_on", [])}
        if n["id"] == "analysis-run":
            n["output_sha256"] = sha256_file(root / "outputs/summary.csv")
    dump_yaml(root / "inputs/dag.yaml", {"nodes": nodes})


def build_valid(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / "inputs").mkdir(parents=True)
    write_csv(root / "inputs/records.csv", RECORDS)
    write_csv(root / "inputs/sources.csv", SOURCES)
    write_csv(root / "inputs/arm_results.csv", ARMS)
    write_csv(root / "inputs/reviews.csv", [{"record_id": r["record_id"], "reviewer": v, "decision": "include"} for r in RECORDS for v in REVIEWERS])
    write_csv(root / "inputs/candidates.csv", [{"record_id": f"R{i}"} for i in range(1, 7)])
    write_csv(root / "inputs/screening.csv", [{"record_id": f"R{i}", "decision": "admitted" if i <= 5 else "excluded"} for i in range(1, 7)])
    write_csv(root / "inputs/citations.csv", CITATIONS)
    dump_json(root / "inputs/doi_registry.json", DOI_REGISTRY)
    dump_yaml(root / "inputs/claims.yaml", {"claims": CLAIMS})
    dump_yaml(root / "inputs/protocol_log.yaml", {"protocol_version": "1.0", "steps_executed": STEPS})
    dump_yaml(root / "inputs/attestation.yaml", {"producer": "fixture-pipeline", "claimed_status": "PASS", "checks_claimed": ["schema", "duplicates"], "children": [{"name": "schema", "exit_code": 0, "result": "PASS"}, {"name": "duplicates", "exit_code": 0, "result": "PASS"}]})
    (root / "inputs/producer_invocations.jsonl").write_text(
        "".join(json.dumps({"invocation_id": f"p-{i}", "check": c, "result": "PASS", "evidence": {"rows": 5}}, sort_keys=True) + "\n" for i, c in enumerate(["schema", "duplicates"])),
        encoding="utf-8",
        newline="",
    )
    rep = [{"record_id": r["record_id"], "score": r["effect"]} for r in RECORDS]
    write_csv(root / "inputs/replicate_a.csv", rep)
    write_csv(root / "inputs/replicate_b.csv", rep)
    dump_yaml(root / "manifest.yaml", manifest_doc("valid"))
    _derived(root)


# ------------------------------------------------------------------ variants
def _edit_csv(root: Path, rel: str, fn: Callable[[list[dict[str, str]]], list[dict[str, str]]]) -> None:
    p = root / rel
    rows = read_csv(p)
    fields = list(rows[0].keys()) if rows else None
    new = fn(rows)
    if new:
        write_csv(p, new, fields)
    else:
        p.write_text(",".join(fields or []) + "\n", encoding="utf-8")


def _edit_yaml(root: Path, rel: str, fn: Callable[[Any], Any]) -> None:
    p = root / rel
    dump_yaml(p, fn(yaml.safe_load(p.read_text(encoding="utf-8"))))


def v_empty_input(root: Path) -> None:
    shutil.rmtree(root / "inputs")
    shutil.rmtree(root / "outputs")
    (root / "inputs").mkdir()
    (root / "inputs/.gitkeep").write_text("")
    dump_yaml(root / "manifest.yaml", {"manifest_version": "1.0", "name": "empty-input", "inputs_dir": "inputs", "ignore": ["**/.gitkeep", ".gitkeep", "inputs/.gitkeep"], "inputs": [{"id": "records", "path": "inputs/records.csv", "kind": "table", "key": "record_id"}]})


def v_missing_table(root: Path) -> None:
    (root / "inputs/reviews.csv").unlink()


def v_partial(root: Path) -> None:
    _edit_yaml(root, "manifest.yaml", lambda m: {**m, "limits": {"max_rows": 3}})


def v_narrated(root: Path) -> None:
    _edit_yaml(root, "inputs/attestation.yaml", lambda a: {**a, "checks_claimed": ["schema", "duplicates", "citation_resolution", "human_review"]})


def v_duplicate_row(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: rows + [dict(rows[2])])
    _derived(root, snapshot=False, registry=False, dag=False, output=False)


def v_deleted_row(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: rows[:-1])
    _edit_csv(root, "inputs/reviews.csv", lambda rows: [r for r in rows if r["record_id"] != "R5"])


def v_unregistered(root: Path) -> None:
    _edit_yaml(root, "inputs/claims.yaml", lambda c: {"claims": c["claims"] + [{"id": "C4", "text": "Median follow-up was 14 months", "value": "14", "metric": "median_follow_up"}]})


def v_rounding(root: Path) -> None:
    _edit_csv(root, "inputs/arm_results.csv", lambda rows: [{**r, "score": {("A", "1"): "0.8498", ("A", "2"): "0.8600", ("B", "1"): "0.8402", ("B", "2"): "0.8500"}[(r["arm"], r["trial"])]} for r in rows])
    _derived(root, snapshot=False, dag=True)


def v_comma(root: Path) -> None:
    _edit_yaml(root, "inputs/claims.yaml", lambda c: {"claims": [{**x, "value": "12,408", "text": "Total participants across admitted studies: 12,408"} if x["id"] == "C1" else x for x in c["claims"]]})


def v_nondet(root: Path) -> None:
    _edit_csv(root, "inputs/replicate_b.csv", lambda rows: list(reversed(rows)))


def v_timezone(root: Path) -> None:
    _edit_csv(root, "inputs/records.csv", lambda rows: [{**r, "source_retrieved_at": "2026-01-11T10:30:00+02:00"} if r["record_id"] == "R2" else r for r in rows])
    _derived(root, registry=True, dag=True)


def v_wrong_authors(root: Path) -> None:
    _edit_csv(root, "inputs/citations.csv", lambda rows: [{**r, "authors": "Quispe; Condori"} if r["citation_id"] == "K1" else r for r in rows])


def v_nonexistent_doi(root: Path) -> None:
    _edit_csv(root, "inputs/citations.csv", lambda rows: [{**r, "doi": "10.5555/szl.fixture.9999"} if r["citation_id"] == "K2" else r for r in rows])


def v_missing_reviewer(root: Path) -> None:
    _edit_csv(root, "inputs/reviews.csv", lambda rows: [r for r in rows if not (r["record_id"] == "R4" and r["reviewer"] == "rev-beta")])


def v_protocol_drift(root: Path) -> None:
    _edit_yaml(root, "inputs/protocol_log.yaml", lambda _: {"protocol_version": "1.1", "steps_executed": ["search", "screen", "extract", "analyze"]})


def v_omitted(root: Path) -> None:
    _edit_csv(root, "inputs/candidates.csv", lambda rows: rows + [{"record_id": "R7"}])


def v_stale(root: Path) -> None:
    # Design changes to v3 after downstream nodes were validated against v2.
    _edit_yaml(root, "inputs/dag.yaml", lambda d: {"nodes": [{**n, "version": "3"} if n["id"] == "design" else n for n in d["nodes"]]})


def v_unresolved(root: Path) -> None:
    _edit_csv(root, "inputs/screening.csv", lambda rows: [{**r, "decision": "unresolved"} if r["record_id"] == "R6" else r for r in rows])
    _write_dag(root)


VARIANTS: dict[str, tuple[Callable[[Path], None] | None, dict[str, Any]]] = {
    "valid": (None, {"status": "PASS", "exit": 0, "evidence": ["pass_evidence"], "claim": "none; all declared claims verified against stored outputs and replayed recipes", "why": "All inputs present, every required check ran and passed."}),
    "empty-input": (v_empty_input, {"status": "ABSTAIN", "exit": 2, "evidence": ["VACUOUS_PASS"], "claim": "any claim about the corpus", "why": "Nothing was examined, so nothing could fail: a vacuous pass is refused."}),
    "missing-table": (v_missing_table, {"status": "ABSTAIN", "exit": 2, "evidence": ["INSUFFICIENT_EVIDENCE", "REQUIRES_HUMAN_REVIEW"], "claim": "that every record was reviewed", "why": "reviews.csv is declared but absent; the gap is visible, not zero."}),
    "partial-execution": (v_partial, {"status": "ABSTAIN", "exit": 2, "evidence": ["PARTIAL_EXECUTION"], "claim": "any population-level result", "why": "Only 3 of N rows examined; cannot be presented as complete."}),
    "narrated-verification": (v_narrated, {"status": "ABSTAIN", "exit": 2, "evidence": ["NARRATED_VERIFICATION", "UNVERIFIED"], "claim": "that citation_resolution and human_review ran", "why": "Producer claims checks with no invocation records."}),
    "duplicate-row": (v_duplicate_row, {"status": "FAIL", "exit": 1, "evidence": ["duplicate_records:records"], "claim": "the stated participant total", "why": "Record R3 appears twice."}),
    "deleted-row": (v_deleted_row, {"status": "FAIL", "exit": 1, "evidence": ["snapshot_rows"], "claim": "that the analysed set equals the accepted snapshot", "why": "R5 was deleted after the snapshot was accepted."}),
    "unregistered-claim": (v_unregistered, {"status": "FAIL", "exit": 1, "evidence": ["EPHEMERAL_CLAIM", "claim_value:C4"], "claim": "C4 (median follow-up)", "why": "A published number has no registry entry; other claims being registered does not excuse it."}),
    "numeric-rounding": (v_rounding, {"status": "FAIL", "exit": 1, "evidence": ["claim_value:C3", "DEFECTIVE_VERIFICATION"], "claim": "C3 (arms equal)", "why": "0.8549 and 0.8451 both round to 0.85 but differ by 0.0098 > tolerance 0.001."}),
    "comma-tokenization": (v_comma, {"status": "FAIL", "exit": 1, "evidence": ["claim_value:C1"], "claim": "C1 (participant total)", "why": "Published '12,408' parses to 12408, not the stored 12480; separators neither evade nor fake comparison."}),
    "nondeterministic-order": (v_nondet, {"status": "FAIL", "exit": 1, "evidence": ["output_determinism"], "claim": "that the output is reproducible byte-for-byte", "why": "Replicates differ only in row order."}),
    "timezone-mismatch": (v_timezone, {"status": "FAIL", "exit": 1, "evidence": ["SOURCE_MISMATCH", "timestamp_consistency"], "claim": "that R2 matches its source retrieval", "why": "Same wall-clock, different offset: instants differ by 2h."}),
    "wrong-authors": (v_wrong_authors, {"status": "FAIL", "exit": 1, "evidence": ["SOURCE_MISMATCH", "citation_metadata"], "claim": "citation K1 attribution", "why": "Authors disagree with registry."}),
    "nonexistent-doi": (v_nonexistent_doi, {"status": "FAIL", "exit": 1, "evidence": ["citation_metadata"], "claim": "citation K2 exists", "why": "DOI absent from a closed-world registry snapshot."}),
    "missing-reviewer": (v_missing_reviewer, {"status": "FAIL", "exit": 1, "evidence": ["PROTOCOL_BROKEN", "reviewer_protocol"], "claim": "dual review of R4", "why": "R4 has 1 of 2 required reviewers."}),
    "protocol-drift": (v_protocol_drift, {"status": "FAIL", "exit": 1, "evidence": ["PROTOCOL_DRIFT"], "claim": "that the declared protocol was followed", "why": "Version 1.1 executed, 'review' step skipped."}),
    "omitted-population": (v_omitted, {"status": "FAIL", "exit": 1, "evidence": ["OMITTED_POPULATION"], "claim": "complete screening", "why": "Candidate R7 never entered the screened set."}),
    "stale-dependency": (v_stale, {"status": "ABSTAIN", "exit": 2, "evidence": ["dependency_validity", "STALE_PENDING_REVALIDATION"], "claim": "the current conclusion (pending revalidation, not false)", "why": "Design bumped to v3; descendants stale; publication blocked."}),
    "unresolved": (v_unresolved, {"status": "ABSTAIN", "exit": 2, "evidence": ["REQUIRES_HUMAN_REVIEW"], "claim": "final screening counts", "why": "R6 is unresolved."}),
}


def build_fixture(root: Path, name: str) -> None:
    fn, exp = VARIANTS[name]
    build_valid(root)
    if fn:
        fn(root)
    if name != "empty-input":
        _edit_yaml(root, "manifest.yaml", lambda m: {**m, "name": name})
    dump_yaml(
        root / "expected.yaml",
        {
            "fixture": name,
            "expected_status": exp["status"],
            "expected_exit_code": exp["exit"],
            "required_evidence": exp["evidence"],
            "claim_not_established": exp["claim"],
            "explanation": exp["why"],
        },
    )


def build_all(dest: Path) -> list[str]:
    for name in VARIANTS:
        build_fixture(dest / name, name)
    return list(VARIANTS)
