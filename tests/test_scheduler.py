import unittest
from datetime import datetime

from openclaw_sentinel.scheduler import CronParseError, CronSchedule


class SchedulerTests(unittest.TestCase):
    def test_parse_and_match_every_five_minutes(self) -> None:
        sched = CronSchedule.parse("*/5 * * * *")
        self.assertTrue(sched.matches(datetime(2026, 2, 15, 10, 15)))
        self.assertFalse(sched.matches(datetime(2026, 2, 15, 10, 16)))

    def test_next_after(self) -> None:
        sched = CronSchedule.parse("30 14 * * *")
        nxt = sched.next_after(datetime(2026, 2, 15, 14, 5, 22))
        self.assertEqual(nxt, datetime(2026, 2, 15, 14, 30))

    def test_invalid_expression(self) -> None:
        with self.assertRaises(CronParseError):
            CronSchedule.parse("* * *")


if __name__ == "__main__":
    unittest.main()
