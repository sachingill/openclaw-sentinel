import tempfile
import unittest
from pathlib import Path

from openclaw_sentinel.onboarding import OnboardingConfig, render_env, write_env


class OnboardingTests(unittest.TestCase):
    def test_render_env_contains_required_fields(self) -> None:
        cfg = OnboardingConfig(tenant_id="tenant-a", autonomy_level="L2")
        text = render_env(cfg)
        self.assertIn("OPENCLAW_TENANT_ID=tenant-a", text)
        self.assertIn("OPENCLAW_AUTONOMY_LEVEL=L2", text)
        self.assertIn("DATADOG_BASE_URL=", text)
        self.assertIn("GRAFANA_BASE_URL=", text)

    def test_write_env_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".env"
            write_env(path, "A=1\n", overwrite=False)
            with self.assertRaises(FileExistsError):
                write_env(path, "A=2\n", overwrite=False)

    def test_write_env_with_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".env"
            write_env(path, "A=1\n", overwrite=False)
            write_env(path, "A=2\n", overwrite=True)
            self.assertEqual(path.read_text(encoding="utf-8"), "A=2\n")


if __name__ == "__main__":
    unittest.main()
