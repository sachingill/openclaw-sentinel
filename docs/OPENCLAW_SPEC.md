# OpenClaw Sentinel Product Specification

Version: v0.1
Date: 2026-02-15
Owner: OpenClaw Sentinel Team

## 1. Product Summary
OpenClaw Sentinel is a 24x7 AI operations agent for engineering teams that continuously ingests incidents, proposes or executes bounded actions, verifies outcomes, and improves safely through controlled offline learning.

Primary outcome: reduce incident triage and resolution effort while preserving strict safety and auditability.

## 2. Goals and Non-Goals

### Goals
- Provide always-on incident triage and response support.
- Support policy-gated autonomy levels from observe-only to bounded auto-action.
- Integrate natively with Datadog and Grafana reporting ecosystems.
- Enable safe, measurable self-improvement through evaluation and promotion gates.
- Provide tenant-safe, auditable operations suitable for enterprise adoption.

### Non-Goals (v1)
- Unrestricted autonomous remediation.
- Live self-modifying production code.
- Broad generic agent capabilities beyond incident operations.

## 3. Target Users and ICP
- Primary ICP: B2B SaaS engineering organizations (10-500 engineers).
- Primary users: on-call engineers, SREs, engineering managers.
- Secondary users: security and platform teams auditing AI actions.

## 4. Core Use Cases
- Continuous incident summarization from alerts, logs, and tickets.
- Severity recommendation with confidence score and explanation.
- Runbook suggestion and bounded execution for approved low-risk actions.
- Post-incident timeline and reporting generation.
- Weekly safety/effectiveness reports to teams.

## 5. Functional Requirements

### 5.1 Always-On Control Loop
OpenClaw Sentinel runs continuously as:
1. Sense: ingest incidents/events continuously.
2. Decide: classify, prioritize, and propose actions with risk/confidence.
3. Act: execute only policy-approved actions.
4. Verify: observe post-action metrics/SLO changes.
5. Learn: store outcomes for offline evaluation and tuning.

### 5.2 Autonomy Levels
- L0 Observe: read + report only.
- L1 Assist: suggest actions; human approval required.
- L2 Bounded Auto: auto-execute allowlisted low-risk runbooks.
- L3 Restricted: high-risk actions always require explicit human approval.

Each tenant defines allowed level per action class.

### 5.3 Policy Engine
Policy checks before any action:
- Risk score from impact, blast radius, reversibility, confidence.
- Allowlist match for tools/endpoints/commands.
- Tenant boundary and RBAC check.
- PII/secret redaction before model calls.

### 5.4 Integrations
- Datadog: events, logs, monitors, dashboards, metrics export.
- Grafana stack: Prometheus metrics, Loki logs, Tempo traces.
- Ticketing: Linear/Jira (v1 can start with one provider).
- Notification: Slack for summaries and approval workflow.

### 5.5 Reporting
Provide near-real-time and periodic reporting:
- KPI API endpoints (`/reporting/kpi`).
- Prebuilt dashboards for Datadog and Grafana.
- Weekly digest (safety + quality + performance).

## 6. Non-Functional Requirements
- Availability target: 99.9% monthly for core triage pipeline.
- End-to-end triage suggestion p95 latency < 90 seconds.
- Multi-tenant data isolation with tenant-scoped access controls.
- Full auditability of model inputs, decisions, tool calls, and approvals.
- Idempotent action execution with retries and DLQ.

## 7. Safety and Governance
- Human approval mandatory for high-risk and out-of-policy actions.
- No production code self-modification.
- Offline-only optimization loop with controlled promotion.
- Circuit breakers for confidence drops, anomaly spikes, or tool failures.
- Immutable audit record for compliance and postmortems.

## 8. Data Model (Minimum)
- Tenant
- IncidentEvent
- IncidentCase
- AISuggestion
- ActionExecution
- ApprovalDecision
- EvaluationRun
- PolicyVersion
- AuditRecord

## 9. System Architecture

