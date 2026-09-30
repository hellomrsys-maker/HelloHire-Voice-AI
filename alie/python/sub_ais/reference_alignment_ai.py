"""
reference_alignment_ai.py — Referential Pronoun & Topic Frame Alignment Sub-AI (ALIE)

Evaluates whether the candidate's answer is anchored to the
interviewer's exact conceptual framing — not a generic response.
"""
from __future__ import annotations
import re
from typing import Dict, Any

class ReferenceAlignmentAI:
    def evaluate(self, question: str, answer: str) -> Dict[str, Any]:
        q = question.lower()
        a = answer.lower()
        q_words = set(re.findall(r'\b[a-z]{4,}\b', q))
        a_words = set(re.findall(r'\b[a-z]{4,}\b', a))

        # Lexical mirroring
        shared = q_words & a_words
        jaccard = len(shared) / max(1, len(q_words | a_words))
        lexical_mirror = min(1.0, jaccard * 3.0)

        # Pronoun echo: interviewer says "you/your" → candidate says "I/my/we/our"
        q_addresses_candidate = ("you" in q or "your" in q)
        a_uses_first_person = bool(re.search(r'\b(i|my|we|our|me)\b', a))
        pronoun_echo = 0.95 if (q_addresses_candidate and a_uses_first_person) else 0.40

        # Topic frame: content words from question found in answer
        frame_hits = sum(1 for w in q_words if w in a_words)
        topic_frame = min(1.0, 0.30 + frame_hits * 0.15)

        composite = pronoun_echo * 0.35 + lexical_mirror * 0.35 + topic_frame * 0.30
        return {
            "sub_ai": "reference_alignment",
            "lexical_mirror_score": round(lexical_mirror, 3),
            "pronoun_echo_score": round(pronoun_echo, 3),
            "topic_frame_retention": round(topic_frame, 3),
            "shared_vocabulary": list(shared)[:8],
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
