"""
interdisciplinary_bridge_ai.py — Interdisciplinary Synthesis & Domain Translation Sub-AI (CDIE)

Evaluates whether the candidate translates principles across domains rather than just
using superficial buzzwords.
"""
from __future__ import annotations
from typing import Dict, Any

class InterdisciplinaryBridgeAI:
    BRIDGE_CUES = [
        "cross-disciplinary", "interdisciplinary", "first-principles translation",
        "mapping principles", "isomorphic", "structural equivalence", "conceptual transfer",
        "borrowed the paradigm from", "adapted from the field of"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        bridge_hits = sum(1 for c in self.BRIDGE_CUES if c in l)
        
        # Check depth of translation: looks for causal explanation of why the transfer works
        causal_cues = ["because the underlying", "due to the shared property", "shares the same dynamic", "governed by the same law"]
        causal_hits = sum(1 for cc in causal_cues if cc in l)

        synthesis_score = min(1.0, 0.30 + bridge_hits * 0.30 + causal_hits * 0.25)
        return {
            "sub_ai": "interdisciplinary_bridge",
            "bridge_cues_found": bridge_hits,
            "causal_grounding_hits": causal_hits,
            "synthesis_depth": round(synthesis_score, 3),
            "composite_score": round(synthesis_score, 3)
        }
