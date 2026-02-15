import os
import unittest

from openclaw_sentinel.cli import main


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.env)

    def test_demo_mode_runs(self) -> None:
        rc = main(["--mode", "demo", "--cycles", "1"])
        self.assertEqual(rc, 0)

    def test_live_mode_fails_without_required_env(self) -> None:
        for key in [
            "OPENCLAW_TENANT_ID",
            "DATADOG_BASE_URL",
            "DATADOG_API_KEY",
            "DATADOG_APP_KEY",
            "GRAFANA_BASE_URL",
            "GRAFANA_API_TOKEN",
        ]:
            os.environ.pop(key, None)

        with self.assertRaises(ValueError):
            main(["--mode", "live", "--cycles", "1"])


if __name__ == "__main__":
    unittest.main()
