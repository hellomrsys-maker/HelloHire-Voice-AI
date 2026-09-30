"""
micro_disagreement_ai.py — Hedges, Face-Saving, and Silent Resistance Sub-AI (ECSE)
"""
from __future__ import annotations
from typing import Dict, Any

class MicroDisagreementAI:
    HEDGES = [
        "somewhat", "in a way", "to some extent", "it depends", "kind of",
        "sort of", "perhaps", "maybe", "i might suggest", "not necessarily", "with respect"
    ]
    BLUNT = [
        "you are wrong", "incorrect", "false", "disagree completely",
        "that makes no sense", "ridiculous", "obviously not"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        h = sum(1 for cue in self.HEDGES if cue in l)
        b = sum(1 for cue in self.BLUNT if cue in l)
        disagree = min(1.0, h * 0.15 + (0.35 if "disagree" in l else 0.0))
        tact = max(0.1, 1.0 - b * 0.40)
        composite = max(0.0, 1.0 - disagree) if h > 0 else 0.95
        return {
            "sub_ai": "micro_disagreement",
            "hedge_count": h,
            "disagreement_signal": round(disagree, 3),
            "diplomatic_tact": round(tact, 3),
            "blunt_confrontation_signals": b,
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
