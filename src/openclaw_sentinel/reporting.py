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
        return {f"openclaw.{k}": v for k, v in self.counters.items()}

    def to_grafana_labels(self) -> Dict[str, str]:
        # Placeholder shape used by future Prometheus/Grafana exporter.
        return {k: str(v) for k, v in self.counters.items()}
