"""Cached, rate-limit-aware, read-only HTTP client.

Every response is written to ``raw/`` with its retrieval timestamp and body hash.
Credentials are sent in headers only and never written to the cache or logs.
A transport error or rate-limit response is SOURCE_UNAVAILABLE - never evidence of a defect.
"""

from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx

from ..models import sha256_bytes, sha256_json, utcnow
from ..safety import redact

SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"


@dataclass
class Response:
    url: str
    status: int | str  # int, or "SOURCE_UNAVAILABLE"
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    retrieved_at: str = ""
    body_sha256: str = ""
    elapsed_ms: float | None = None
    detail: str = ""

    @property
    def ok(self) -> bool:
        return isinstance(self.status, int) and 200 <= self.status < 300

    @property
    def unavailable(self) -> bool:
        return self.status == SOURCE_UNAVAILABLE

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", "replace")


class CachedClient:
    def __init__(
        self,
        cache_dir: Path | None,
        headers: dict[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
        min_interval: float = 0.0,
        timeout: float = 30.0,
        max_retries: int = 2,
        surface: str = "http",
    ):
        self.cache_dir = cache_dir
        self.surface = surface
        self._client = httpx.Client(
            headers={"User-Agent": "szl-evidence-mandate/0.1 (read-only audit)", **(headers or {})},
            transport=transport,
            timeout=timeout,
            follow_redirects=True,
        )
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._last = 0.0
        self._lock = threading.Lock()
        self.requests = 0
        self.unavailable = 0

    def close(self) -> None:
        self._client.close()

    def _throttle(self) -> None:
        with self._lock:
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def request(self, method: str, url: str, params: dict[str, Any] | None = None, json_body: Any = None, headers: dict[str, str] | None = None, cache: bool = True, max_bytes: int | None = None) -> Response:
        full = url + (("&" if "?" in url else "?") + urlencode(params) if params else "")
        attempt = 0
        while True:
            attempt += 1
            self._throttle()
            t0 = time.perf_counter()
            try:
                with self._client.stream(method, full, json=json_body, headers=headers) as r:
                    chunks = []
                    size = 0
                    for c in r.iter_bytes():
                        chunks.append(c)
                        size += len(c)
                        if max_bytes and size >= max_bytes:
                            break
                    body = b"".join(chunks)
                    if max_bytes:
                        body = body[:max_bytes]
                    resp = Response(full, r.status_code, body, {k.lower(): v for k, v in r.headers.items()}, utcnow(), sha256_bytes(body), round((time.perf_counter() - t0) * 1000, 1))
            except httpx.HTTPError as e:
                resp = Response(full, SOURCE_UNAVAILABLE, b"", {}, utcnow(), "", None, f"transport: {e.__class__.__name__}")
            self.requests += 1
            if self._is_rate_limited(resp):
                reset = resp.headers.get("x-ratelimit-reset") or resp.headers.get("retry-after")
                if attempt <= self.max_retries and resp.headers.get("retry-after", "").isdigit() and int(resp.headers["retry-after"]) <= 30:
                    time.sleep(int(resp.headers["retry-after"]))
                    continue
                resp = Response(full, SOURCE_UNAVAILABLE, b"", resp.headers, resp.retrieved_at, "", resp.elapsed_ms, f"rate limited (http {resp.status}); reset={reset}")
            elif isinstance(resp.status, int) and resp.status >= 500 and attempt <= self.max_retries:
                time.sleep(1.5 * attempt)
                continue
            elif resp.status == SOURCE_UNAVAILABLE and attempt <= self.max_retries:
                time.sleep(1.0 * attempt)
                continue
            break
        if resp.unavailable:
            self.unavailable += 1
        if cache and self.cache_dir is not None:
            self._store(method, resp, json_body)
        return resp

    def get(self, url: str, params: dict[str, Any] | None = None, **kw: Any) -> Response:
        return self.request("GET", url, params=params, **kw)

    @staticmethod
    def _is_rate_limited(r: Response) -> bool:
        if r.status == 429:
            return True
        if r.status == 403 and (r.headers.get("x-ratelimit-remaining") == "0" or b"rate limit" in r.body[:500].lower()):
            return True
        return False

    def _store(self, method: str, r: Response, json_body: Any) -> None:
        assert self.cache_dir is not None
        key = sha256_json([method, redact(r.url), json_body])[:32]
        d = self.cache_dir / self.surface
        d.mkdir(parents=True, exist_ok=True)
        keep_headers = {k: v for k, v in r.headers.items() if k in {"content-type", "etag", "last-modified", "link", "x-ratelimit-remaining", "x-ratelimit-reset", "x-github-request-id"}}
        rec = {
            "method": method,
            "url": redact(r.url),
            "request_body_sha256": sha256_json(json_body) if json_body is not None else None,
            "status": r.status,
            "retrieved_at": r.retrieved_at,
            "body_sha256": r.body_sha256,
            "elapsed_ms": r.elapsed_ms,
            "headers": keep_headers,
            "detail": r.detail,
            "body": redact(r.body.decode("utf-8", "replace")) if len(r.body) < 2_000_000 else f"<{len(r.body)} bytes omitted>",
        }
        (d / f"{key}.json").write_text(json.dumps(rec, sort_keys=True, ensure_ascii=False), encoding="utf-8")


_LINK_NEXT = re.compile(r'<([^>]+)>;\s*rel="next"')


def next_link(r: Response) -> str | None:
    m = _LINK_NEXT.search(r.headers.get("link", ""))
    return m.group(1) if m else None


def paginate(client: CachedClient, url: str, params: dict[str, Any] | None = None, max_pages: int = 100) -> tuple[list[Any], dict[str, Any]]:
    """Follow rel=next links until exhausted. Returns (items, meta). Never silently truncates:
    an unavailable page makes the denominator UNAVAILABLE."""
    items: list[Any] = []
    pages = 0
    nxt: str | None = url
    p = params
    state = "OBSERVED"
    detail = ""
    while nxt:
        r = client.get(nxt, params=p)
        p = None
        pages += 1
        if not r.ok:
            state = "UNAVAILABLE"
            detail = f"page {pages}: {r.status} {r.detail}"
            break
        data = r.json()
        if isinstance(data, dict) and "items" in data:
            data = data["items"]
        items.extend(data)
        nxt = next_link(r)
        if pages >= max_pages and nxt:
            state = "UNAVAILABLE"
            detail = f"stopped at max_pages={max_pages} with more pages remaining"
            break
    return items, {"pages": pages, "denominator_state": state, "detail": detail, "retrieved_at": utcnow()}
