import hashlib
import hmac
import json
import unittest

from openclaw_sentinel.api import handle_webhook
from openclaw_sentinel.connectors import StaticConnector
from openclaw_sentinel.models import Action, AutonomyLevel, Incident, RiskProfile
from openclaw_sentinel.policy import PolicyEngine, PolicyRule
from openclaw_sentinel.rate_limit import SlidingWindowRateLimiter
from openclaw_sentinel.service import SentinelService
from openclaw_sentinel.verification import VerificationService
from openclaw_sentinel.webhooks import WebhookConfig, WebhookSecrets


def _sig(secret: str, raw: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


class WebhookTests(unittest.TestCase):
    def _service(self):
        connector = StaticConnector(source_name="empty", incidents=[])

        def planner(incident: Incident):
            yield (
                Action(
                    id=f"{incident.id}-a1",
                    incident_id=incident.id,
                    tenant_id=incident.tenant_id,
                    action_type="restart_service",
                    command="systemctl restart worker",
                ),
                RiskProfile(impact=1, blast_radius=1, reversibility=5, confidence=0.95),
            )

        return SentinelService(
            connectors=[connector],
            policy_engine=PolicyEngine(
                PolicyRule(
                    tenant_id="t1",
                    max_autonomy=AutonomyLevel.L2_BOUNDED_AUTO,
                    allowlisted_action_types={"restart_service"},
                )
            ),
            planner=planner,
            executor=lambda _a: "ok",
            verifier=VerificationService(),
        )

    def test_telegram_webhook_triggers_cycle(self):
        service = self._service()
        cfg = WebhookConfig(
            tenant_id="t1",
            secrets=WebhookSecrets(telegram_secret_token="telegram-secret"),
        )
        limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
        raw = json.dumps({"message": {"message_id": 1, "text": "restart", "chat": {"id": 42}}}).encode("utf-8")
        status, body = handle_webhook(
            path="/webhook/telegram",
            headers={"x-telegram-bot-api-secret-token": "telegram-secret", "content-type": "application/json"},
            raw_body=raw,
            service=service,
            webhook_cfg=cfg,
            limiter=limiter,
        )
        self.assertEqual(status, 202)
        self.assertEqual(body["actions_approved"], 1)

    def test_whatsapp_invalid_signature_blocked(self):
        service = self._service()
        cfg = WebhookConfig(
            tenant_id="t1",
            secrets=WebhookSecrets(twilio_signature_secret="wa-secret"),
        )
        limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
        raw = b"Body=help&MessageSid=SM1&From=+1000"
        status, body = handle_webhook(
            path="/webhook/whatsapp",
            headers={"content-type": "application/x-www-form-urlencoded", "x-openclaw-signature": "bad"},
            raw_body=raw,
            service=service,
            webhook_cfg=cfg,
            limiter=limiter,
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "unauthorized")

    def test_twitter_webhook_rate_limited(self):
        service = self._service()
        cfg = WebhookConfig(
            tenant_id="t1",
            secrets=WebhookSecrets(twitter_signature_secret="x-secret"),
        )
        limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60)
        raw = json.dumps({"id": "x1", "text": "incident post", "author": "alice"}).encode("utf-8")
        headers = {"content-type": "application/json", "x-openclaw-signature": _sig("x-secret", raw)}

        first_status, _ = handle_webhook(
            path="/webhook/twitter",
            headers=headers,
            raw_body=raw,
            service=service,
            webhook_cfg=cfg,
            limiter=limiter,
        )
        second_status, second_body = handle_webhook(
            path="/webhook/twitter",
            headers=headers,
            raw_body=raw,
            service=service,
            webhook_cfg=cfg,
            limiter=limiter,
        )

        self.assertEqual(first_status, 202)
        self.assertEqual(second_status, 429)
        self.assertEqual(second_body["error"], "rate_limited")


if __name__ == "__main__":
    unittest.main()
