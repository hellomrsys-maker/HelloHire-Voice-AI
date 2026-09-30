"""
politeness_register_ai.py — Formal/Informal Calibration & Courtesy Markers Sub-AI (ECSE)
"""
from __future__ import annotations
from typing import Dict, Any

class PolitenessRegisterAI:
    COURTESY = [
        "thank you", "i appreciate", "of course", "please", "my pleasure",
        "delighted", "certainly", "indeed", "with pleasure", "happy to"
    ]
    CRUDE = [
        "whatever", "don't care", "bluntly", "stupid", "dumb", "bullshit", "crap"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        ct = sum(1 for c in self.COURTESY if c in l)
        cr = sum(1 for c in self.CRUDE if c in l)
        courtesy = min(1.0, ct * 0.20)
        formal = max(0.0, 1.0 - cr * 0.35)
        composite = courtesy * 0.40 + formal * 0.60
        return {
            "sub_ai": "politeness_register",
            "courtesy_markers": ct,
            "formal_compliance": round(formal, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
