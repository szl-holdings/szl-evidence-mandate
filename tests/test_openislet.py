"""Real pinned-function replay; synthetic inputs are mathematical test fields."""
from __future__ import annotations

import ast
import hashlib
import inspect
import io
import json
from email.message import Message
from importlib.resources import files
from unittest.mock import patch

import pytest

from szl_evidence.cli import build_parser
from szl_evidence.openislet import replay, server
from szl_evidence.receipts import receipt_hash


@pytest.mark.parametrize("height", replay.HEIGHTS)
@pytest.mark.parametrize("kinetics", ("linear", "nonlinear"))
def test_actual_solver_refinement_and_faults(height, kinetics):
    pytest.importorskip("numpy")
    result = replay.run_replay({"amplitude_uM": height, "kinetics": kinetics})
    p = result["payload"]
    assert result["status"] == "PASS"
    assert result["signature_state"] == "UNSIGNED"
    assert "signature" not in result
    assert result["receipt_sha256"] == receipt_hash(result)
    assert p["source"]["revision"] == replay.PIN
    assert p["input_class"] == "SYNTHETIC_MANUFACTURED_SOLUTION"
    assert p["biological_validation"] is False
    assert all(p["checks"].values())
    assert len(p["mesh_results"]) == 4
    assert len(p["finest_profile"]) == 127
    assert len(p["negative_controls"]) == 2
    assert all(1.9 < n < 2.1 for n in p["observed_orders"])
    assert all(c["relative_linf_error"] > .001 for c in p["negative_controls"])
    assert p["mesh_results"][-1]["relative_linf_error"] < 1e-4
    # Immutable analytical oracle, not values copied from the solver.
    assert p["parameters"]["diffusion_cm2_s"] == 1.4e-5
    assert p["reference"]["boundaries"] == "H(0) = H(L) = 0 uM"
    text = json.dumps(result, allow_nan=False)
    assert receipt_hash(json.loads(text)) == result["receipt_sha256"]


def test_source_binding_and_fail_closed():
    pytest.importorskip("numpy")
    from szl_evidence.openislet.vendor import peroxide

    record = replay._verify_source(peroxide)
    assert record["license"] == "Apache-2.0"
    with patch.object(peroxide, "D_H2O2_HYDROGEL_CM2_S", 2.8e-5), pytest.raises(replay.ReplayError, match="SOURCE_MISMATCH"):
        replay.run_replay({})
    with patch.object(replay.inspect, "getsource", return_value="def changed(): pass\n"), pytest.raises(replay.ReplayError, match="SOURCE_MISMATCH"):
        replay.run_replay({})
    for name, digest in record["function_sha256"].items():
        assert hashlib.sha256(inspect.getsource(getattr(peroxide, name)).encode()).hexdigest() == digest


def test_fault_mutations_restored():
    pytest.importorskip("numpy")
    from szl_evidence.openislet.vendor import peroxide

    replay.run_replay({})
    assert peroxide.D_H2O2_HYDROGEL_CM2_S == replay.DIFFUSION_CM2_S


@pytest.mark.parametrize("value", [
    None, [], "", 1, {"amplitude_uM": True}, {"amplitude_uM": 0}, {"amplitude_uM": 1e300},
    {"amplitude_uM": float("nan")}, {"amplitude_uM": float("inf")}, {"amplitude_uM": "25000"},
    {"kinetics": []}, {"kinetics": "medical"}, {"url": "https://example.com"},
    {"source": "/etc/passwd"}, {"command": "echo unsafe"}, {"meshes": [1000000000]},
    {"kinetics": None}, {"amplitude_uM": -1}, {"amplitude_uM": 10**900},
])
def test_closed_input_contract(value):
    with pytest.raises(ValueError):
        replay.validate_request(value)


@pytest.mark.parametrize("value", [
    b'{"amplitude_uM":NaN}', b'{"amplitude_uM":Infinity}', b'{"amplitude_uM":1e309}',
    b'{"kinetics":"linear","kinetics":"nonlinear"}', b'\xff', b'{', b"[]" ,
    b"x" * 1025, b"[" * 1000, "{}".encode("utf-16"),
])
def test_strict_json(value):
    with pytest.raises(ValueError):
        server.strict_request(value)


def test_default_request():
    assert server.strict_request(b"{}") == {"amplitude_uM": 25000.0, "kinetics": "nonlinear"}


def test_spawn_worker_real_solver():
    pytest.importorskip("numpy")
    result = server.bounded_replay({"amplitude_uM": 25000, "kinetics": "nonlinear"})
    assert result["status"] == "PASS"
    assert result["receipt_sha256"] == receipt_hash(result)


@pytest.mark.parametrize("outcome", ["timeout", "eof", "worker_error"])
def test_worker_failure_is_explicit_and_process_is_closed(outcome):
    class FakePipe:
        def __init__(self):
            self.closed = False

        def poll(self, timeout):
            return outcome != "timeout"

        def recv(self):
            if outcome == "eof":
                raise EOFError
            return {"error": "DEPENDENCY_UNAVAILABLE"}

        def close(self):
            self.closed = True

    class FakeProcess:
        pid = 123

        def __init__(self):
            self.live = True
            self.closed = False

        def start(self):
            pass

        def join(self, timeout):
            pass

        def is_alive(self):
            return self.live

        def terminate(self):
            self.live = False

        def close(self):
            self.closed = True

    read, write, process = FakePipe(), FakePipe(), FakeProcess()

    class Context:
        def Pipe(self, duplex):
            return read, write

        def Process(self, **kwargs):
            return process

    with patch.object(server.multiprocessing, "get_context", return_value=Context()):
        with pytest.raises(replay.ReplayError):
            server.bounded_replay({})
    assert read.closed and write.closed and process.closed and not process.live


