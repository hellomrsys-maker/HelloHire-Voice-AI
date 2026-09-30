"""
verbal_sub_ai.py - RVCE Verbal Articulation & Fluency Sub-AI

Evaluates:
1. Speech rate & cadence (optimal 130 - 165 WPM band)
2. Linguistic register compliance (executive / professional vs colloquial)
3. Disfluent filler word mitigation
4. Lexical diversity (Type-Token Ratio & vocabulary density)
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

class VerbalSubAI:
    def __init__(self):
        self.fillers = [
            "um", "uh", "like", "you know", "sort of", "kind of", "basically", "actually", "literally"
        ]
        self.colloquialisms = [
            "gonna", "wanna", "kinda", "sorta", "dunno", "dude", "stuff like that", "you know what i mean"
        ]

    def evaluate(self, transcript: str, measured_wpm: float = 145.0) -> Dict[str, Any]:
        lower = transcript.lower()
        words = re.findall(r"\b[A-Za-z0-9'-]+\b", lower)
        total_words = max(1, len(words))

        # 1. Pacing WPM score
        if 130.0 <= measured_wpm <= 165.0:
            wpm_score = 1.0
        else:
            wpm_diff = min(abs(measured_wpm - 145.0), 100.0)
            wpm_score = max(0.2, 1.0 - (wpm_diff / 100.0))

        # 2. Register compliance
        colloquial_hits = sum(1 for c in self.colloquialisms if c in lower)
        register_compliance = max(0.1, 1.0 - (colloquial_hits * 0.25))

        # 3. Filler penalty
        filler_hits = 0
        for f in self.fillers:
            if " " in f:
                filler_hits += len(re.findall(re.escape(f), lower))
            else:
                filler_hits += words.count(f)
        filler_penalty = min(0.6, filler_hits * 0.04)

        # 4. Lexical diversity
        unique_words = len(set(words))
        ttr = unique_words / total_words
        vocabulary_density = min(1.0, max(0.2, ttr * 1.3))

        composite = (
            wpm_score * 0.30 +
            register_compliance * 0.30 +
            vocabulary_density * 0.25 +
            (1.0 - filler_penalty) * 0.15
        )

        return {
            "sub_ai": "verbal",
            "wpm_score": round(wpm_score, 3),
            "measured_wpm": measured_wpm,
            "register_compliance": round(register_compliance, 3),
            "filler_penalty": round(filler_penalty, 3),
            "vocabulary_density": round(vocabulary_density, 3),
            "type_token_ratio": round(ttr, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
