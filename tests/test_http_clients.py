import json
import unittest

from openclaw_sentinel.http_clients import DatadogAPIClient, GrafanaAPIClient


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class HTTPClientTests(unittest.TestCase):
    def test_datadog_client_fetch_events(self):
        def opener(req, timeout=10):
            self.assertIn("/api/v2/events", req.full_url)
            headers = {k.lower(): v for k, v in req.header_items()}
            self.assertEqual(headers["dd-api-key"], "k")
            return _FakeResponse({"data": [{"id": "1"}]})

        client = DatadogAPIClient(base_url="https://api.datadog.test", api_key="k", app_key="a", opener=opener)
        data = client.fetch_events()
        self.assertEqual(data[0]["id"], "1")

    def test_grafana_client_fetch_alerts(self):
        def opener(req, timeout=10):
            self.assertIn("/api/alertmanager/grafana/api/v2/alerts", req.full_url)
            self.assertTrue(req.headers["Authorization"].startswith("Bearer"))
            return _FakeResponse([{"labels": {"alertname": "CPUHigh"}}])

        client = GrafanaAPIClient(base_url="https://grafana.test", api_token="token", opener=opener)
        data = client.fetch_alerts()
        self.assertEqual(data[0]["labels"]["alertname"], "CPUHigh")


if __name__ == "__main__":
    unittest.main()
