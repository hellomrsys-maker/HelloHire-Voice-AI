"""
rapport_building_ai.py — Warmth, Collective Identity, and Bonding Language Sub-AI (ECSE)
"""
from __future__ import annotations
from typing import Dict, Any

class RapportBuildingAI:
    WARMTH = [
        "i appreciate", "thank you for", "that's insightful", "i completely agree",
        "i understand", "i empathize", "that resonates", "absolutely", "i see your point",
        "great question", "pleasure to discuss", "honored to meet"
    ]
    COLLECTIVE = [
        "we ", "our team", "together", "collectively", "as a group", "collaborat",
        "co-create", "shared mission", "cross-functional"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        w = sum(1 for c in self.WARMTH if c in l)
        c = sum(1 for cue in self.COLLECTIVE if cue in l)
        warmth = min(1.0, w * 0.25)
        collective = min(1.0, c * 0.22)
        bonding = min(1.0, (warmth + collective) * 0.60 + 0.35)
        composite = warmth * 0.40 + collective * 0.20 + bonding * 0.40
        return {
            "sub_ai": "rapport_building",
            "warmth_density": round(warmth, 3),
            "collective_identity": round(collective, 3),
            "bonding_score": round(bonding, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
