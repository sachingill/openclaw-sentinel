import unittest

from openclaw_sentinel.api import handle_get, handle_run_cycle
from openclaw_sentinel.connectors import StaticConnector
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule
from openclaw_sentinel.service import SentinelService
from openclaw_sentinel.verification import VerificationService


class APITests(unittest.TestCase):
    def _service(self):
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

        return SentinelService(
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

    def test_health_and_run_cycle_handlers(self):
        service = self._service()
        status, payload = handle_get("/health", service)
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")

        status, payload = handle_run_cycle({"cycle_id": "api-test"}, service)
        self.assertEqual(status, 200)
        self.assertEqual(payload["cycle_id"], "api-test")
        self.assertEqual(payload["actions_approved"], 1)

        status, metrics = handle_get("/metrics", service)
        self.assertEqual(status, 200)
        self.assertEqual(metrics["actions_approved"], 1)


if __name__ == "__main__":
    unittest.main()
