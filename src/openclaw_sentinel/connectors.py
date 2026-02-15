from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Protocol

from .models import Incident


class IncidentConnector(Protocol):
    source_name: str

    def fetch_incidents(self) -> Iterable[Incident]:
        ...


@dataclass
class StaticConnector:
    source_name: str
    incidents: List[Incident] = field(default_factory=list)

    def fetch_incidents(self) -> Iterable[Incident]:
        return list(self.incidents)


@dataclass
class DatadogConnector:
    raw_events: List[Dict[str, str]] = field(default_factory=list)
    source_name: str = "datadog"

    def fetch_incidents(self) -> Iterable[Incident]:
        incidents: List[Incident] = []
        for event in self.raw_events:
            incidents.append(
                Incident(
                    id=event["id"],
                    tenant_id=event["tenant_id"],
                    source=self.source_name,
                    severity=event.get("severity", "medium"),
                    summary=event.get("title", "datadog alert"),
                    tags={"monitor_id": event.get("monitor_id", "unknown")},
                )
            )
        return incidents


@dataclass
class GrafanaConnector:
    raw_alerts: List[Dict[str, str]] = field(default_factory=list)
    source_name: str = "grafana"

    def fetch_incidents(self) -> Iterable[Incident]:
        incidents: List[Incident] = []
        for alert in self.raw_alerts:
            incidents.append(
                Incident(
                    id=alert["id"],
                    tenant_id=alert["tenant_id"],
                    source=self.source_name,
                    severity=alert.get("severity", "medium"),
                    summary=alert.get("name", "grafana alert"),
                    tags={"rule_uid": alert.get("rule_uid", "unknown")},
                )
            )
        return incidents
