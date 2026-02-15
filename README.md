# OpenClaw Sentinel

OpenClaw Sentinel is a policy-gated 24x7 AI incident operations core with bounded autonomy, integration-ready ingestion, and safe promotion gates for self-improvement.

## Objective Coverage
1. Spec Drafting: complete (`docs/OPENCLAW_SPEC.md`, `docs/DELIVERY_LEVELS.md`)
2. Test Cases: complete for core safety/runtime flows (`tests/`)
3. Code Development: runnable MVP core in `src/openclaw_sentinel/`

## Implemented Modules
1. Connectors: Datadog/Grafana normalization interfaces
2. Policy Engine: deny-by-default allowlists and risk thresholds
3. Control Runtime: cycle runner with approval/block execution paths
4. Verification: action outcome validation
5. Reporting: metric store + Datadog/Grafana export shapes
6. Learning: promotion gate for safe candidate rollout decisions
7. CLI: demo cycle runner

## Run
```bash
cd /Users/sachingill/project/code/ai/openclaw
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m openclaw_sentinel --cycles 1
```
