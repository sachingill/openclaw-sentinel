from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List


class AutonomyLevel(IntEnum):
    L0_OBSERVE = 0
    L1_ASSIST = 1
    L2_BOUNDED_AUTO = 2
    L3_RESTRICTED = 3


@dataclass(frozen=True)
class Incident:
    id: str
    tenant_id: str
    source: str
    severity: str
    summary: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    id: str
    incident_id: str
    tenant_id: str
    action_type: str
    command: str
    requires_high_privilege: bool = False
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RiskProfile:
    impact: int
    blast_radius: int
    reversibility: int
    confidence: float

    def score(self) -> float:
        # Higher reversibility should reduce risk.
        inverse_reversibility = 6 - self.reversibility
        weighted = (self.impact * 0.35) + (self.blast_radius * 0.35) + (inverse_reversibility * 0.2)
        confidence_penalty = (1.0 - self.confidence) * 5 * 0.1
        return round(weighted + confidence_penalty, 3)


@dataclass
class Decision:
    approved: bool
    reason: str
    required_level: AutonomyLevel
    action: Action


@dataclass
class LoopResult:
    incident: Incident
    decisions: List[Decision]


@dataclass(frozen=True)
class ActionOutcome:
    action: Action
    success: bool
    details: str


@dataclass
class CycleSummary:
    cycle_id: str
    incidents_seen: int
    actions_approved: int
    actions_blocked: int
    actions_succeeded: int
