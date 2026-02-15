from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class OnboardingConfig:
    tenant_id: str = "t1"
    mode: str = "demo"
    autonomy_level: str = "L1"
    max_risk_score: str = "2.8"
    datadog_base_url: str = "https://api.datadoghq.com"
    datadog_api_key: str = "replace_me"
    datadog_app_key: str = "replace_me"
    grafana_base_url: str = "https://your-grafana.example.com"
    grafana_api_token: str = "replace_me"
    webhook_default_severity: str = "medium"
    telegram_secret_token: str = "replace_me"
    whatsapp_signature_secret: str = "replace_me"
    twitter_signature_secret: str = "replace_me"


def render_env(cfg: OnboardingConfig) -> str:
    lines = [
        "# OpenClaw Sentinel live mode configuration",
        f"OPENCLAW_TENANT_ID={cfg.tenant_id}",
        f"OPENCLAW_AUTONOMY_LEVEL={cfg.autonomy_level}",
        f"OPENCLAW_MAX_RISK_SCORE={cfg.max_risk_score}",
        "",
        "# Datadog",
        f"DATADOG_BASE_URL={cfg.datadog_base_url}",
        f"DATADOG_API_KEY={cfg.datadog_api_key}",
        f"DATADOG_APP_KEY={cfg.datadog_app_key}",
        "",
        "# Grafana",
        f"GRAFANA_BASE_URL={cfg.grafana_base_url}",
        f"GRAFANA_API_TOKEN={cfg.grafana_api_token}",
        "",
        "# Optional webhook settings (used with --enable-webhooks)",
        f"OPENCLAW_WEBHOOK_DEFAULT_SEVERITY={cfg.webhook_default_severity}",
        f"OPENCLAW_TELEGRAM_SECRET_TOKEN={cfg.telegram_secret_token}",
        f"OPENCLAW_WHATSAPP_SIGNATURE_SECRET={cfg.whatsapp_signature_secret}",
        f"OPENCLAW_TWITTER_SIGNATURE_SECRET={cfg.twitter_signature_secret}",
    ]
    return "\n".join(lines) + "\n"


def _prompt(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def run_interactive() -> OnboardingConfig:
    mode = _prompt("Mode (demo/live)", "demo").lower()
    if mode not in {"demo", "live"}:
        raise ValueError("mode must be demo or live")

    cfg = OnboardingConfig(
        tenant_id=_prompt("Tenant ID", "t1"),
        mode=mode,
        autonomy_level=_prompt("Autonomy level (L0/L1/L2/L3)", "L1").upper(),
        max_risk_score=_prompt("Max risk score", "2.8"),
        datadog_base_url=_prompt("Datadog base URL", "https://api.datadoghq.com"),
        datadog_api_key=_prompt("Datadog API key", "replace_me"),
        datadog_app_key=_prompt("Datadog APP key", "replace_me"),
        grafana_base_url=_prompt("Grafana base URL", "https://your-grafana.example.com"),
        grafana_api_token=_prompt("Grafana API token", "replace_me"),
        webhook_default_severity=_prompt("Webhook default severity", "medium"),
        telegram_secret_token=_prompt("Telegram secret token", "replace_me"),
        whatsapp_signature_secret=_prompt("WhatsApp signature secret", "replace_me"),
        twitter_signature_secret=_prompt("Twitter signature secret", "replace_me"),
    )
    return cfg


def write_env(output: Path, content: str, overwrite: bool = False) -> None:
    if output.exists() and not overwrite:
        raise FileExistsError(f"{output} already exists. Use --overwrite to replace it.")
    output.write_text(content, encoding="utf-8")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenClaw Sentinel onboarding wizard")
    parser.add_argument("--output", default=".env", help="Output env file path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists")
    parser.add_argument("--non-interactive", action="store_true", help="Use flags/defaults instead of prompts")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--tenant-id", default="t1")
    parser.add_argument("--autonomy-level", default="L1")
    parser.add_argument("--max-risk-score", default="2.8")
    args = parser.parse_args(argv)

    if args.non_interactive:
        cfg = OnboardingConfig(
            mode=args.mode,
            tenant_id=args.tenant_id,
            autonomy_level=args.autonomy_level,
            max_risk_score=args.max_risk_score,
        )
    else:
        cfg = run_interactive()

    content = render_env(cfg)
    output = Path(args.output)
    write_env(output=output, content=content, overwrite=args.overwrite)

    print(f"Onboarding complete. Generated {output}.")
    if cfg.mode == "demo":
        print("Run: openclaw-sentinel --mode demo --cycles 1")
    else:
        print("Run: openclaw-sentinel --mode live --cycles 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
