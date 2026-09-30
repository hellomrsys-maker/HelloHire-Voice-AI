"""
pathos_resonance_ai.py — Emotional Resonance & Audience Empathy Sub-AI (PMCE)
"""
from __future__ import annotations
from typing import Dict, Any

class PathosAI:
    EMOTIONAL_CUES = [
        "pain point", "frustration", "empower", "delight", "transform",
        "impact", "meaningful", "vision", "passion", "burnout", "relief"
    ]
    STORY_CUES = [
        "for example", "imagine if", "one customer", "a memorable situation",
        "we experienced firsthand", "a real-world scenario"
    ]

    def evaluate(self, text: str) -> Dict[str, Any]:
        l = text.lower()
        emo = sum(1 for e in self.EMOTIONAL_CUES if e in l)
        story = sum(1 for s in self.STORY_CUES if s in l)
        resonance = min(1.0, 0.25 + emo * 0.18 + story * 0.22)
        return {
            "sub_ai": "pathos",
            "emotional_cues": emo,
            "story_framing": story,
            "composite_score": round(resonance, 3)
        }
