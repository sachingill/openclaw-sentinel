from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

from .models import Action, AutonomyLevel, Decision, RiskProfile


@dataclass
class PolicyRule:
    tenant_id: str
    max_autonomy: AutonomyLevel = AutonomyLevel.L1_ASSIST
    allowlisted_action_types: Set[str] = field(default_factory=set)
    blocked_commands: Set[str] = field(default_factory=set)
    max_risk_score_for_auto: float = 2.8


class PolicyEngine:
    def __init__(self, rule: PolicyRule) -> None:
        self.rule = rule

    def evaluate(self, action: Action, risk: RiskProfile) -> Decision:
        if action.tenant_id != self.rule.tenant_id:
            return Decision(False, "tenant_mismatch", AutonomyLevel.L3_RESTRICTED, action)

        if action.action_type not in self.rule.allowlisted_action_types:
            return Decision(False, "action_type_not_allowlisted", AutonomyLevel.L3_RESTRICTED, action)

        for blocked in self.rule.blocked_commands:
            if blocked in action.command:
                return Decision(False, "command_blocked", AutonomyLevel.L3_RESTRICTED, action)

        if action.requires_high_privilege:
            return Decision(False, "high_privilege_requires_human", AutonomyLevel.L3_RESTRICTED, action)

        risk_score = risk.score()
        if risk_score > self.rule.max_risk_score_for_auto:
            return Decision(False, f"risk_too_high:{risk_score}", AutonomyLevel.L1_ASSIST, action)

        if self.rule.max_autonomy < AutonomyLevel.L2_BOUNDED_AUTO:
            return Decision(False, "autonomy_level_requires_human", AutonomyLevel.L1_ASSIST, action)

        return Decision(True, "approved_for_auto", AutonomyLevel.L2_BOUNDED_AUTO, action)
