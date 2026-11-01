"""DOI resolvers. Offline (closed-world snapshot) and Crossref (network).

A network failure yields UNAVAILABLE, which checks map to ABSTAIN/SOURCE_UNAVAILABLE.
It is never treated as evidence that a DOI does not exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Resolution:
    state: str  # FOUND | NOT_FOUND | UNAVAILABLE
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    detail: str = ""


class CitationResolver:
    def configure(self, ctx: Any, section: dict[str, Any]) -> None:  # pragma: no cover - interface
        pass

    def resolve(self, doi: str) -> Resolution:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> dict[str, Any]:
        return {"resolver": self.__class__.__name__}


class OfflineResolver(CitationResolver):
    """Resolves against a registry snapshot declared in the manifest.

    Absence means NOT_FOUND only if the snapshot declares itself closed-world; otherwise
    absence is UNAVAILABLE (we cannot tell).
    """

    def __init__(self) -> None:
        self.records: dict[str, Any] = {}
        self.closed_world = False
        self.meta: dict[str, Any] = {}

    def configure(self, ctx: Any, section: dict[str, Any]) -> None:
        reg = ctx.data(section.get("registry", "")) or {}
        self.records = {k.lower(): v for k, v in (reg.get("records") or {}).items()}
        self.closed_world = bool(reg.get("closed_world"))
        self.meta = {k: reg.get(k) for k in ("source", "retrieved_at", "closed_world")}

    def resolve(self, doi: str) -> Resolution:
        rec = self.records.get(doi.strip().lower())
        if rec is None:
            return Resolution("NOT_FOUND" if self.closed_world else "UNAVAILABLE", detail="not in snapshot")
        return Resolution("FOUND", list(rec.get("authors", [])), rec.get("year"))

    def describe(self) -> dict[str, Any]:
        return {"resolver": "offline-snapshot", **self.meta}


class CrossrefResolver(CitationResolver):
    """Live Crossref lookup. 404 -> NOT_FOUND; HTTP, transport or response errors -> UNAVAILABLE."""

    def __init__(self, client: Any = None, base: str = "https://api.crossref.org/works/"):
        self.client = client
        self.base = base

    def resolve(self, doi: str) -> Resolution:
        import httpx

        client = self.client or httpx.Client(timeout=15, headers={"User-Agent": "szl-evidence-mandate/0.1"})
        try:
            r = client.get(self.base + doi.strip())
        except httpx.HTTPError as e:
            return Resolution("UNAVAILABLE", detail=f"transport: {e.__class__.__name__}")
        if r.status_code == 404:
            return Resolution("NOT_FOUND", detail="crossref 404")
        if r.status_code != 200:
            return Resolution("UNAVAILABLE", detail=f"http {r.status_code}")
        # Never turn an unusable success body into evidence that the DOI is absent.
        # Keep the detail bounded and independent of the upstream response body.
        unavailable = Resolution("UNAVAILABLE", detail="invalid crossref response")
        try:
            payload = r.json()
        except ValueError:
            return unavailable
        if not isinstance(payload, dict) or not isinstance(payload.get("message"), dict):
            return unavailable
        msg = payload["message"]
        authors = msg.get("author", [])
        if not isinstance(authors, list) or any(
            not isinstance(author, dict) or not isinstance(author.get("family", ""), str)
            for author in authors
        ):
            return unavailable
        issued = msg.get("issued")
        if issued is None:
            issued = {}
        if not isinstance(issued, dict):
            return unavailable
        parts = issued.get("date-parts")
        if parts is None:
            parts = []
        if not isinstance(parts, list):
            return unavailable
        year = None
        if parts:
            if not isinstance(parts[0], list) or not parts[0]:
                return unavailable
            year = parts[0][0]
            if year is not None and type(year) is not int:
                return unavailable
        return Resolution("FOUND", [author.get("family", "") for author in authors], year)

    def describe(self) -> dict[str, Any]:
        return {"resolver": "crossref", "base": self.base}
