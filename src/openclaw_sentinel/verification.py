from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .models import Action, ActionOutcome


@dataclass
class VerificationService:
    """Validates action execution using deterministic mock checks for v1 core."""

    failure_keywords: tuple[str, ...] = ("fail", "timeout", "error")
    synthetic_metrics: Dict[str, float] = field(default_factory=dict)

    def verify(self, action: Action, executor_result: str) -> ActionOutcome:
        result = executor_result.lower()
        success = not any(keyword in result for keyword in self.failure_keywords)
        return ActionOutcome(action=action, success=success, details=executor_result)
