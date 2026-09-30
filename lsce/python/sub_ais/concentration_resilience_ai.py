"""
concentration_resilience_ai.py — Evaluates focus retention and completeness on complex multi-part questions.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List


class ConcentrationResilienceAI:
    """
    Evaluates whether the candidate maintains concentration to address all parts
    of multi-clause inquiries, especially late in an interview.
    """

    def evaluate(self, question: str, answer: str) -> Dict[str, Any]:
        q_clean = question.lower()
        a_clean = answer.lower()

        # Count sub-questions / imperatives in prompt
        question_marks = q_clean.count("?")
        has_and = " and " in q_clean or " as well as " in q_clean
        sub_prompts = max(question_marks, 2 if has_and else 1)

        # Look for answering markers ("regarding", "secondly", "to your first point", etc.)
        structured_markers = [
            "first", "second", "additionally", "furthermore", "regarding",
            "to answer your question about", "on the other hand", "finally"
        ]
        marker_hits = sum(1 for m in structured_markers if m in a_clean)

        answer_words = len(re.findall(r"\b\w+\b", a_clean))

        # Expected elaboration
        expected_words = sub_prompts * 25
        length_ratio = min(1.0, answer_words / max(expected_words, 1))

        resilience = min(1.0, max(0.0, 0.35 + (length_ratio * 0.45) + min(marker_hits * 0.10, 0.20)))

        return {
            "resilience_score": round(resilience, 3),
            "sub_prompts_detected": sub_prompts,
            "structured_marker_count": marker_hits,
            "answer_word_count": answer_words,
            "has_high_resilience": resilience >= 0.65
        }
