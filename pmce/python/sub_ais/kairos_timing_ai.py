"""
kairos_timing_ai.py — Timing & Situational Appropriateness Sub-AI (PMCE)
"""
from __future__ import annotations
from typing import Dict, Any

class KairosAI:
    TRANSITION_CUES = [
        "building on that point", "given what you just mentioned", "furthermore",
        "consequently", "now is the time", "critical moment", "inflection point"
    ]
    CONTEXT_ANCHORS = [
        "as you mentioned earlier", "referring to your point", "as we discussed",
        "as you noted", "to your earlier question"
    ]

    def evaluate(self, text: str, turn_number: int = 1) -> Dict[str, Any]:
        l = text.lower()
        trans = sum(1 for t in self.TRANSITION_CUES if t in l)
        anchors = sum(1 for a in self.CONTEXT_ANCHORS if a in l)
        
        # Pacing fit: earlier turns moderate, later turns reward anchors
        pacing_fit = 1.0 if turn_number >= 3 else 0.85
        composite = min(1.0, 0.35 + trans * 0.20 + anchors * 0.25) * pacing_fit
        return {
            "sub_ai": "kairos",
            "transition_cues": trans,
            "context_anchors": anchors,
            "situational_fit": round(pacing_fit, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