def handler(path, headers=None, body=b""):
    """Exercise real request handlers without binding ports or starting the app."""
    obj = object.__new__(server.WorkbenchHandler)
    obj.path = path
    obj.headers = Message()
    for key, value in headers or []:
        obj.headers[key] = value
    obj.rfile = io.BytesIO(body)
    obj.wfile = io.BytesIO()
    obj.status = None
    obj.response_headers = {}
    obj.send_response = lambda status: setattr(obj, "status", status)
    obj.send_header = lambda key, value: obj.response_headers.__setitem__(key, value)
    obj.end_headers = lambda: None
    return obj


@pytest.mark.parametrize("path", ["/etc/passwd", "/../pyproject.toml", "/api/openislet/meta?url=x", "/vendor/peroxide.py"])
def test_no_arbitrary_files(path):
    obj = handler(path)
    obj.do_GET()
    assert obj.status == 404


def test_package_assets_and_headers():
    for path in ["/", "/app.js", "/style.css", "/api/openislet/meta"]:
        obj = handler(path)
        obj.do_GET()
        assert obj.status == 200
        assert obj.wfile.getvalue()
        assert obj.response_headers["X-Content-Type-Options"] == "nosniff"
        assert "script-src 'self'" in obj.response_headers["Content-Security-Policy"]
    assert "Apache-2.0" in files("szl_evidence.openislet").joinpath("vendor/NOTICE.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("headers,status", [
    ([], 400),
    ([("Content-Length", "2"), ("Content-Length", "2")], 400),
    ([("Content-Length", "-1")], 400),
    ([("Content-Length", "10000")], 413),
    ([("Content-Length", "9" * 5000)], 413),
    ([("Content-Length", "2"), ("Transfer-Encoding", "chunked")], 400),
    ([("Content-Length", "2"), ("Content-Type", "text/plain")], 415),
    ([("Content-Length", "2"), ("Origin", "https://untrusted.test"), ("Host", "local")], 403),
])
def test_http_framing_and_origin(headers, status):
    obj = handler("/api/openislet/replay", headers, b"{}")
    obj.do_POST()
    assert obj.status == status
    assert "error" in json.loads(obj.wfile.getvalue())

def test_huge_json_integer_is_a_bounded_validation_error():
    raw = json.dumps({"amplitude_uM": 10**900, "kinetics": "nonlinear"}).encode()
    assert len(raw) <= server.MAX_BODY_BYTES
    obj = handler("/api/openislet/replay", [
        ("Content-Length", str(len(raw))), ("Content-Type", "application/json"),
    ], raw)
    obj.do_POST()
    assert obj.status == 400
    assert "synthetic presets" in json.loads(obj.wfile.getvalue())["error"]


def test_endpoint_exact_bytes_and_explicit_error():
    pytest.importorskip("numpy")
    raw = b'{"amplitude_uM":1,"kinetics":"linear"}'
    headers = [("Content-Length", str(len(raw))), ("Content-Type", "application/json"),
               ("Origin", "https://preview.test"), ("Host", "preview.test")]
    receipt = replay.run_replay({"amplitude_uM": 1, "kinetics": "linear"})
    obj = handler("/api/openislet/replay", headers, raw)
    with patch.object(server, "bounded_replay", return_value=receipt):
        obj.do_POST()
    assert obj.status == 200
    assert obj.wfile.getvalue() == json.dumps(receipt, allow_nan=False).encode()
    with patch.object(server, "bounded_replay", side_effect=replay.ReplayError("TIME_LIMIT")):
        obj = handler("/api/openislet/replay", headers, raw)
        obj.do_POST()
    assert obj.status == 503
    assert json.loads(obj.wfile.getvalue()) == {"error": "TIME_LIMIT"}


def test_receipt_tamper_and_static_no_reconstruction():
    pytest.importorskip("numpy")
    result = replay.run_replay({})
    result["payload"]["mesh_results"][0]["relative_linf_error"] = 0.0
    assert result["receipt_sha256"] != receipt_hash(result)
    script = files("szl_evidence.openislet").joinpath("static/app.js").read_text(encoding="utf-8")
    assert "new Blob([receiptBytes]" in script
    assert "JSON.stringify(receipt" not in script
    assert ".innerHTML" not in script
    # Preview access is browser-managed even though this app has no login.
    assert 'credentials: "omit"' not in script
    assert script.count('credentials: "same-origin"') == 2


def test_cli_compatibility_and_optional_import():
    parser = build_parser()
    assert parser.parse_args(["engine", "verify", "fixtures/valid"]).ecmd == "verify"
    assert parser.parse_args(["openislet", "replay"]).kinetics == "nonlinear"
    assert parser.parse_args(["openislet", "workbench"]).host == "127.0.0.1"
    with pytest.raises(SystemExit):
        parser.parse_args(["openislet", "replay", "--amplitude-um", "nan"])
    tree = ast.parse(inspect.getsource(server))
    assert not any(isinstance(n, ast.Import) and any(a.name == "numpy" for a in n.names) for n in tree.body)
