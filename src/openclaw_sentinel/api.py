from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from .service import SentinelService


def _json(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def handle_get(path: str, service: SentinelService) -> tuple[int, dict[str, Any]]:
    if path == "/health":
        return 200, {"status": "ok"}
    if path == "/metrics":
        return 200, service.reporting.snapshot()
    if path == "/digest":
        return 200, {"digest": service.reporting.weekly_digest()}
    return 404, {"error": "not_found"}


def handle_run_cycle(payload: dict[str, Any], service: SentinelService) -> tuple[int, dict[str, Any]]:
    cycle_id = str(payload.get("cycle_id", "api-cycle"))
    summary = service.run_cycle(cycle_id=cycle_id)
    return 200, summary.__dict__


def build_handler(service: SentinelService) -> type[BaseHTTPRequestHandler]:
    class SentinelAPIHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            status, payload = handle_get(self.path, service)
            _json(self, status, payload)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/run-cycle":
                _json(self, 404, {"error": "not_found"})
                return

            content_len = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_len) if content_len else b"{}"
            payload = json.loads(raw.decode("utf-8"))
            status, body = handle_run_cycle(payload, service)
            _json(self, status, body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return SentinelAPIHandler


def serve(service: SentinelService, host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    handler = build_handler(service)
    server = ThreadingHTTPServer((host, port), handler)
    return server


def run_server_forever(service: SentinelService, host: str = "127.0.0.1", port: int = 8080) -> None:
    server = serve(service=service, host=host, port=port)
    server.serve_forever()
