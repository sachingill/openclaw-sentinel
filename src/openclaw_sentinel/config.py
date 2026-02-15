from __future__ import annotations

import os
from dataclasses import dataclass

from .models import AutonomyLevel
from .webhooks import WebhookConfig, WebhookSecrets


@dataclass(frozen=True)
class LiveConfig:
    tenant_id: str
    datadog_base_url: str
    datadog_api_key: str
    datadog_app_key: str
    grafana_base_url: str
    grafana_api_token: str
    autonomy_level: AutonomyLevel
    max_risk_score_for_auto: float


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_live_config() -> LiveConfig:
    level_raw = os.getenv("OPENCLAW_AUTONOMY_LEVEL", "L1").strip().upper()
    levels = {
        "L0": AutonomyLevel.L0_OBSERVE,
        "L1": AutonomyLevel.L1_ASSIST,
        "L2": AutonomyLevel.L2_BOUNDED_AUTO,
        "L3": AutonomyLevel.L3_RESTRICTED,
    }
    if level_raw not in levels:
        raise ValueError("OPENCLAW_AUTONOMY_LEVEL must be one of: L0, L1, L2, L3")

    risk_raw = os.getenv("OPENCLAW_MAX_RISK_SCORE", "2.8").strip()
    try:
        max_risk_score = float(risk_raw)
    except ValueError as exc:
        raise ValueError("OPENCLAW_MAX_RISK_SCORE must be numeric") from exc

    return LiveConfig(
        tenant_id=_require_env("OPENCLAW_TENANT_ID"),
        datadog_base_url=_require_env("DATADOG_BASE_URL"),
        datadog_api_key=_require_env("DATADOG_API_KEY"),
        datadog_app_key=_require_env("DATADOG_APP_KEY"),
        grafana_base_url=_require_env("GRAFANA_BASE_URL"),
        grafana_api_token=_require_env("GRAFANA_API_TOKEN"),
        autonomy_level=levels[level_raw],
        max_risk_score_for_auto=max_risk_score,
    )


def load_webhook_config(tenant_id: str) -> WebhookConfig:
    default_severity = os.getenv("OPENCLAW_WEBHOOK_DEFAULT_SEVERITY", "medium").strip() or "medium"
    return WebhookConfig(
        tenant_id=tenant_id,
        default_severity=default_severity,
        secrets=WebhookSecrets(
            telegram_secret_token=os.getenv("OPENCLAW_TELEGRAM_SECRET_TOKEN", "").strip(),
            twilio_signature_secret=os.getenv("OPENCLAW_WHATSAPP_SIGNATURE_SECRET", "").strip(),
            twitter_signature_secret=os.getenv("OPENCLAW_TWITTER_SIGNATURE_SECRET", "").strip(),
        ),
    )
