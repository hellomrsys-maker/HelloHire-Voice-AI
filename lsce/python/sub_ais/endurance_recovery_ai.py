"""
endurance_recovery_ai.py — Evaluates candidate rebound velocity after high-stress or challenging turns.
"""

from __future__ import annotations
from typing import Dict, Any, List


class EnduranceRecoveryAI:
    """
    Evaluates whether performance stabilizes or rebounds immediately after
    challenging technical questions or critical feedback.
    """

    def __init__(self):
        self.performance_history: List[float] = []

    def evaluate(self, current_turn_score: float) -> Dict[str, Any]:
        self.performance_history.append(current_turn_score)
        n = len(self.performance_history)

        if n <= 1:
            rebound = 0.50
            recovery_velocity = 0.0
        else:
            prev = self.performance_history[-2]
            delta = current_turn_score - prev
            recovery_velocity = delta

            if prev < 0.50 and current_turn_score >= 0.60:
                rebound = 0.90  # Strong bounce back from low turn
            elif delta >= 0.0:
                rebound = min(1.0, 0.50 + delta * 0.50)
            else:
                rebound = max(0.10, 0.50 + delta * 0.50)

        return {
            "recovery_score": round(rebound, 3),
            "delta_from_previous": round(recovery_velocity, 3),
            "total_turns": n,
            "has_recovered": rebound >= 0.60
        }
