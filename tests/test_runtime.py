import unittest

from openclaw_sentinel.connectors import StaticConnector
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule
from openclaw_sentinel.service import SentinelService
from openclaw_sentinel.verification import VerificationService


class RuntimeTests(unittest.TestCase):
    def test_run_forever_honors_max_cycles(self) -> None:
        connector = StaticConnector(
            source_name="datadog",
            incidents=[Incident(id="i1", tenant_id="t1", source="datadog", severity="high", summary="cpu")],
        )

        def planner(incident: Incident):
            yield (
                Action(
                    id=f"{incident.id}-a1",
                    incident_id=incident.id,
                    tenant_id="t1",
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.9),
            )

        def executor(_action: Action) -> str:
            return "ok"

        service = SentinelService(
            connectors=[connector],
            policy_engine=PolicyEngine(
                PolicyRule(
                    tenant_id="t1",
                    max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
                    allowlisted_action_types={"restart_service"},
                )
            ),
            planner=planner,
            executor=executor,
            verifier=VerificationService(),
        )

        summaries = service.run_forever(interval_seconds=0, max_cycles=2)
        self.assertEqual(len(summaries), 2)
        self.assertEqual(summaries[0].cycle_id, "cycle-1")
        self.assertEqual(summaries[1].cycle_id, "cycle-2")


if __name__ == "__main__":
    unittest.main()
