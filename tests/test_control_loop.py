import unittest

from openclaw_sentinel.control_loop import ControlLoop
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule


class ControlLoopTests(unittest.TestCase):
    def _incident(self) -> Incident:
        return Incident(
            id="inc-1",
            tenant_id="t1",
            source="datadog",
            severity="high",
            summary="worker saturation",
        )

    def test_executes_only_approved_actions(self) -> None:
        executed = []

        def planner(incident: Incident):
            yield (
                Action(
                    id="a-ok",
                    incident_id=incident.id,
                    tenant_id="t1",
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.9),
            )
            yield (
                Action(
                    id="a-no",
                    incident_id=incident.id,
                    tenant_id="t1",
                    action_type="drop_database",
                    command="drop db",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.9),
            )

        def executor(action: Action) -> str:
            executed.append(action.id)
            return "ok"

        rule = PolicyRule(
            tenant_id="t1",
            max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
            allowlisted_action_types={"restart_service"},
        )
        loop = ControlLoop(PolicyEngine(rule), planner=planner, executor=executor)
        result = loop.run_once(self._incident())

        self.assertEqual(executed, ["a-ok"])
        self.assertEqual(len(result.decisions), 2)
        self.assertIn("a-no:blocked", "\n".join(loop.execution_log))

    def test_blocks_tenant_mismatch(self) -> None:
        def planner(incident: Incident):
            yield (
                Action(
                    id="a-tenant",
                    incident_id=incident.id,
                    tenant_id="other-tenant",
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95),
            )

        def executor(_action: Action) -> str:
            raise AssertionError("executor should not run for tenant mismatch")

        rule = PolicyRule(
            tenant_id="t1",
            max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
            allowlisted_action_types={"restart_service"},
        )
        loop = ControlLoop(PolicyEngine(rule), planner=planner, executor=executor)
        result = loop.run_once(self._incident())

        self.assertFalse(result.decisions[0].approved)
        self.assertEqual(result.decisions[0].reason, "tenant_mismatch")


if __name__ == "__main__":
    unittest.main()
