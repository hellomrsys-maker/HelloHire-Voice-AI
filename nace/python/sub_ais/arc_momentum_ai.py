"""
arc_momentum_ai.py — Evaluates story progression velocity and narrative forward momentum.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

FORWARD_MOMENTUM_MARKERS = [
    "first", "then", "next", "subsequently", "following that",
    "after that", "in parallel", "finally", "to summarize",
    "looking forward", "key takeaway", "what i learned"
]

STAGNATION_MARKERS = [
    "you know", "like i said", "as i mentioned before", "going back to",
    "um", "uh", "anyway so yeah", "and stuff like that"
]


class ArcMomentumAI:
    """
    Evaluates whether the candidate drives their narrative forward toward a conclusion
    versus rambling or cycling circularly.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()
        words = re.findall(r"\b[a-z0-9\-]+\b", cleaned)
        word_count = max(len(words), 1)

        forward_hits = [m for m in FORWARD_MOMENTUM_MARKERS if m in cleaned]
        stagnation_hits = [m for m in STAGNATION_MARKERS if m in cleaned]

        forward_density = min(1.0, len(forward_hits) / max(word_count / 30.0, 1.0))
        stagnation_density = min(1.0, len(stagnation_hits) / max(word_count / 25.0, 1.0))

        base_momentum = 0.40
        momentum = min(1.0, max(0.0, base_momentum + (forward_density * 0.45) - (stagnation_density * 0.35)))

        return {
            "momentum_score": round(momentum, 3),
            "forward_transitions_count": len(forward_hits),
            "stagnation_markers_count": len(stagnation_hits),
            "forward_density": round(forward_density, 3),
            "stagnation_density": round(stagnation_density, 3),
            "has_forward_drive": momentum >= 0.50
        }
