from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime
from typing import List

from .api import run_server_forever
from .config import load_live_config, load_webhook_config
from .connectors import DatadogConnector, GrafanaConnector
from .http_clients import DatadogAPIClient, GrafanaAPIClient
from .live_connectors import LiveDatadogConnector, LiveGrafanaConnector
from .planner import RuleBasedPlanner
from .policy import PolicyEngine, PolicyRule
from .rate_limit import SlidingWindowRateLimiter
from .scheduler import CronSchedule
from .service import SentinelService
from .logging_utils import configure_logging
from .verification import VerificationService
from .models import AutonomyLevel

logger = logging.getLogger("openclaw_sentinel.cli")


def _demo_service() -> SentinelService:
    datadog = DatadogConnector(
        raw_events=[
            {
                "id": "dd-1",
                "tenant_id": "t1",
                "severity": "high",
                "title": "High worker queue depth",
                "monitor_id": "m-10",
            }
        ]
    )
    grafana = GrafanaConnector(
        raw_alerts=[
            {
                "id": "gr-1",
                "tenant_id": "t1",
                "severity": "critical",
                "name": "API latency breach",
                "rule_uid": "r-77",
            }
        ]
    )
    rule = PolicyRule(
        tenant_id="t1",
        max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
        allowlisted_action_types={"restart_service", "scale_worker"},
        blocked_commands={"rm -rf", "terraform destroy"},
        max_risk_score_for_auto=2.8,
    )
    planner = RuleBasedPlanner()

    def executor(_action):
        return "ok"

    return SentinelService(
        connectors=[datadog, grafana],
        policy_engine=PolicyEngine(rule),
        planner=planner.plan,
        executor=executor,
        verifier=VerificationService(),
    )


def _live_service(cfg=None) -> SentinelService:
    cfg = cfg or load_live_config()
    datadog_client = DatadogAPIClient(
        base_url=cfg.datadog_base_url,
        api_key=cfg.datadog_api_key,
        app_key=cfg.datadog_app_key,
    )
    grafana_client = GrafanaAPIClient(
        base_url=cfg.grafana_base_url,
        api_token=cfg.grafana_api_token,
    )
    rule = PolicyRule(
        tenant_id=cfg.tenant_id,
        max_autonomy=cfg.autonomy_level,
        allowlisted_action_types={"restart_service", "scale_worker"},
        blocked_commands={"rm -rf", "terraform destroy", "drop database"},
        max_risk_score_for_auto=cfg.max_risk_score_for_auto,
    )
    planner = RuleBasedPlanner()

    def executor(_action):
        return "ok"

    return SentinelService(
        connectors=[
            LiveDatadogConnector(client=datadog_client, tenant_id=cfg.tenant_id),
            LiveGrafanaConnector(client=grafana_client, tenant_id=cfg.tenant_id),
        ],
        policy_engine=PolicyEngine(rule),
        planner=planner.plan,
        executor=executor,
        verifier=VerificationService(),
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run OpenClaw Sentinel demo")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo", help="Execution mode")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles to run")
    parser.add_argument("--cron", default="", help="Cron expression for scheduled cycle runs (5 fields)")
    parser.add_argument("--serve", action="store_true", help="Start REST API server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve")
    parser.add_argument("--port", type=int, default=8080, help="Port for --serve")
    parser.add_argument("--enable-webhooks", action="store_true", help="Enable /webhook/* endpoints")
    parser.add_argument("--webhook-rate-limit", type=int, default=30, help="Webhook max requests per window")
    parser.add_argument("--webhook-rate-window", type=int, default=60, help="Webhook rate limit window seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    parser.add_argument("--log-file", default="", help="Optional log file path")
    args = parser.parse_args(argv)
    configure_logging(debug=args.debug, log_file=args.log_file or None)

    live_cfg = load_live_config() if args.mode == "live" else None
    service = _demo_service() if args.mode == "demo" else _live_service(cfg=live_cfg)
    if args.serve:
        webhook_cfg = None
        limiter = None
        if args.enable_webhooks:
            tenant_id = "t1" if args.mode == "demo" else live_cfg.tenant_id
            webhook_cfg = load_webhook_config(tenant_id=tenant_id)
            limiter = SlidingWindowRateLimiter(
                max_requests=args.webhook_rate_limit,
                window_seconds=args.webhook_rate_window,
            )
        logger.info("Starting API server host=%s port=%s webhooks=%s", args.host, args.port, args.enable_webhooks)
        run_server_forever(service=service, host=args.host, port=args.port, webhook_cfg=webhook_cfg, limiter=limiter)
        return 0

    if args.cron:
        schedule = CronSchedule.parse(args.cron)
        logger.info("Cron mode enabled schedule=%s cycles=%s", args.cron, args.cycles)
        summaries = []
        for i in range(args.cycles):
            now = datetime.now()
            next_run = schedule.next_after(now)
            sleep_seconds = max(0.0, (next_run - now).total_seconds())
            logger.info("Waiting until next run cycle=%s run_at=%s sleep_seconds=%.3f", i + 1, next_run.isoformat(), sleep_seconds)
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
            cycle_id = f"cron-{i + 1}"
            summaries.append(service.run_cycle(cycle_id=cycle_id))
    else:
        summaries = service.run_forever(interval_seconds=0, max_cycles=args.cycles)

    payload = {
        "summaries": [summary.__dict__ for summary in summaries],
        "metrics": service.reporting.snapshot(),
        "datadog_series": service.reporting.to_datadog_series(),
        "grafana_labels": service.reporting.to_grafana_labels(),
    }
    logger.debug("Execution payload=%s", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
