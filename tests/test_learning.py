import unittest

from openclaw_sentinel.learning import EvalScore, PromotionGate


class PromotionGateTests(unittest.TestCase):
    def test_rejects_safety_regression(self) -> None:
        gate = PromotionGate()
        score = EvalScore(
            precision=0.95,
            recall=0.9,
            false_critical_rate=0.01,
            p95_latency_sec=20,
            safety_regression=True,
        )
        result = gate.evaluate(score)
        self.assertFalse(result.approved)
        self.assertEqual(result.reason, "safety_regression")

    def test_approves_good_candidate(self) -> None:
        gate = PromotionGate()
        score = EvalScore(
            precision=0.9,
            recall=0.8,
            false_critical_rate=0.05,
            p95_latency_sec=50,
            safety_regression=False,
        )
        result = gate.evaluate(score)
        self.assertTrue(result.approved)
        self.assertEqual(result.reason, "approved")


if __name__ == "__main__":
    unittest.main()
