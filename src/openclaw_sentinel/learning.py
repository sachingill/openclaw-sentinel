from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EvalScore:
    precision: float
    recall: float
    false_critical_rate: float
    p95_latency_sec: float
    safety_regression: bool


@dataclass(frozen=True)
class PromotionThresholds:
    min_precision: float = 0.75
    min_recall: float = 0.70
    max_false_critical_rate: float = 0.10
    max_p95_latency_sec: float = 90.0


@dataclass
class PromotionResult:
    approved: bool
    reason: str
    metrics: Dict[str, float]


class PromotionGate:
    def __init__(self, thresholds: PromotionThresholds | None = None) -> None:
        self.thresholds = thresholds or PromotionThresholds()

    def evaluate(self, candidate: EvalScore) -> PromotionResult:
        if candidate.safety_regression:
            return PromotionResult(False, "safety_regression", self._metrics(candidate))
        if candidate.precision < self.thresholds.min_precision:
            return PromotionResult(False, "precision_below_threshold", self._metrics(candidate))
        if candidate.recall < self.thresholds.min_recall:
            return PromotionResult(False, "recall_below_threshold", self._metrics(candidate))
        if candidate.false_critical_rate > self.thresholds.max_false_critical_rate:
            return PromotionResult(False, "false_critical_rate_too_high", self._metrics(candidate))
        if candidate.p95_latency_sec > self.thresholds.max_p95_latency_sec:
            return PromotionResult(False, "latency_too_high", self._metrics(candidate))
        return PromotionResult(True, "approved", self._metrics(candidate))

    def _metrics(self, score: EvalScore) -> Dict[str, float]:
        return {
            "precision": score.precision,
            "recall": score.recall,
            "false_critical_rate": score.false_critical_rate,
            "p95_latency_sec": score.p95_latency_sec,
        }
