"""Local, single-job workbench. Never a generic upload, proxy or execution API."""
from __future__ import annotations

import json
import multiprocessing
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.resources import files
from typing import Any
from urllib.parse import urlsplit

from .replay import HEIGHTS, LIMITATIONS, ReplayError, provenance, validate_request

MAX_BODY_BYTES = 1024
WALL_SECONDS = 15
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}


def _worker(connection: Any, request: dict[str, Any]) -> None:
    """Fresh process isolates in-memory fault controls; no user code is loaded."""
    try:
        os.environ["OPENBLAS_NUM_THREADS"] = "1"
        os.environ["OMP_NUM_THREADS"] = "1"
        if sys.platform != "win32":
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
        from .replay import run_replay

        connection.send({"receipt": run_replay(request)})
    except Exception as exc:  # Worker errors are explicit; do not leak paths or runtime details over HTTP.
        message = str(exc) if isinstance(exc, ReplayError) else "EXECUTION_ERROR: replay did not produce a receipt."
        connection.send({"error": message})
    finally:
        connection.close()


def bounded_replay(request: Any) -> dict[str, Any]:
    selected = validate_request(request)
    context = multiprocessing.get_context("spawn")
    read, write = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(write, selected), daemon=True)
    try:
        process.start()
        write.close()
        if not read.poll(WALL_SECONDS):
            raise ReplayError("TIME_LIMIT: replay exceeded the 15 second wall-clock budget.")
        try:
            result = read.recv()
        except EOFError as exc:
            raise ReplayError("WORKER_EXITED: replay stopped without a receipt (including resource-limit exits).") from exc
        if "error" in result:
            raise ReplayError(result["error"])
        return result["receipt"]
    finally:
        read.close()
        write.close()
        if process.pid is not None:
            process.join(timeout=0.5)
            if process.is_alive():
                process.terminate()
                process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
            process.close()


def strict_request(body: bytes) -> dict[str, Any]:
    if len(body) > MAX_BODY_BYTES:
        raise ValueError("Request exceeds 1024 bytes.")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON keys are refused.")
            result[key] = value
        return result

    def reject_constant(_: str) -> None:
        raise ValueError("Non-finite JSON numbers are refused.")

    try:
        value = json.loads(body.decode("utf-8"), object_pairs_hook=pairs, parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("A valid UTF-8 JSON preset object is required.") from exc
    return validate_request(value)


def metadata() -> dict[str, Any]:
    return {"source": provenance(), "amplitude_presets_uM": list(HEIGHTS),
            "kinetics": ["linear", "nonlinear"], "meshes": [16, 32, 64, 128],
            "max_request_bytes": MAX_BODY_BYTES, "wall_limit_seconds": WALL_SECONDS,
            "limits": LIMITATIONS, "provider": "Local pinned upstream function excerpts; no model or MCP connection."}


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "SZLEvidenceWorkbench/1"
    sys_version = ""
    protocol_version = "HTTP/1.0"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, fmt: str, *args: Any) -> None:
        # No query strings, payloads or user-supplied request text in logs.
        pass

    def _respond(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, data: Any) -> None:
        self._respond(status, json.dumps(data, allow_nan=False).encode(), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path == "/api/openislet/meta":
            self._json(200, metadata())
        elif self.path in STATIC:
            name, mime = STATIC[self.path]
            self._respond(200, files(__package__).joinpath("static", name).read_bytes(), mime)
        else:
            self._json(404, {"error": "NOT_FOUND: only the workbench and its fixed API paths are served."})

    def do_POST(self) -> None:
        if self.path != "/api/openislet/replay":
            self._json(404, {"error": "NOT_FOUND"})
            return
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        # No CORS, credentials or sessions. Browser requests must be same origin.
        try:
            origin_ok = not origin or (urlsplit(origin).netloc == host and urlsplit(origin).scheme in ("http", "https"))
        except ValueError:
            origin_ok = False
        if not origin_ok:
            self._json(403, {"error": "ORIGIN_REFUSED: cross-origin replay is not allowed."})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get("Transfer-Encoding") or len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdecimal():
            self._json(400, {"error": "FRAMING_REFUSED: one Content-Length, no Transfer-Encoding required."})
            return
        if len(lengths[0]) > 4:
            self._json(413, {"error": "BODY_LIMIT: request must be between 1 and 1024 bytes."})
            return
        length = int(lengths[0])
        if not 0 < length <= MAX_BODY_BYTES:
            self._json(413, {"error": "BODY_LIMIT: request must be between 1 and 1024 bytes."})
            return
        if self.headers.get_content_type() != "application/json":
            self._json(415, {"error": "CONTENT_TYPE: application/json is required."})
            return
        try:
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("Request body was truncated.")
            selected = strict_request(body)
            self._json(200, bounded_replay(selected))
        except (ValueError, TimeoutError) as exc:
            self._json(400, {"error": str(exc)})
        except ReplayError as exc:
            self._json(503, {"error": str(exc)})


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    with HTTPServer((host, port), WorkbenchHandler) as server:
        server.request_queue_size = 4
        print(f"OpenIslet evidence workbench: http://{host}:{server.server_port}", flush=True)
        print("Research software verification only. No patient data or external providers.", flush=True)
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            # Ctrl-C is a normal local shutdown; the context manager closes the listener.
            pass


def cmd_workbench(args: Any) -> int:
    serve(args.host, args.port)
    return 0


def cmd_replay(args: Any) -> int:
    try:
        receipt = bounded_replay({"amplitude_uM": args.amplitude_um, "kinetics": args.kinetics})
    except ReplayError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}))
        return 3
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if receipt["status"] == "PASS" else 1
