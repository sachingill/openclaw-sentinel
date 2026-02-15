from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from .rate_limit import SlidingWindowRateLimiter
from .service import SentinelService
from .webhooks import WebhookConfig, process_webhook


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


def handle_webhook(
    path: str,
    headers: dict[str, str],
    raw_body: bytes,
    service: SentinelService,
    webhook_cfg: WebhookConfig,
    limiter: SlidingWindowRateLimiter,
) -> tuple[int, dict[str, Any]]:
    parts = [p for p in path.split("/") if p]
    if len(parts) != 2 or parts[0] != "webhook":
        return 404, {"error": "not_found"}

    source = parts[1].lower()
    identity = headers.get("x-forwarded-for", headers.get("x-real-ip", "unknown"))
    rate_key = f"{source}:{identity}"
    if not limiter.allow(rate_key):
        return 429, {"error": "rate_limited"}

    try:
        incident = process_webhook(source=source, headers=headers, raw_body=raw_body, cfg=webhook_cfg)
    except PermissionError:
        return 401, {"error": "unauthorized"}
    except (ValueError, json.JSONDecodeError):
        return 400, {"error": "bad_request"}

    cycle_id = f"webhook-{source}-{incident.id}"
    summary = service.run_incident(cycle_id=cycle_id, incident=incident)
    return 202, summary.__dict__


def build_handler(
    service: SentinelService,
    webhook_cfg: WebhookConfig,
    limiter: SlidingWindowRateLimiter,
) -> type[BaseHTTPRequestHandler]:
    class SentinelAPIHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            status, payload = handle_get(self.path, service)
            _json(self, status, payload)

        def do_POST(self) -> None:  # noqa: N802
            content_len = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_len) if content_len else b"{}"
            if self.path == "/run-cycle":
                payload = json.loads(raw.decode("utf-8"))
                status, body = handle_run_cycle(payload, service)
                _json(self, status, body)
                return

            if self.path.startswith("/webhook/"):
                status, body = handle_webhook(
                    path=self.path,
                    headers={k: v for k, v in self.headers.items()},
                    raw_body=raw,
                    service=service,
                    webhook_cfg=webhook_cfg,
                    limiter=limiter,
                )
                _json(self, status, body)
                return

            status, body = 404, {"error": "not_found"}
            _json(self, status, body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return SentinelAPIHandler


def serve(
    service: SentinelService,
    host: str = "127.0.0.1",
    port: int = 8080,
    webhook_cfg: WebhookConfig | None = None,
    limiter: SlidingWindowRateLimiter | None = None,
) -> ThreadingHTTPServer:
    effective_webhook_cfg = webhook_cfg or WebhookConfig(tenant_id="default")
    effective_limiter = limiter or SlidingWindowRateLimiter(max_requests=30, window_seconds=60)
    handler = build_handler(service, webhook_cfg=effective_webhook_cfg, limiter=effective_limiter)
    server = ThreadingHTTPServer((host, port), handler)
    return server


def run_server_forever(
    service: SentinelService,
    host: str = "127.0.0.1",
    port: int = 8080,
    webhook_cfg: WebhookConfig | None = None,
    limiter: SlidingWindowRateLimiter | None = None,
) -> None:
    server = serve(service=service, host=host, port=port, webhook_cfg=webhook_cfg, limiter=limiter)
    server.serve_forever()
