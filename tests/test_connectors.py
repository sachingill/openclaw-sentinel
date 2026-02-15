import unittest

from openclaw_sentinel.connectors import DatadogConnector, GrafanaConnector


class ConnectorTests(unittest.TestCase):
    def test_datadog_connector_normalizes_events(self) -> None:
        connector = DatadogConnector(
            raw_events=[
                {
                    "id": "dd-1",
                    "tenant_id": "t1",
                    "severity": "high",
                    "title": "Queue depth alert",
                    "monitor_id": "m1",
                }
            ]
        )
        incidents = list(connector.fetch_incidents())
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].source, "datadog")
        self.assertEqual(incidents[0].tags["monitor_id"], "m1")

    def test_grafana_connector_normalizes_alerts(self) -> None:
        connector = GrafanaConnector(
            raw_alerts=[
                {
                    "id": "gr-1",
                    "tenant_id": "t1",
                    "severity": "critical",
                    "name": "Latency high",
                    "rule_uid": "r-100",
                }
            ]
        )
        incidents = list(connector.fetch_incidents())
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].source, "grafana")
        self.assertEqual(incidents[0].tags["rule_uid"], "r-100")


if __name__ == "__main__":
    unittest.main()
