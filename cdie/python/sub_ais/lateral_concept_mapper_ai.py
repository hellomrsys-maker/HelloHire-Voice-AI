"""
lateral_concept_mapper_ai.py — Lateral Thinking & Orthogonal Solution Mapping Sub-AI (CDIE)

Identifies non-linear, orthogonal, and counter-intuitive solutions vs brute-force scaling.
"""
from __future__ import annotations
from typing import Dict, Any

class LateralConceptMapperAI:
    LATERAL_CUES = [
        "orthogonal approach", "counter-intuitive", "inverted the problem",
        "instead of brute-forcing", "sidestepped the bottleneck", "reframed the constraint",
        "unconventional architecture", "novel paradigm", "lateral thinking"
    ]
    BRUTE_FORCE_CUES = [
        "just added more machines", "threw more hardware at it", "scaled up instances",
        "did it manually", "hoped for the best", "brute-force"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        lat_hits = sum(1 for c in self.LATERAL_CUES if c in l)
        brute_hits = sum(1 for b in self.BRUTE_FORCE_CUES if b in l)

        lateral_score = min(1.0, 0.35 + lat_hits * 0.28 - brute_hits * 0.20)
        lateral_score = max(0.1, lateral_score)

        return {
            "sub_ai": "lateral_concept_mapper",
            "lateral_cues": lat_hits,
            "brute_force_signals": brute_hits,
            "lateral_inventiveness": round(lateral_score, 3),
            "composite_score": round(lateral_score, 3)
        }
