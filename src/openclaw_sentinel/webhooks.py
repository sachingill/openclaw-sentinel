from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Any, Dict
from urllib.parse import parse_qs

from .models import Incident


@dataclass
class WebhookSecrets:
    telegram_secret_token: str = ""
    twilio_signature_secret: str = ""
    twitter_signature_secret: str = ""


@dataclass
class WebhookConfig:
    tenant_id: str
    default_severity: str = "medium"
    secrets: WebhookSecrets = field(default_factory=WebhookSecrets)


def _hmac_sha256(secret: str, raw_body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _verify_signature(source: str, headers: Dict[str, str], raw_body: bytes, cfg: WebhookConfig) -> bool:
    source = source.lower()
    if source == "telegram":
        if not cfg.secrets.telegram_secret_token:
            return False
        token = headers.get("x-telegram-bot-api-secret-token", "")
        return hmac.compare_digest(token, cfg.secrets.telegram_secret_token)

    if source == "whatsapp":
        if not cfg.secrets.twilio_signature_secret:
            return False
        expected = _hmac_sha256(cfg.secrets.twilio_signature_secret, raw_body)
        return hmac.compare_digest(headers.get("x-openclaw-signature", ""), expected)

    if source == "twitter":
        if not cfg.secrets.twitter_signature_secret:
            return False
        expected = _hmac_sha256(cfg.secrets.twitter_signature_secret, raw_body)
        return hmac.compare_digest(headers.get("x-openclaw-signature", ""), expected)

    return False


def _parse_payload(source: str, raw_body: bytes, content_type: str) -> Dict[str, Any]:
    source = source.lower()
    if source == "whatsapp" and "application/x-www-form-urlencoded" in content_type:
        parsed = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
        return {k: v[0] for k, v in parsed.items()}

    if not raw_body:
        return {}
    return json.loads(raw_body.decode("utf-8"))


def _incident_from_payload(source: str, payload: Dict[str, Any], cfg: WebhookConfig) -> Incident:
    source = source.lower()
    if source == "telegram":
        msg = payload.get("message", {})
        chat = msg.get("chat", {})
        incident_id = f"tg-{msg.get('message_id', 'unknown')}"
        summary = str(msg.get("text", "telegram event"))
        return Incident(
            id=incident_id,
            tenant_id=cfg.tenant_id,
            source="telegram",
            severity=cfg.default_severity,
            summary=summary,
            tags={"chat_id": str(chat.get("id", "unknown"))},
        )

    if source == "whatsapp":
        summary = str(payload.get("Body", "whatsapp event"))
        incident_id = str(payload.get("MessageSid", f"wa-{hash(summary)}"))
        from_id = str(payload.get("From", "unknown"))
        return Incident(
            id=incident_id,
            tenant_id=cfg.tenant_id,
            source="whatsapp",
            severity=cfg.default_severity,
            summary=summary,
            tags={"from": from_id},
        )

    if source == "twitter":
        incident_id = str(payload.get("id", f"x-{hash(json.dumps(payload, sort_keys=True))}"))
        summary = str(payload.get("text", "twitter event"))
        author = str(payload.get("author", "unknown"))
        severity = str(payload.get("severity", cfg.default_severity))
        return Incident(
            id=incident_id,
            tenant_id=cfg.tenant_id,
            source="twitter",
            severity=severity,
            summary=summary,
            tags={"author": author},
        )

    raise ValueError("unsupported_source")


def process_webhook(
    source: str,
    headers: Dict[str, str],
    raw_body: bytes,
    cfg: WebhookConfig,
) -> Incident:
    normalized_headers = {k.lower(): v for k, v in headers.items()}
    if not _verify_signature(source, normalized_headers, raw_body, cfg):
        raise PermissionError("invalid_signature")

    content_type = normalized_headers.get("content-type", "application/json")
    payload = _parse_payload(source, raw_body, content_type)
    return _incident_from_payload(source, payload, cfg)
