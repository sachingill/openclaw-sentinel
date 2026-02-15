import unittest

from openclaw_sentinel.live_connectors import LiveDatadogConnector, LiveGrafanaConnector


class _DDClient:
    def fetch_events(self):
        return [
            {
                "id": "dd1",
                "attributes": {
                    "title": "Queue backlog",
                    "status": "high",
                    "monitor": "m-1",
                },
            }
        ]


class _GrafanaClient:
    def fetch_alerts(self):
        return [
            {
                "labels": {
                    "alertname": "LatencyHigh",
                    "severity": "critical",
                    "rule_uid": "r-1",
                },
                "annotations": {"summary": "Latency is high"},
            }
        ]


class LiveConnectorTests(unittest.TestCase):
    def test_live_datadog_connector_maps_incident(self):
        connector = LiveDatadogConnector(client=_DDClient(), tenant_id="t1")
        items = list(connector.fetch_incidents())
        self.assertEqual(items[0].tenant_id, "t1")
        self.assertEqual(items[0].tags["monitor_id"], "m-1")

    def test_live_grafana_connector_maps_incident(self):
        connector = LiveGrafanaConnector(client=_GrafanaClient(), tenant_id="t1")
        items = list(connector.fetch_incidents())
        self.assertEqual(items[0].severity, "critical")
        self.assertEqual(items[0].summary, "Latency is high")


if __name__ == "__main__":
    unittest.main()
