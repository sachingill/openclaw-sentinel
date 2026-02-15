import unittest

from openclaw_sentinel.connectors import StaticConnector
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule
from openclaw_sentinel.service import SentinelService
from openclaw_sentinel.verification import VerificationService


class SentinelServiceTests(unittest.TestCase):
    def test_run_cycle_tracks_approved_blocked_and_success(self) -> None:
        incidents = [
            Incident(id="inc-1", tenant_id="t1", source="datadog", severity="high", summary="cpu"),
        ]

        connector = StaticConnector(source_name="datadog", incidents=incidents)

        def planner(incident: Incident):
            yield (
                Action(
                    id=f"{incident.id}-allowed",
                    incident_id=incident.id,
                    tenant_id="t1",
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95),
            )
            yield (
                Action(
                    id=f"{incident.id}-blocked",
                    incident_id=incident.id,
                    tenant_id="t1",
                    action_type="dangerous_action",
                    command="rm -rf /",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95),
            )

        def executor(_action: Action) -> str:
            return "ok"

        rule = PolicyRule(
            tenant_id="t1",
            max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
            allowlisted_action_types={"restart_service"},
            blocked_commands={"rm -rf"},
        )

        service = SentinelService(
            connectors=[connector],
            policy_engine=PolicyEngine(rule),
            planner=planner,
            executor=executor,
            verifier=VerificationService(),
        )

        summary = service.run_cycle(cycle_id="cycle-1")

        self.assertEqual(summary.incidents_seen, 1)
        self.assertEqual(summary.actions_approved, 1)
        self.assertEqual(summary.actions_blocked, 1)
        self.assertEqual(summary.actions_succeeded, 1)

        metrics = service.reporting.snapshot()
        self.assertEqual(metrics["incidents_seen"], 1)
        self.assertEqual(metrics["actions_approved"], 1)
        self.assertEqual(metrics["actions_blocked"], 1)
        self.assertEqual(metrics["actions_succeeded"], 1)


if __name__ == "__main__":
    unittest.main()
