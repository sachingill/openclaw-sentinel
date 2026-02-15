from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .connectors import IncidentConnector
from .http_clients import DatadogAPIClient, GrafanaAPIClient
from .models import Incident


@dataclass
class LiveDatadogConnector(IncidentConnector):
    client: DatadogAPIClient
    tenant_id: str
    source_name: str = "datadog"

    def fetch_incidents(self) -> Iterable[Incident]:
        incidents: List[Incident] = []
        for event in self.client.fetch_events():
            attrs: Dict[str, object] = event.get("attributes", {})
            title = str(attrs.get("title", "datadog event"))
            severity = str(attrs.get("status", "medium"))
            monitor_id = str(attrs.get("monitor", "unknown"))
            incidents.append(
                Incident(
                    id=str(event.get("id", title)),
                    tenant_id=self.tenant_id,
                    source=self.source_name,
                    severity=severity,
                    summary=title,
                    tags={"monitor_id": monitor_id},
                )
            )
        return incidents


@dataclass
class LiveGrafanaConnector(IncidentConnector):
    client: GrafanaAPIClient
    tenant_id: str
    source_name: str = "grafana"

    def fetch_incidents(self) -> Iterable[Incident]:
        incidents: List[Incident] = []
        for alert in self.client.fetch_alerts():
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})
            summary = str(annotations.get("summary", labels.get("alertname", "grafana alert")))
            severity = str(labels.get("severity", "medium"))
            rule_uid = str(labels.get("rule_uid", "unknown"))
            incident_id = str(labels.get("alertname", summary))
            incidents.append(
                Incident(
                    id=incident_id,
                    tenant_id=self.tenant_id,
                    source=self.source_name,
                    severity=severity,
                    summary=summary,
                    tags={"rule_uid": rule_uid},
                )
            )
        return incidents
