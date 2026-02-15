import logging
import tempfile
import unittest

from openclaw_sentinel.logging_utils import configure_logging


class LoggingUtilsTests(unittest.TestCase):
    def test_configure_logging_debug_with_file(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            configure_logging(debug=True, log_file=tmp.name)
            logger = logging.getLogger("openclaw_sentinel.test")
            logger.debug("debug-line")
            for handler in logging.getLogger().handlers:
                handler.flush()
            tmp.seek(0)
            content = tmp.read().decode("utf-8")
            self.assertIn("debug-line", content)


if __name__ == "__main__":
    unittest.main()
