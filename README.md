# OpenClaw Sentinel

OpenClaw Sentinel is a policy-gated 24x7 AI incident operations core with bounded autonomy, integration-ready ingestion, and safe promotion gates for self-improvement.

## Objective Coverage
1. Spec Drafting: complete (`docs/OPENCLAW_SPEC.md`, `docs/DELIVERY_LEVELS.md`)
2. Test Cases: complete for core safety/runtime flows (`tests/`)
3. Code Development: runnable MVP core in `src/openclaw_sentinel/`

## Implemented Modules
1. Connectors: Datadog/Grafana normalization interfaces
2. Live Connectors: API-backed incident ingestion adapters
3. Policy Engine: deny-by-default allowlists and risk thresholds
4. Control Runtime: cycle runner with approval/block execution paths
5. Verification: action outcome validation
6. Reporting: metric store + Datadog/Grafana export shapes
7. Learning: promotion gate for safe candidate rollout decisions
8. API: health/metrics/digest/run-cycle handlers and server
9. CLI: demo cycle runner and API server launcher

## Run
```bash
cd /Users/sachingill/project/code/ai/openclaw
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m openclaw_sentinel --cycles 1
PYTHONPATH=src python3 -m openclaw_sentinel --serve --host 127.0.0.1 --port 8080
```