### 9.1 Components
- Connectors Service: pulls incidents from Datadog/Grafana/ticketing.
- Normalization Service: maps source data to common incident schema.
- Policy Engine: risk scoring, allowlists, RBAC, redaction.
- Agent Orchestrator: prompts, planning, tool-calling, confidence scoring.
- Action Runner: executes approved bounded runbooks.
- Verification Service: validates outcomes against defined SLO/KPI checks.
- Learning Pipeline: nightly evaluation and candidate generation.
- Reporting Service: KPI rollups and dashboard APIs.
- Audit Service: append-only event history.

### 9.2 Telemetry Standard
Use OpenTelemetry across all components:
- Metrics -> Prometheus (Grafana) + Datadog metrics exporter.
- Traces -> Tempo + Datadog APM.
- Logs -> Loki + Datadog logs.

## 10. KPI Definitions
Primary KPIs:
- Triage time reduction (%).
- Suggestion acceptance rate (%).
- Auto-action success rate (%).
- Human override rate (%).
- False-critical recommendation rate (%).
- MTTA/MTTR delta vs baseline.

Safety KPIs:
- Policy violation attempts blocked.
- Rollback rate of auto-actions.
- Confidence drift index.
- Incidents with incomplete audit trail (target: 0).

## 11. Continuous Improvement (Safe)

### 11.1 Nightly Evaluation Loop
- Build candidate prompt/policy/tool configurations.
- Replay on golden incident dataset + recent sampled incidents.
- Compare against production baseline.
- Generate promotion recommendation with expected KPI deltas.

### 11.2 Promotion Gates
A candidate can promote only if:
- No safety regression.
- False-critical rate below threshold.
- Precision/recall above class thresholds.
- p95 latency not degraded beyond threshold.
- Canary (5-10% traffic) success for two consecutive windows.
- Human approver signs off.

## 12. 30-Day Delivery Plan

### Week 1
- Define incident schema and policy contract.
- Build initial connectors (Datadog + one ticket system).
- Implement audit/event model and storage.
- Add baseline OTel instrumentation.

### Week 2
- Ship L0/L1 control loop and Slack approval flow.
- Add KPI API and first reporting rollups.
- Stand up OTel Collector dual export (Grafana + Datadog).

### Week 3
- Add L2 bounded runbooks for one low-risk class.
- Implement verification checks + circuit breakers.
- Publish dashboard packs (Datadog/Grafana).

### Week 4
- Launch pilot with 2-3 design partners.
- Run evaluation/promotion pipeline in shadow mode.
- Tune thresholds and finalize GA criteria.

## 13. Release Criteria (Pilot to GA)
- 4 weeks stable operation with no critical safety incidents.
- >= 30% median triage time reduction in pilot accounts.
- >= 60% suggestion acceptance in scoped use cases.
- Complete audit coverage for 100% of actions.
- Documented runbooks and on-call procedures.

## 14. Risks and Mitigations
- Integration API instability -> connector adapters + retries + versioned clients.
- False confidence -> calibration, lower auto thresholds, forced approval fallback.
- Tenant data leakage risk -> hard partitioning + scoped tokens + continuous tests.
- Alert noise overload -> prioritization model + deduplication + suppression rules.

## 15. Open Decisions
- First ticketing provider for v1 (Linear vs Jira).
- Storage engine for long-term reporting at scale (Postgres vs ClickHouse).
- Initial low-risk runbook set for L2.

## 16. Initial Backlog Epics
- EPIC-1: Ingestion and Normalization
- EPIC-2: Policy and Safety Engine
- EPIC-3: Agent Orchestration and Suggestions
- EPIC-4: Approval Workflow and Action Runner
- EPIC-5: Verification and Reliability Controls
- EPIC-6: Reporting and Dashboards (Grafana + Datadog)
- EPIC-7: Evaluation, Canary, and Promotion Pipeline
- EPIC-8: Enterprise Controls (RBAC, Audit, Tenant Isolation)
