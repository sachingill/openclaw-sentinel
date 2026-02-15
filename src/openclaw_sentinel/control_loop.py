from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Tuple

from .models import Action, Incident, LoopResult, RiskProfile
from .policy import PolicyEngine

ActionPlanner = Callable[[Incident], Iterable[Tuple[Action, RiskProfile]]]
ActionExecutor = Callable[[Action], str]


@dataclass
class ControlLoop:
    policy_engine: PolicyEngine
    planner: ActionPlanner
    executor: ActionExecutor
    execution_log: List[str] = field(default_factory=list)

    def run_once(self, incident: Incident) -> LoopResult:
        decisions = []
        for action, risk in self.planner(incident):
            decision = self.policy_engine.evaluate(action, risk)
            decisions.append(decision)
            if decision.approved:
                result = self.executor(action)
                self.execution_log.append(f"{action.id}:{result}")
            else:
                self.execution_log.append(f"{action.id}:blocked:{decision.reason}")
        return LoopResult(incident=incident, decisions=decisions)
