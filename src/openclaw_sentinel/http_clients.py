from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from urllib import parse, request

Opener = Callable[[request.Request], Any]


@dataclass
class DatadogAPIClient:
    base_url: str
    api_key: str
    app_key: str
    opener: Opener = request.urlopen
    timeout_seconds: int = 10

    def fetch_events(self, query: str = "status:error", limit: int = 50) -> List[Dict[str, Any]]:
        params = parse.urlencode({"filter[query]": query, "page[limit]": str(limit)})
        url = f"{self.base_url.rstrip('/')}/api/v2/events?{params}"
        req = request.Request(
            url,
            headers={
                "Accept": "application/json",
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
            },
        )
        with self.opener(req, timeout=self.timeout_seconds) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("data", [])


@dataclass
class GrafanaAPIClient:
    base_url: str
    api_token: str
    alert_path: str = "/api/alertmanager/grafana/api/v2/alerts"
    opener: Opener = request.urlopen
    timeout_seconds: int = 10

    def fetch_alerts(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}{self.alert_path}"
        req = request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_token}",
            },
        )
        with self.opener(req, timeout=self.timeout_seconds) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if isinstance(payload, list):
            return payload
        return payload.get("alerts", [])
