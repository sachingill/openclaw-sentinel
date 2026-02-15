import unittest

from openclaw_sentinel.models import Action, AutonomyLevel, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule


class PolicyEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = PolicyRule(
            tenant_id="t1",
            max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
            allowlisted_action_types={"restart_service", "scale_worker"},
            blocked_commands={"rm -rf", "terraform destroy"},
            max_risk_score_for_auto=2.8,
        )
        self.engine = PolicyEngine(self.rule)

    def test_denies_non_allowlisted_action(self) -> None:
        action = Action(
            id="a1",
            incident_id="i1",
            tenant_id="t1",
            action_type="drop_database",
            command="drop db",
        )
        risk = RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95)
        decision = self.engine.evaluate(action, risk)
        self.assertFalse(decision.approved)
        self.assertEqual(decision.reason, "action_type_not_allowlisted")

    def test_denies_blocked_command(self) -> None:
        action = Action(
            id="a2",
            incident_id="i1",
            tenant_id="t1",
            action_type="restart_service",
            command="rm -rf /tmp/cache",
        )
        risk = RiskProfile(impact=1, blast_radius=1, reversibility=4, confidence=0.9)
        decision = self.engine.evaluate(action, risk)
        self.assertFalse(decision.approved)
        self.assertEqual(decision.reason, "command_blocked")

    def test_denies_high_risk_even_if_allowlisted(self) -> None:
        action = Action(
            id="a3",
            incident_id="i1",
            tenant_id="t1",
            action_type="restart_service",
            command="systemctl restart app",
        )
        risk = RiskProfile(impact=5, blast_radius=5, reversibility=1, confidence=0.6)
        decision = self.engine.evaluate(action, risk)
        self.assertFalse(decision.approved)
        self.assertTrue(decision.reason.startswith("risk_too_high:"))

    def test_approves_low_risk_allowlisted_action(self) -> None:
        action = Action(
            id="a4",
            incident_id="i1",
            tenant_id="t1",
            action_type="restart_service",
            command="systemctl restart worker",
        )
        risk = RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95)
        decision = self.engine.evaluate(action, risk)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.reason, "approved_for_auto")


if __name__ == "__main__":
    unittest.main()
