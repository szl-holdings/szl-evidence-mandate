"""An HTTP success is not proof that an audit listing is complete."""

import httpx
import pytest

from szl_evidence.adapters.http import CachedClient, paginate


def collect_second_page(body):
    requested = []

    def handler(request):
        requested.append(str(request.url))
        if len(requested) == 1:
            return httpx.Response(200, json=[{"id": 1}], headers={
                "link": '<https://api.example/items?page=2>; rel="next"',
            })
        return httpx.Response(200, content=body, headers={
            "link": '<https://api.example/items?page=3>; rel="next"',
        })

    client = CachedClient(None, transport=httpx.MockTransport(handler), max_retries=0)
    try:
        items, meta = paginate(client, "https://api.example/items")
    finally:
        client.close()
    return items, meta, requested


@pytest.mark.parametrize("body", [
    b'{"message":"unexpected response"}', b'{}', b'"not a list"', b'null',
    b'false', b'7', b'{"items":null}', b'{"items":{}}', b'{"items":"wrong"}',
])
def test_unexpected_page_shape_never_counts_keys_or_characters(body):
    items, meta, requested = collect_second_page(body)
    assert items == [{"id": 1}]
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert meta["pages"] == 2
    assert "page 2" in meta["detail"]
    assert len(requested) == 2


@pytest.mark.parametrize("body", [b'{"message":"unexpected response"}', b'{}', b'"abc"'])
def test_terminal_invalid_page_never_reports_observed_denominator(body):
    client = CachedClient(None, transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=body)), max_retries=0)
    try:
        items, meta = paginate(client, "https://api.example/items")
    finally:
        client.close()
    assert items == []
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert meta["pages"] == 1


@pytest.mark.parametrize("body", [b'{', b'[] trailing text', b'\xff', b'[' * 10000 + b']' * 10000])
def test_malformed_json_keeps_prior_evidence_without_raising(body):
    items, meta, requested = collect_second_page(body)
    assert items == [{"id": 1}]
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert "invalid JSON" in meta["detail"]
    assert "page 2" in meta["detail"]
    assert len(requested) == 2


@pytest.mark.parametrize("payload", [[], [{"id": 2}], {"items": []}, {"items": [{"id": 2}]}])
def test_complete_list_and_items_envelope_keep_observed_coverage(payload):
    client = CachedClient(None, transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload)), max_retries=0)
    try:
        items, meta = paginate(client, "https://api.example/items")
    finally:
        client.close()
    assert items == (payload["items"] if isinstance(payload, dict) else payload)
    assert meta["denominator_state"] == "OBSERVED"
    assert meta["pages"] == 1


def test_provider_reported_incomplete_results_are_not_complete_evidence():
    items, meta, requested = collect_second_page(
        b'{"items":[{"id":2}],"incomplete_results":true}')
    assert items == [{"id": 1}, {"id": 2}]
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert "incomplete" in meta["detail"]
    assert len(requested) == 2


@pytest.mark.parametrize("body", [
    b'["garbage"]', b'[null]', b'[7]', b'[false]', b'[[]]',
    b'[{"id":2}, "garbage"]', b'{"items":[{"id":2}, null]}',
])
def test_malformed_items_reject_entire_page_and_preserve_prior_evidence(body):
    items, meta, requested = collect_second_page(body)
    assert items == [{"id": 1}]
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert "page 2" in meta["detail"]
    assert len(requested) == 2


@pytest.mark.parametrize("flag", [b'null', b'"false"', b'"true"', b'0', b'1', b'[]', b'{}'])
def test_malformed_completeness_flag_rejects_page(flag):
    items, meta, requested = collect_second_page(
        b'{"items":[{"id":2}],"incomplete_results":' + flag + b'}')
    assert items == [{"id": 1}]
    assert meta["denominator_state"] == "UNAVAILABLE"
    assert "incomplete_results" in meta["detail"]
    assert len(requested) == 2


def test_explicit_complete_results_flag_keeps_observed_coverage():
    client = CachedClient(None, transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={
            "items": [{"id": 2}], "incomplete_results": False})), max_retries=0)
    try:
        items, meta = paginate(client, "https://api.example/items")
    finally:
        client.close()
    assert items == [{"id": 2}]
    assert meta["denominator_state"] == "OBSERVED"
