import os
import unittest

from openclaw_sentinel.config import load_live_config


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.env)

    def test_load_live_config_success(self) -> None:
        os.environ["OPENCLAW_TENANT_ID"] = "t1"
        os.environ["OPENCLAW_AUTONOMY_LEVEL"] = "L2"
        os.environ["OPENCLAW_MAX_RISK_SCORE"] = "2.4"
        os.environ["DATADOG_BASE_URL"] = "https://api.datadoghq.com"
        os.environ["DATADOG_API_KEY"] = "key"
        os.environ["DATADOG_APP_KEY"] = "app"
        os.environ["GRAFANA_BASE_URL"] = "https://grafana.example.com"
        os.environ["GRAFANA_API_TOKEN"] = "token"

        cfg = load_live_config()
        self.assertEqual(cfg.tenant_id, "t1")
        self.assertEqual(cfg.max_risk_score_for_auto, 2.4)

    def test_load_live_config_missing_env(self) -> None:
        os.environ.pop("OPENCLAW_TENANT_ID", None)
        with self.assertRaises(ValueError):
            load_live_config()


if __name__ == "__main__":
    unittest.main()
