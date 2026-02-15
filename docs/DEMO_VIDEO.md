# Demo Video Guide

## Goal
Record a clear 4-6 minute demo showing:
1. Installation
2. Onboarding
3. Autonomous execution
4. Outcomes and quality checks

## Recording Setup
1. Terminal font: 16-18pt, dark background.
2. Window size: 120x35 or larger.
3. Start with clean terminal in repo root.

## Demo Run Command
```bash
cd /Users/sachingill/project/code/ai/openclaw
./scripts/demo_terminal.sh
```

## Shot Plan (Timestamped)
1. 00:00-00:20 Intro
- Show repo root and say: "This is OpenClaw Sentinel, a policy-gated autonomous incident operations agent."

2. 00:20-01:10 Installation
- Run `./scripts/install.sh` (or let demo script do it).
- Highlight virtualenv and package setup.

3. 01:10-02:00 Onboarding
- Show `openclaw-onboarding --non-interactive ... --output .env.demo`.
- Highlight generated `.env.demo` fields for tenant/autonomy/integrations.

4. 02:00-03:00 Quality Gate
- Show unit tests passing.
- Speak line: "All tests pass before live execution."

5. 03:00-04:20 Autonomous Workflow
- Show `openclaw-sentinel --mode demo --cycles 2 --debug --log-file openclaw-demo.log`.
- Explain flow: ingest -> plan -> policy gate -> execute -> verify -> report.

6. 04:20-05:20 Outcomes
- Show metrics JSON in terminal output.
- Show `tail -n 20 openclaw-demo.log` for traceability.
- Mention safety gates, logs, and deterministic outcomes.

## Narration Script (Short)
"OpenClaw Sentinel installs with one script, onboards in one command, and can run autonomously in policy-gated cycles. We verify quality first with tests, then execute a multi-cycle run with debug logs enabled. The output includes cycle summaries, action metrics, and traceable logs for operational confidence."

## Optional Webhook Segment (Extra 60-90s)
If you want to show webhook readiness:
1. Show command used to run API with webhooks enabled:
```bash
openclaw-sentinel --mode demo --serve --enable-webhooks --webhook-rate-limit 30 --webhook-rate-window 60 --debug --log-file ./openclaw-demo.log
```
2. Mention supported triggers: Telegram, WhatsApp, Twitter relay.
3. Mention controls: signature validation + rate limiting.

## Final Slide / Closing Text
- Installer: ready
- Onboarding: ready
- Autonomous core: ready
- Safety controls: enabled
- Tests: passing
