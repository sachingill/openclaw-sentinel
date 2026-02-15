import unittest

from openclaw_sentinel.reporting import ReportingStore


class ReportingTests(unittest.TestCase):
    def test_weekly_digest_contains_kpis(self) -> None:
        store = ReportingStore()
        store.increment("incidents_seen", 4)
        store.increment("actions_approved", 3)
        store.increment("actions_blocked", 1)
        store.increment("actions_succeeded", 2)
        store.increment("actions_failed", 1)

        digest = store.weekly_digest()

        self.assertIn("incidents_seen: 4", digest)
        self.assertIn("actions_approved: 3", digest)
        self.assertIn("approved_action_success_rate_pct: 66.67", digest)


if __name__ == "__main__":
    unittest.main()
