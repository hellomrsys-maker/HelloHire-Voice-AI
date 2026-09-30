"""
affect_valence_ai.py — Positive/Negative/Neutral Emotional Tone Detection Sub-AI (ECSE)
"""
from __future__ import annotations
from typing import Dict, Any

class AffectValenceAI:
    POS_CUES = [
        "excited", "thrilled", "passionate", "delighted", "love", "genuinely",
        "absolutely", "fantastic", "proud", "confident", "energized", "eager",
        "honored", "optimistic", "glad", "happy", "inspired"
    ]
    NEG_CUES = [
        "unfortunately", "difficult", "struggle", "challenging", "frustrat",
        "anxious", "concerned", "worried", "hesitant", "doubt", "nervous",
        "disappointed", "dread", "problematic", "failing"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        pos = min(1.0, sum(0.12 for c in self.POS_CUES if c in l))
        neg = min(1.0, sum(0.12 for c in self.NEG_CUES if c in l))
        valence = max(-1.0, min(1.0, pos - neg))
        composite = min(1.0, max(0.0, 0.5 + valence * 0.5))
        return {
            "sub_ai": "affect_valence",
            "positive_affect": round(pos, 3),
            "negative_affect": round(neg, 3),
            "valence_score": round(valence, 3),
            "composite_score": round(composite, 3)
        }
