# OpenClaw Sentinel Delivery Levels

Date: 2026-02-15

## Objective
Ship OpenClaw-Sentinel in iterative levels so progress is reviewable every 20 minutes.

## Level 1: Spec Drafting
Status: Complete

Scope:
- Lock v1 boundaries (24x7 control loop, bounded autonomy, reporting).
- Define safety policy matrix and promotion gates.
- Define integration contracts for Datadog and Grafana.

Exit Criteria:
- Product spec published.
- Delivery levels and acceptance criteria documented.
- Open decisions called out explicitly.

Artifacts:
- `docs/OPENCLAW_SPEC.md`
- `docs/DELIVERY_LEVELS.md`

## Level 2: Test Cases
Status: Complete

Scope:
- Define testable safety invariants before broad code expansion.
- Cover autonomy gates and risk threshold behavior.
- Cover reporting aggregation and outcome tracking.

Exit Criteria:
- Core policy tests pass.
- Control loop execution tests pass.
- Regression tests enforce deny-by-default behavior.

Artifacts:
- `tests/test_policy.py`
- `tests/test_control_loop.py`
- `tests/test_connectors.py`
- `tests/test_service.py`
- `tests/test_learning.py`
- `tests/test_reporting.py`
- `tests/test_runtime.py`

## Level 3: Code Development
Status: Complete (MVP Core)

Scope:
- Implement minimal core services:
  - Incident model and action model
  - Policy engine
  - Control loop executor
  - Reporting metric aggregator
- Keep integration layer adapter-friendly for Datadog/Grafana ingestion/export.

Exit Criteria:
- Local simulation runs.
- Unit tests green.
- Repository ready for next sprint (connectors + APIs).

Artifacts:
- `src/openclaw_sentinel/*`

## Checkpoint Cadence
- Every 20 minutes: push working increments and summary.
- Each checkpoint must include:
  - What changed
  - What passed/failed
  - Next immediate scope
