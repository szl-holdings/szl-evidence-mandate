"""CWE-312 regression: secret-scanning alert values must never be requested or cached.

GitHub's /repos/{owner}/{repo}/secret-scanning/alerts returns each alert's leaked credential in
``secret`` unless the request sets ``hide_secret=true``, and CachedClient writes response bodies to
``raw/``. The sentinel is generated at runtime and matches none of the redaction formats in
``safety.redact``, so only the request flag and the cache scrub can keep it out.
"""

from __future__ import annotations

import json
import secrets

import httpx

from szl_evidence.adapters.http import SECRET_BODY_WITHHELD, CachedClient, scrub_secret_members
from szl_evidence.audit.github import GitHubCollector
from szl_evidence.safety import redact


def _sentinel() -> str:
    return "szl-sentinel-" + secrets.token_hex(16)


def _cached_text(cache_dir) -> str:
    return "".join(p.read_text(encoding="utf-8") for p in sorted(cache_dir.rglob("*.json")))


def test_secret_scanning_alerts_hide_secret_and_never_reach_the_cache(tmp_path):
    sentinel = _sentinel()
    assert redact(sentinel) == sentinel  # redaction alone would not have caught it
    queries: list[dict[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/repos/o/r/secret-scanning/alerts":
            queries.append(dict(request.url.params))
            # A server that ignores hide_secret: the cache must still drop the member.
            return httpx.Response(200, json=[{"number": 1, "state": "open", "secret_type": "npm_access_token", "secret": sentinel}])
        return httpx.Response(404, json={"message": "Not Found"})

    client = CachedClient(tmp_path, transport=httpx.MockTransport(handler), max_retries=0, surface="github")
    try:
        detail = GitHubCollector(client, "o", authenticated=False).repo_detail({"full_name": "o/r", "name": "r", "default_branch": "main"})
    finally:
        client.close()

    assert queries == [{"state": "open", "per_page": "100", "hide_secret": "true"}]
    assert detail["secret_scanning_alerts"] == {"open": 1, "lower_bound": False, "types": ["npm_access_token"]}
    assert sentinel not in json.dumps(detail)
    assert sentinel not in _cached_text(tmp_path)
    records = [json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "github").glob("*.json")]
    alert_records = [r for r in records if "/secret-scanning/alerts" in r["url"]]
    assert len(alert_records) == 1
    assert alert_records[0]["body_secret_members_removed"] == 1
    assert json.loads(alert_records[0]["body"]) == [{"number": 1, "state": "open", "secret_type": "npm_access_token"}]


def test_scrub_removes_secret_members_at_any_depth_and_keeps_the_rest():
    s1, s2 = _sentinel(), _sentinel()
    body = json.dumps({"items": [{"secret": s1, "secret_type": "t"}], "nested": {"deeper": [{"Secret": s2, "n": 2}]}})
    text, removed = scrub_secret_members(body)
    assert removed == 2 and s1 not in text and s2 not in text
    assert json.loads(text) == {"items": [{"secret_type": "t"}], "nested": {"deeper": [{"n": 2}]}}


def test_scrub_leaves_bodies_without_secret_members_byte_identical():
    for body in ['{"message":"Not Found"}', '[{"secret_type":"x","secret_type_display_name":"X"}]',
                 '{"note":"\\"secret\\": \\"in a string value\\""}', "<html>not json</html>", "", "[" * 10_000 + "]" * 10_000]:
        assert scrub_secret_members(body) == (body, 0), body[:40]


def test_unparseable_body_naming_a_secret_member_is_withheld(tmp_path):
    sentinel = _sentinel()
    truncated = '[{"secret_type":"t","secret": "' + sentinel  # e.g. a body cut off mid-stream
    assert scrub_secret_members(truncated) == (SECRET_BODY_WITHHELD, 1)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=truncated.encode())

    client = CachedClient(tmp_path, transport=httpx.MockTransport(handler), max_retries=0, surface="t")
    try:
        client.get("https://api.example/x")
    finally:
        client.close()
    assert sentinel not in _cached_text(tmp_path)
    (record,) = [json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "t").glob("*.json")]
    assert record["body"] == SECRET_BODY_WITHHELD and record["body_secret_members_removed"] == 1
