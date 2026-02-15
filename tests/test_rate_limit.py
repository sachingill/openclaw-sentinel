import unittest

from openclaw_sentinel.rate_limit import SlidingWindowRateLimiter


class RateLimitTests(unittest.TestCase):
    def test_allows_then_blocks_within_window(self) -> None:
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
        self.assertTrue(limiter.allow("k1"))
        self.assertTrue(limiter.allow("k1"))
        self.assertFalse(limiter.allow("k1"))


if __name__ == "__main__":
    unittest.main()
