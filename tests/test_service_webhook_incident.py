import unittest

from openclaw_sentinel.connectors import StaticConnector
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule
from openclaw_sentinel.service import SentinelService
from openclaw_sentinel.verification import VerificationService


class ServiceWebhookIncidentTests(unittest.TestCase):
    def test_run_incident_processes_single_incident(self):
        service = SentinelService(
            connectors=[StaticConnector(source_name="none", incidents=[])],
            policy_engine=PolicyEngine(
                PolicyRule(
                    tenant_id="t1",
                    max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
                    allowlisted_action_types={"restart_service"},
                )
            ),
            planner=lambda incident: [
                (
                    Action(
                        id=f"{incident.id}-a1",
                        incident_id=incident.id,
                        tenant_id=incident.tenant_id,
                        action_type="restart_service",
                        command="systemctl restart worker",
                    ),
                    RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.9),
                )
            ],
            executor=lambda _a: "ok",
            verifier=VerificationService(),
        )

        summary = service.run_incident(
            cycle_id="webhook-cycle",
            incident=Incident(id="w1", tenant_id="t1", source="telegram", severity="medium", summary="msg"),
        )

        self.assertEqual(summary.incidents_seen, 1)
        self.assertEqual(summary.actions_approved, 1)
        self.assertEqual(summary.actions_succeeded, 1)


if __name__ == "__main__":
    unittest.main()
