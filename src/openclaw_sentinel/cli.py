from __future__ import annotations

import argparse
import json
from typing import List

from .api import run_server_forever
from .config import load_live_config
from .connectors import DatadogConnector, GrafanaConnector
from .http_clients import DatadogAPIClient, GrafanaAPIClient
from .live_connectors import LiveDatadogConnector, LiveGrafanaConnector
from .planner import RuleBasedPlanner
from .policy import PolicyEngine, PolicyRule
from .service import SentinelService
from .verification import VerificationService
from .models import AutonomyLevel


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


def _live_service() -> SentinelService:
    cfg = load_live_config()
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
    parser.add_argument("--serve", action="store_true", help="Start REST API server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve")
    parser.add_argument("--port", type=int, default=8080, help="Port for --serve")
    args = parser.parse_args(argv)

    service = _demo_service() if args.mode == "demo" else _live_service()
    if args.serve:
        run_server_forever(service=service, host=args.host, port=args.port)
        return 0

    summaries = service.run_forever(interval_seconds=0, max_cycles=args.cycles)

    payload = {
        "summaries": [summary.__dict__ for summary in summaries],
        "metrics": service.reporting.snapshot(),
        "datadog_series": service.reporting.to_datadog_series(),
        "grafana_labels": service.reporting.to_grafana_labels(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
