from __future__ import annotations

import argparse
import json
from typing import List

from .connectors import DatadogConnector, GrafanaConnector
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


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run OpenClaw Sentinel demo")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles to run")
    args = parser.parse_args(argv)

    service = _demo_service()
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
