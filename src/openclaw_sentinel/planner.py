from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from .models import Action, Incident, RiskProfile


@dataclass
class RuleBasedPlanner:
    """Maps incident severity to bounded runbook actions and risk estimates."""

    def plan(self, incident: Incident) -> Iterable[Tuple[Action, RiskProfile]]:
        severity = incident.severity.lower()
        if severity in {"critical", "high"}:
            yield (
                Action(
                    id=f"{incident.id}:restart_worker",
                    incident_id=incident.id,
                    tenant_id=incident.tenant_id,
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=2, blast_radius=2, reversibility=5, confidence=0.85),
            )
        if severity == "critical":
            yield (
                Action(
                    id=f"{incident.id}:scale_worker",
                    incident_id=incident.id,
                    tenant_id=incident.tenant_id,
                    action_type="scale_worker",
                    command="kubectl scale deployment/worker --replicas=6",
                ),
                RiskProfile(impact=3, blast_radius=2, reversibility=4, confidence=0.8),
            )
