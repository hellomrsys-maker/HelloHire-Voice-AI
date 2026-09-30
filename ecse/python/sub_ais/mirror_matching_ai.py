"""
mirror_matching_ai.py — Vocabulary & Rhythm Mirroring Sub-AI (ECSE)
"""
from __future__ import annotations
import re
from typing import Dict, Any

class MirrorMatchingAI:
    def evaluate(
        self,
        answer: str,
        interviewer_last_turn: str,
        candidate_wpm: float = 145.0,
        interviewer_wpm: float = 140.0
    ) -> Dict[str, Any]:
        al = set(re.findall(r'\b[a-z]{5,}\b', answer.lower()))
        ql = re.findall(r'\b[a-z]{5,}\b', interviewer_last_turn.lower())
        hits = sum(1 for w in ql if w in al)
        vocab_mirror = min(1.0, (hits / max(1, len(ql))) * 3.0)
        wpm_diff = abs(candidate_wpm - interviewer_wpm)
        rhythm_sync = max(0.2, 1.0 - (wpm_diff / 60.0))
        composite = vocab_mirror * 0.50 + rhythm_sync * 0.50
        return {
            "sub_ai": "mirror_matching",
            "vocabulary_mirror": round(vocab_mirror, 3),
            "vocabulary_mirroring": round(vocab_mirror, 3),
            "rhythm_synchrony": round(rhythm_sync, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
