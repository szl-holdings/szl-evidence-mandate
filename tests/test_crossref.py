"""Crossref responses are external evidence; malformed metadata is unavailable."""

from __future__ import annotations

import json

import httpx
import pytest

from szl_evidence.adapters.citations import CrossrefResolver, Resolution
from szl_evidence.verifier import verify


@pytest.mark.parametrize("body", [
    b"{not json",
    b"\xff",
    b"null",
    b"[]",
    b"{}",
    b'{"message": null}',
    b'{"message": []}',
    b'{"message": {"author": null}}',
    b'{"message": {"author": "Smith"}}',
    b'{"message": {"author": [null]}}',
    b'{"message": {"author": [{"family": []}]}}',
    b'{"message": {"issued": []}}',
    b'{"message": {"issued": "2026"}}',
    b'{"message": {"issued": {"date-parts": "2026"}}}',
    b'{"message": {"issued": {"date-parts": 0}}}',
    b'{"message": {"issued": {"date-parts": [[]]}}}',
    b'{"message": {"issued": {"date-parts": [null]}}}',
    b'{"message": {"issued": {"date-parts": ["2026"]}}}',
    b'{"message": {"issued": {"date-parts": [["2026"]]}}}',
    b'{"message": {"issued": {"date-parts": [[true]]}}}',
])
def test_malformed_success_response_is_unavailable(body):
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=body))) as client:
        result = CrossrefResolver(client=client).resolve("10.5555/synthetic")
    assert result == Resolution("UNAVAILABLE", detail="invalid crossref response")


@pytest.mark.parametrize(("message", "expected"), [
    ({"author": [{"family": "Smith"}, {"family": "Jones"}],
      "issued": {"date-parts": [[2026, 11, 1]]}}, Resolution("FOUND", ["Smith", "Jones"], 2026)),
    ({}, Resolution("FOUND")),
    ({"author": [{}], "issued": None}, Resolution("FOUND", [""])),
    ({"issued": {"date-parts": []}}, Resolution("FOUND")),
    ({"issued": {"date-parts": None}}, Resolution("FOUND")),
    ({"issued": {"date-parts": [[None]]}}, Resolution("FOUND")),
])
def test_valid_response_preserves_metadata_and_optional_defaults(message, expected):
    def respond(request):
        assert str(request.url) == "https://api.crossref.org/works/10.5555/synthetic"
        return httpx.Response(200, json={"message": message})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert CrossrefResolver(client=client).resolve(" 10.5555/synthetic ") == expected


@pytest.mark.parametrize(("status", "expected"), [
    (404, Resolution("NOT_FOUND", detail="crossref 404")),
    (503, Resolution("UNAVAILABLE", detail="http 503")),
])
def test_http_status_is_preserved_without_parsing_error_body(status, expected):
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, content=b"invalid"))) as client:
        assert CrossrefResolver(client=client).resolve("10.5555/synthetic") == expected


@pytest.mark.parametrize("body", [b"{not json", json.dumps({"message": {"author": [None]}}).encode()])
def test_malformed_success_response_abstains_in_verifier(valid, body):
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=body))) as client:
        receipt = verify(valid, resolver=CrossrefResolver(client=client))
    invocation = next(item for item in receipt["invocations"] if item["check"] == "citation_metadata")
    assert invocation["result"]["status"] == "ABSTAIN"
    assert invocation["result"]["reason"] == "SOURCE_UNAVAILABLE"
    assert receipt["status"] == "ABSTAIN"
    assert receipt["exit_code"] == 2
