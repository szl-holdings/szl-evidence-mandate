"""Publication depends on usable ancestry, including after a graph reload."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict

import pytest
import yaml

from szl_evidence.dependencies import DependencyError, DependencyGraph
from szl_evidence.models import Validity
from szl_evidence.verifier import verify


def graph_data() -> dict:
    return {
        "nodes": [
            {"id": "source", "kind": "SOURCE_SNAPSHOT", "version": "1", "output_sha256": "a" * 64},
            {
                "id": "analysis", "kind": "ANALYSIS_RUN", "version": "1",
                "depends_on": ["source"], "validated_against": {"source": "1"},
                "output_sha256": "a" * 64,
            },
            {
                "id": "conclusion", "kind": "CONCLUSION", "version": "1",
                "depends_on": ["analysis"], "validated_against": {"analysis": "1"},
                "output_sha256": "a" * 64,
            },
            {"id": "independent", "kind": "SOURCE_SNAPSHOT", "version": "1"},
        ],
    }


def reload_graph(graph: DependencyGraph) -> DependencyGraph:
    # Exercise the actual load boundary with persisted state strings, rather
    # than keeping the original in-memory Node objects alive.
    saved = json.dumps({"nodes": [asdict(node) for node in graph.nodes.values()]})
    return DependencyGraph.load(json.loads(saved))


@pytest.mark.parametrize("state", [
    Validity.INVALIDATED, Validity.SUPERSEDED, Validity.UNRESOLVED,
    Validity.STALE_PENDING_REVALIDATION,
])
def test_persisted_unusable_parent_blocks_its_full_dependency_closure(state):
    data = graph_data()
    data["nodes"][0]["state"] = state.value
    graph = DependencyGraph.load(data)

    result = graph.evaluate()

    assert result["direct_drift"] == {}  # all recorded fingerprints still match
    assert result["publication_blocked"] == ["analysis", "conclusion", "source"]
    assert graph.nodes["source"].state == state
    assert graph.nodes["analysis"].state == Validity.STALE_PENDING_REVALIDATION
    assert graph.nodes["conclusion"].state == Validity.STALE_PENDING_REVALIDATION
    assert graph.nodes["independent"].state == Validity.CURRENT
    assert reload_graph(graph).evaluate() == result


def test_missing_parent_marks_consumer_unresolved_and_blocks_descendants():
    data = graph_data()
    data["nodes"].pop(0)
    graph = DependencyGraph.load(data)

    result = graph.evaluate()

    assert result["publication_blocked"] == ["analysis", "conclusion"]
    assert result["broken_refs"] == [{"node": "analysis", "missing_parent": "source"}]
    assert graph.nodes["analysis"].state == Validity.UNRESOLVED
    assert graph.nodes["conclusion"].state == Validity.STALE_PENDING_REVALIDATION
    assert reload_graph(graph).evaluate() == result


def test_non_parent_validation_reference_blocks_publication():
    data = graph_data()
    data["nodes"][1]["validated_against"]["independent"] = "1"
    graph = DependencyGraph.load(data)

    result = graph.evaluate()

    assert result["publication_blocked"] == ["analysis", "conclusion"]
    assert result["broken_refs"] == [{"node": "analysis", "validated_against_non_parent": "independent"}]
    assert graph.nodes["analysis"].state == Validity.UNRESOLVED


def test_missing_artifact_path_blocks_its_full_dependency_closure(tmp_path):
    data = graph_data()
    data["nodes"][0]["path"] = "missing-source.json"
    graph = DependencyGraph.load(data, tmp_path)

    result = graph.evaluate()

    assert result["publication_blocked"] == ["analysis", "conclusion", "source"]
    assert result["broken_refs"] == [{"node": "source", "missing_path": "missing-source.json"}]
    assert graph.nodes["source"].state == Validity.UNRESOLVED


def test_restored_parent_requires_explicit_revalidation_to_recover():
    data = graph_data()
    source = data["nodes"].pop(0)
    graph = DependencyGraph.load(data)
    graph.evaluate()
    repaired = {"nodes": [asdict(node) for node in graph.nodes.values()] + [source]}
    graph = DependencyGraph.load(json.loads(json.dumps(repaired)))

    assert graph.evaluate()["broken_refs"] == []
    assert graph.nodes["analysis"].state == Validity.UNRESOLVED
    assert graph.evaluate()["publication_blocked"] == ["analysis", "conclusion"]
    result = graph.revalidate("analysis", "a" * 64)

    assert result["result"] == Validity.REVALIDATED_UNCHANGED.value
    assert graph.evaluate()["publication_blocked"] == []


def test_restored_artifact_requires_reload_and_explicit_revalidation(tmp_path):
    data = graph_data()
    content = b"restored evidence\n"
    digest = hashlib.sha256(content).hexdigest()
    data["nodes"][0].update(path="source.json", output_sha256=digest)
    data["nodes"][1]["validated_against"]["source"] = f"1@{digest[:12]}"
    graph = DependencyGraph.load(data, tmp_path)
    graph.evaluate()
    saved = json.dumps({"nodes": [asdict(node) for node in graph.nodes.values()]})
    (tmp_path / "source.json").write_bytes(content)
    # load() captures current file bytes; revalidation does not manufacture a
    # content hash for a previously missing artifact or silently re-read files.
    graph = DependencyGraph.load(json.loads(saved), tmp_path)

    assert graph.evaluate()["broken_refs"] == []
    assert graph.nodes["source"].state == Validity.UNRESOLVED
    result = graph.revalidate("source", digest)

    assert result["result"] == Validity.REVALIDATED_UNCHANGED.value
    assert graph.evaluate()["publication_blocked"] == []


@pytest.mark.parametrize("fault", ["missing_parent", "missing_path", "non_parent_validation"])
def test_unresolved_node_cannot_revalidate_with_remaining_structural_fault(fault, tmp_path):
    data = graph_data()
    target = "analysis"
    if fault == "missing_parent":
        data["nodes"].pop(0)
    elif fault == "missing_path":
        data["nodes"][0]["path"] = "missing-source.json"
        target = "source"
    else:
        data["nodes"][1]["validated_against"]["independent"] = "1"
    graph = DependencyGraph.load(data, tmp_path)
    graph.evaluate()

    with pytest.raises(DependencyError, match="structural"):
        graph.revalidate(target, "a" * 64)
    assert graph.nodes[target].state == Validity.UNRESOLVED
    assert target in graph.evaluate()["publication_blocked"]


@pytest.mark.parametrize("state", [Validity.INVALIDATED, Validity.UNRESOLVED, Validity.STALE_PENDING_REVALIDATION])
def test_structurally_repaired_unresolved_node_still_requires_ready_ancestry(state):
    data = graph_data()
    data["nodes"][0]["state"] = state.value
    data["nodes"][1]["state"] = Validity.UNRESOLVED.value
    graph = DependencyGraph.load(data)

    assert graph.broken_refs() == []
    with pytest.raises(DependencyError, match="parent.*not ready"):
        graph.revalidate("analysis", "a" * 64)
    assert graph.nodes["analysis"].state == Validity.UNRESOLVED


@pytest.mark.parametrize("state", [Validity.INVALIDATED, Validity.SUPERSEDED])
def test_structural_error_does_not_erase_terminal_state(state):
    data = graph_data()
    data["nodes"][1]["state"] = state.value
    data["nodes"].pop(0)
    graph = DependencyGraph.load(data)

    result = graph.evaluate()
    graph.mark_unresolved()

    assert result["publication_blocked"] == ["analysis", "conclusion"]
    assert graph.nodes["analysis"].state == state


@pytest.mark.parametrize("operation", ["invalidate", "supersede", "impact"])
def test_dependency_propagation_preserves_existing_terminal_descendants(operation):
    data = graph_data()
    data["nodes"][1]["state"] = Validity.INVALIDATED.value
    data["nodes"][2]["state"] = Validity.SUPERSEDED.value
    graph = DependencyGraph.load(data)

    if operation == "invalidate":
        graph.invalidate("source", "source was disproved")
    elif operation == "supersede":
        graph.supersede("source", by="independent")
    else:
        graph.impact("source")

    assert graph.nodes["analysis"].state == Validity.INVALIDATED
    assert graph.nodes["conclusion"].state == Validity.SUPERSEDED
    assert "conclusion" in graph.evaluate()["publication_blocked"]
    with pytest.raises(DependencyError, match="not pending revalidation"):
        graph.revalidate("analysis", "a" * 64)


def test_healthy_graph_remains_current_and_unblocked():
    graph = DependencyGraph.load(graph_data())
    before = copy.deepcopy(graph.nodes)

    result = graph.evaluate()

    assert result["direct_drift"] == {}
    assert result["broken_refs"] == []
    assert result["stale"] == result["publication_blocked"] == []
    assert graph.nodes == before
    assert graph.evaluate() == result


def test_unchanged_revalidation_clears_only_the_revalidated_dependency_path():
    data = graph_data()
    data["nodes"][0]["state"] = Validity.STALE_PENDING_REVALIDATION.value
    graph = DependencyGraph.load(data)
    graph.evaluate()

    result = graph.revalidate("source", "a" * 64)

    assert result["result"] == Validity.REVALIDATED_UNCHANGED.value
    assert result["descendants_still_pending"] == []
    assert graph.evaluate()["publication_blocked"] == []
    assert reload_graph(graph).evaluate()["publication_blocked"] == []


def test_changed_revalidation_keeps_descendants_blocked_until_they_revalidate():
    data = graph_data()
    data["nodes"][0]["state"] = Validity.STALE_PENDING_REVALIDATION.value
    graph = DependencyGraph.load(data)
    graph.evaluate()

    changed = graph.revalidate("source", "b" * 64)

    assert changed["result"] == Validity.REVALIDATED_CHANGED.value
    assert set(changed["descendants_still_pending"]) == {"analysis", "conclusion"}
    graph = reload_graph(graph)
    assert graph.evaluate()["publication_blocked"] == ["analysis", "conclusion"]
    graph.revalidate("analysis", "a" * 64)
    assert graph.evaluate()["publication_blocked"] == []


@pytest.mark.parametrize("state", [
    Validity.INVALIDATED, Validity.SUPERSEDED, Validity.UNRESOLVED,
    Validity.STALE_PENDING_REVALIDATION,
])
def test_revalidation_cannot_clear_a_node_with_an_unusable_ancestor(state):
    data = graph_data()
    data["nodes"][0]["state"] = state.value
    data["nodes"][2]["state"] = Validity.STALE_PENDING_REVALIDATION.value
    graph = DependencyGraph.load(data)

    # A caller must not clear a leaf by skipping evaluate() or by relying on
    # a matching fingerprint while its invalid ancestry is still persisted.
    with pytest.raises(DependencyError, match="parent.*not ready"):
        graph.revalidate("conclusion", "a" * 64)
    assert graph.evaluate()["publication_blocked"] == ["analysis", "conclusion", "source"]


def test_unchanged_revalidation_cannot_clear_an_independently_blocked_branch():
    data = graph_data()
    data["nodes"][0]["state"] = Validity.STALE_PENDING_REVALIDATION.value
    data["nodes"][3]["state"] = Validity.INVALIDATED.value
    data["nodes"][1]["depends_on"].append("independent")
    data["nodes"][1]["validated_against"]["independent"] = "1"
    graph = DependencyGraph.load(data)
    graph.evaluate()

    result = graph.revalidate("source", "a" * 64)

    assert set(result["descendants_still_pending"]) == {"analysis", "conclusion"}
    assert graph.evaluate()["publication_blocked"] == ["analysis", "conclusion", "independent"]


def test_unchanged_revalidation_leaves_missing_secondary_parent_unresolved():
    data = graph_data()
    data["nodes"][0]["state"] = Validity.STALE_PENDING_REVALIDATION.value
    data["nodes"][1]["depends_on"].append("missing")
    graph = DependencyGraph.load(data)
    graph.evaluate()

    result = graph.revalidate("source", "a" * 64)

    assert result["result"] == Validity.REVALIDATED_UNCHANGED.value
    assert graph.nodes["analysis"].state == Validity.UNRESOLVED
    assert graph.nodes["conclusion"].state == Validity.STALE_PENDING_REVALIDATION
    assert graph.evaluate()["publication_blocked"] == ["analysis", "conclusion"]


def test_supersede_then_rewire_revalidates_consumers_but_retains_archived_blocker():
    graph = DependencyGraph.load(graph_data())
    graph.supersede("source", by="independent")
    graph.nodes["analysis"].depends_on = ["independent"]
    graph.nodes["analysis"].validated_against = {}

    result = graph.revalidate("analysis", "a" * 64)

    assert result["result"] == Validity.REVALIDATED_UNCHANGED.value
    assert result["descendants_still_pending"] == []
    assert graph.nodes["conclusion"].state == Validity.CURRENT
    # evaluate() covers the whole supplied graph, not an inferred publication
    # subset. Rewiring consumers does not turn the archived source current.
    assert graph.evaluate()["publication_blocked"] == ["source"]


def test_engine_does_not_pass_a_superseded_leaf(valid):
    path = valid / "inputs/dag.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    next(node for node in data["nodes"] if node["id"] == "conclusion")["state"] = "SUPERSEDED"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    result = verify(valid)

    assert result["status"] == "ABSTAIN"
    invocation = next(item for item in result["invocations"] if item["check"] == "dependency_validity")
    assert invocation["result"]["status"] == "ABSTAIN"
    assert invocation["result"]["evidence"][0]["publication_blocked"] == ["conclusion"]
