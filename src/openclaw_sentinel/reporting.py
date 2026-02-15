from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ReportingStore:
    counters: Dict[str, int] = field(default_factory=dict)

    def increment(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def snapshot(self) -> Dict[str, int]:
        return dict(self.counters)

    def to_datadog_series(self) -> Dict[str, int]:
        # Placeholder shape used by future Datadog exporter.
        return {f"openclaw_sentinel.{k}": v for k, v in self.counters.items()}

    def to_grafana_labels(self) -> Dict[str, str]:
        # Placeholder shape used by future Prometheus/Grafana exporter.
        return {k: str(v) for k, v in self.counters.items()}

    def weekly_digest(self) -> str:
        incidents = self.counters.get("incidents_seen", 0)
        approved = self.counters.get("actions_approved", 0)
        blocked = self.counters.get("actions_blocked", 0)
        succeeded = self.counters.get("actions_succeeded", 0)
        failed = self.counters.get("actions_failed", 0)
        success_rate = 0.0 if approved == 0 else round((succeeded / approved) * 100, 2)
        return (
            "OpenClaw Sentinel Weekly Digest\n"
            f"- incidents_seen: {incidents}\n"
            f"- actions_approved: {approved}\n"
            f"- actions_blocked: {blocked}\n"
            f"- actions_succeeded: {succeeded}\n"
            f"- actions_failed: {failed}\n"
            f"- approved_action_success_rate_pct: {success_rate}\n"
        )
