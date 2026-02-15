from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, List

from .connectors import IncidentConnector
from .models import Action, CycleSummary, Incident, RiskProfile
from .policy import PolicyEngine
from .reporting import ReportingStore
from .verification import VerificationService

PlannerFn = Callable[[Incident], Iterable[tuple[Action, RiskProfile]]]
ExecutorFn = Callable[[Action], str]


@dataclass
class SentinelService:
    connectors: List[IncidentConnector]
    policy_engine: PolicyEngine
    planner: PlannerFn
    executor: ExecutorFn
    verifier: VerificationService
    reporting: ReportingStore = field(default_factory=ReportingStore)

    def _process_incident(self, incident: Incident) -> tuple[int, int, int]:
        actions_approved = 0
        actions_blocked = 0
        actions_succeeded = 0
        self.reporting.increment("incidents_seen")

        for action, risk in self.planner(incident):
            decision = self.policy_engine.evaluate(action, risk)
            if not decision.approved:
                actions_blocked += 1
                self.reporting.increment("actions_blocked")
                self.reporting.increment(f"blocked_reason_{decision.reason}")
                continue

            actions_approved += 1
            self.reporting.increment("actions_approved")
            result = self.executor(action)
            outcome = self.verifier.verify(action, result)
            if outcome.success:
                actions_succeeded += 1
                self.reporting.increment("actions_succeeded")
            else:
                self.reporting.increment("actions_failed")
        return actions_approved, actions_blocked, actions_succeeded

    def run_incident(self, cycle_id: str, incident: Incident) -> CycleSummary:
        approved, blocked, succeeded = self._process_incident(incident)
        return CycleSummary(
            cycle_id=cycle_id,
            incidents_seen=1,
            actions_approved=approved,
            actions_blocked=blocked,
            actions_succeeded=succeeded,
        )

    def run_cycle(self, cycle_id: str) -> CycleSummary:
        incidents_seen = 0
        actions_approved = 0
        actions_blocked = 0
        actions_succeeded = 0

        for connector in self.connectors:
            for incident in connector.fetch_incidents():
                incidents_seen += 1
                approved, blocked, succeeded = self._process_incident(incident)
                actions_approved += approved
                actions_blocked += blocked
                actions_succeeded += succeeded

        return CycleSummary(
            cycle_id=cycle_id,
            incidents_seen=incidents_seen,
            actions_approved=actions_approved,
            actions_blocked=actions_blocked,
            actions_succeeded=actions_succeeded,
        )

    def run_forever(self, interval_seconds: int = 60, max_cycles: int | None = None) -> List[CycleSummary]:
        summaries: List[CycleSummary] = []
        cycle = 1
        while True:
            cycle_id = f"cycle-{cycle}"
            summaries.append(self.run_cycle(cycle_id=cycle_id))
            if max_cycles is not None and cycle >= max_cycles:
                return summaries
            cycle += 1
            time.sleep(interval_seconds)
