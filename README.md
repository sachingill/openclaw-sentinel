# OpenClaw Sentinel

OpenClaw Sentinel is a policy-gated 24x7 AI incident operations agent.

## Documentation
1. Product spec: `docs/OPENCLAW_SPEC.md`
2. Delivery levels: `docs/DELIVERY_LEVELS.md`

## Modes
1. `demo`: runs with seeded sample incidents.
2. `live`: runs using Datadog and Grafana credentials from environment variables.

## Run
```bash
cd /Users/sachingill/project/code/ai/openclaw
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m openclaw_sentinel --mode demo --cycles 1
PYTHONPATH=src python3 -m openclaw_sentinel --mode demo --serve --host 127.0.0.1 --port 8080
PYTHONPATH=src python3 -m openclaw_sentinel --mode demo --serve --enable-webhooks --webhook-rate-limit 30 --webhook-rate-window 60
cp .env.example .env
# export env vars from .env in your shell, then:
PYTHONPATH=src python3 -m openclaw_sentinel --mode live --cycles 1
```
