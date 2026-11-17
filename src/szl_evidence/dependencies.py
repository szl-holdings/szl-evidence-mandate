"""Dependency-aware validity.

SOURCE SNAPSHOT -> DESIGN -> ADMITTED EVIDENCE -> ANALYSIS RUN -> RANKING -> FIGURE -> CONCLUSION

Each node records the fingerprint of every parent it was validated against. When a parent's
current fingerprint differs, the node and all its descendants become
STALE_PENDING_REVALIDATION. Nothing is recomputed silently and nothing is declared false:
staleness is not falsity. Stale nodes are blocked from publication until revalidated.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .models import Validity, sha256_file
from .safety import contained

KINDS = ["SOURCE_SNAPSHOT", "DESIGN", "ADMITTED_EVIDENCE", "ANALYSIS_RUN", "RANKING", "FIGURE", "CONCLUSION"]
_TERMINAL_STATES = {Validity.SUPERSEDED, Validity.INVALIDATED}
_BLOCKED_STATES = _TERMINAL_STATES | {Validity.UNRESOLVED, Validity.STALE_PENDING_REVALIDATION}


@dataclass
class Node:
    id: str
    kind: str
    version: str
    depends_on: list[str] = field(default_factory=list)
    validated_against: dict[str, str] = field(default_factory=dict)
    path: str | None = None
    output_sha256: str | None = None
    state: Validity = Validity.CURRENT
    content_sha256: str | None = None

    def fingerprint(self) -> str:
        return f"{self.version}@{self.content_sha256[:12]}" if self.content_sha256 else str(self.version)


class DependencyError(Exception):
    pass


class DependencyGraph:
    def __init__(self, nodes: list[Node]):
        self.nodes = {n.id: n for n in nodes}
        if len(self.nodes) != len(nodes):
            raise DependencyError("duplicate node ids in dependency graph")

    @classmethod
    def load(cls, data: dict[str, Any], root: Path | None = None) -> "DependencyGraph":
        nodes = []
        for raw in data.get("nodes", []):
            n = Node(
                id=str(raw["id"]),
                kind=str(raw.get("kind", "UNKNOWN")),
                version=str(raw.get("version", "")),
                depends_on=[str(x) for x in raw.get("depends_on", [])],
                validated_against={str(k): str(v) for k, v in (raw.get("validated_against") or {}).items()},
                path=raw.get("path"),
                output_sha256=raw.get("output_sha256"),
                state=Validity(raw.get("state", "CURRENT")),
            )
            if n.path and root is not None:
                p = contained(root, n.path)
                n.content_sha256 = sha256_file(p) if p.exists() else None
            nodes.append(n)
        return cls(nodes)

    # ------------------------------------------------------------------ structure
    def broken_refs(self) -> list[dict[str, str]]:
        out = []
        for n in self.nodes.values():
            for p in n.depends_on:
                if p not in self.nodes:
                    out.append({"node": n.id, "missing_parent": p})
            for p in n.validated_against:
                if p not in n.depends_on:
                    out.append({"node": n.id, "validated_against_non_parent": p})
            if n.path and n.content_sha256 is None:
                out.append({"node": n.id, "missing_path": n.path})
        return out

    def children(self, node_id: str) -> list[str]:
        return sorted(n.id for n in self.nodes.values() if node_id in n.depends_on)

    def descendants(self, node_id: str) -> list[str]:
        seen: list[str] = []
        q = deque(self.children(node_id))
        while q:
            c = q.popleft()
            if c in seen:
                continue
            seen.append(c)
            q.extend(self.children(c))
        return seen

    def topo_order(self) -> list[str]:
        indeg = {k: 0 for k in self.nodes}
        for n in self.nodes.values():
            for p in n.depends_on:
                if p in self.nodes:
                    indeg[n.id] += 1
        q = deque(sorted(k for k, v in indeg.items() if v == 0))
        order = []
        while q:
            k = q.popleft()
            order.append(k)
            for c in self.children(k):
                indeg[c] -= 1
                if indeg[c] == 0:
                    q.append(c)
        if len(order) != len(self.nodes):
            raise DependencyError("cycle in dependency graph")
        return order

    # ------------------------------------------------------------------ validity
    def _mark_stale(self, node_ids: Iterable[str]) -> None:
        """Propagate revalidation without erasing stronger validity findings."""
        for nid in node_ids:
            if self.nodes[nid].state not in _TERMINAL_STATES | {Validity.UNRESOLVED}:
                self.nodes[nid].state = Validity.STALE_PENDING_REVALIDATION

    def evaluate(self) -> dict[str, Any]:
        """Block publication on broken references, unusable ancestry, or drift.

        Persisted validity states matter even when fingerprints still match.
        ``stale`` lists nodes pending revalidation; ``publication_blocked`` also
        includes unresolved, invalidated, and superseded nodes. This evaluates
        the whole supplied graph: an archived superseded node remains blocked
        after its consumers move to a replacement. No publication subset is
        inferred. Evaluation never clears a prior validity finding.
        """
        order = self.topo_order()
        broken = self.broken_refs()
        for finding in broken:
            node = self.nodes[finding["node"]]
            if node.state not in _TERMINAL_STATES:
                node.state = Validity.UNRESOLVED
        direct: dict[str, list[dict[str, str]]] = {}
        for nid in order:
            n = self.nodes[nid]
            for p in n.depends_on:
                parent = self.nodes.get(p)
                if parent is None:
                    continue
                recorded = n.validated_against.get(p)
                if recorded is None:
                    direct.setdefault(nid, []).append({"parent": p, "recorded": "NONE", "current": parent.fingerprint()})
                elif recorded != parent.fingerprint():
                    direct.setdefault(nid, []).append({"parent": p, "recorded": recorded, "current": parent.fingerprint()})
        blocked = set(direct) | {nid for nid, node in self.nodes.items() if node.state in _BLOCKED_STATES}
        # A topological pass carries every blocker to all descendants, including
        # blockers loaded from a prior run rather than discovered as new drift.
        for nid in order:
            if nid in blocked:
                blocked.update(self.children(nid))
        self._mark_stale(blocked)
        stale = {nid for nid in blocked if self.nodes[nid].state == Validity.STALE_PENDING_REVALIDATION}
        return {
            "direct_drift": {k: direct[k] for k in sorted(direct)},
            "broken_refs": broken,
            "stale": sorted(stale),
            "publication_blocked": sorted(blocked),
            "states": {k: self.nodes[k].state.value for k in sorted(self.nodes)},
            "note": "Staleness is not falsity: stale nodes are pending revalidation, not declared false.",
        }

    def supersede(self, node_id: str, by: str) -> dict[str, Any]:
        """A newer node replaces this one; descendants must revalidate against the replacement."""
        if node_id not in self.nodes or by not in self.nodes:
            raise DependencyError("supersede needs two existing nodes")
        self.nodes[node_id].state = Validity.SUPERSEDED
        stale = self.descendants(node_id)
        self._mark_stale(stale)
        return {"superseded": node_id, "by": by, "descendants_marked_stale": stale}

    def invalidate(self, node_id: str, reason: str) -> dict[str, Any]:
        """Evidence showed this node is wrong. Descendants are stale (not automatically false)."""
        if node_id not in self.nodes:
            raise DependencyError(f"unknown node: {node_id}")
        self.nodes[node_id].state = Validity.INVALIDATED
        stale = self.descendants(node_id)
        self._mark_stale(stale)
        return {"invalidated": node_id, "reason": reason, "descendants_marked_stale": stale, "note": "descendants are pending revalidation, not declared false"}

    def mark_unresolved(self) -> list[str]:
        """Nodes whose parents are missing cannot be evaluated: UNRESOLVED."""
        out = sorted({b["node"] for b in self.broken_refs() if "missing_parent" in b})
        for n in out:
            if self.nodes[n].state not in _TERMINAL_STATES:
                self.nodes[n].state = Validity.UNRESOLVED
        return out

    def impact(self, node_id: str) -> dict[str, Any]:
        """Impact report for a hypothetical or actual change to ``node_id``."""
        if node_id not in self.nodes:
            raise DependencyError(f"unknown node: {node_id}")
        desc = self.descendants(node_id)
        self._mark_stale(desc)
        return {
            "changed": node_id,
            "descendants_marked_stale": desc,
            "publication_blocked": desc,
            "recomputed": [],
            "declared_false": [],
            "note": "No descendant was recomputed or declared false. Revalidate each before publication.",
        }

    def revalidate(self, node_id: str, new_output_sha256: str) -> dict[str, Any]:
        """Record a run after structural repair and with usable ancestry.

        Explicit revalidation can recover a repaired UNRESOLVED node; merely
        restoring a reference never clears it. Unchanged output clears the path
        for children; changed output leaves them pending their own revalidation.
        """
        evaluation = self.evaluate()
        n = self.nodes[node_id]
        if n.state not in (Validity.STALE_PENDING_REVALIDATION, Validity.UNRESOLVED):
            raise DependencyError(f"{node_id} is not pending revalidation (state={n.state.value})")
        structural = [finding for finding in evaluation["broken_refs"] if finding["node"] == node_id]
        if structural:
            raise DependencyError(f"{node_id} has unresolved structural errors: {structural}")
        blocked_parents = sorted(set(n.depends_on) & set(evaluation["publication_blocked"]))
        if blocked_parents:
            raise DependencyError(f"{node_id} parents not ready for revalidation: {blocked_parents}")
        for p in n.depends_on:
            n.validated_against[p] = self.nodes[p].fingerprint()
        changed = new_output_sha256 != n.output_sha256
        n.state = Validity.REVALIDATED_CHANGED if changed else Validity.REVALIDATED_UNCHANGED
        still_stale = []
        if not changed:
            # Children validated against this node's (unchanged) fingerprint: if no other parent is
            # stale, they return to CURRENT. Otherwise they remain pending.
            desc = set(self.descendants(node_id))
            for c in [x for x in self.topo_order() if x in desc]:
                cn = self.nodes[c]
                parents_ok = all(
                    p in self.nodes
                    and self.nodes[p].state in (Validity.CURRENT, Validity.REVALIDATED_UNCHANGED)
                    and cn.validated_against.get(p) == self.nodes[p].fingerprint()
                    for p in cn.depends_on
                )
                if parents_ok and cn.state == Validity.STALE_PENDING_REVALIDATION:
                    cn.state = Validity.CURRENT
                elif cn.state == Validity.STALE_PENDING_REVALIDATION:
                    still_stale.append(c)
        else:
            n.output_sha256 = new_output_sha256
            still_stale = [c for c in self.descendants(node_id) if self.nodes[c].state == Validity.STALE_PENDING_REVALIDATION]
        return {
            "node": node_id,
            "result": n.state.value,
            "output_changed": changed,
            "descendants_still_pending": still_stale,
            "states": {k: self.nodes[k].state.value for k in sorted(self.nodes)},
        }
