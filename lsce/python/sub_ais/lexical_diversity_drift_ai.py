"""
lexical_diversity_drift_ai.py — Evaluates vocabulary richness (Type-Token Ratio) and lexical flattening over time.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List


class LexicalDiversityDriftAI:
    """
    Computes lexical richness and tracks whether the candidate's vocabulary narrows
    due to mental exhaustion.
    """

    def __init__(self):
        self.ttr_history: List[float] = []

    def evaluate(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"\b[a-z0-9\-]+\b", text.lower())
        total_tokens = len(words)

        if total_tokens == 0:
            ttr = 0.50
        else:
            unique_types = len(set(words))
            # Standardized / root TTR to reduce length bias
            ttr = unique_types / max(total_tokens, 1)

        self.ttr_history.append(ttr)

        # Baseline is initial 2 turns or 0.65
        baseline = sum(self.ttr_history[:2]) / max(len(self.ttr_history[:2]), 1)
        drift = baseline - ttr if len(self.ttr_history) > 2 else 0.0

        richness_score = min(1.0, max(0.0, ttr * 1.25))

        return {
            "current_ttr": round(ttr, 3),
            "lexical_richness": round(richness_score, 3),
            "diversity_drift": round(max(0.0, drift), 3),
            "total_tokens": total_tokens,
            "unique_types": len(set(words)),
            "is_lexically_rich": richness_score >= 0.55
        }
