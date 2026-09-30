"""
fatigue_trajectory_ai.py — Evaluates trajectory of response lengths, cognitive depth, and fatigue degradation.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List


class FatigueTrajectoryAI:
    """
    Monitors degradation of answer volume and structural elaboration across turns.
    """

    def __init__(self):
        self.word_counts: List[int] = []

    def evaluate(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\b\w+\b", text)
        count = len(words)
        self.word_counts.append(count)

        n = len(self.word_counts)
        if n <= 1:
            slope = 0.0
            fatigue_index = 0.0
        else:
            # Simple linear regression slope across turns
            x_mean = (n - 1) / 2.0
            y_mean = sum(self.word_counts) / float(n)
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(self.word_counts))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            slope = (numerator / denominator) if denominator > 0 else 0.0

            # Negative slope indicates potential fatigue
            if slope < -5.0:
                fatigue_index = min(1.0, abs(slope) / 20.0)
            else:
                fatigue_index = 0.0

        stamina = max(0.0, 1.0 - fatigue_index)

        return {
            "current_word_count": count,
            "turn_history_counts": list(self.word_counts),
            "trajectory_slope": round(slope, 3),
            "fatigue_index": round(fatigue_index, 3),
            "stamina_score": round(stamina, 3),
            "is_fatiguing": fatigue_index >= 0.40
        }
