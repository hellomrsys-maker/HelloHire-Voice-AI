"""
qa_relevance_ai.py — Question-Answer Topical Relevance Sub-AI (ALIE)

Evaluates whether the answer actually addresses what was asked —
detecting generic "filler" responses vs. specifically on-topic ones.
"""
from __future__ import annotations
import re
from typing import Dict, Any

class QARelevanceAI:
    GENERIC_FILLERS = [
        "that's a great question", "i believe", "in my opinion", "generally speaking",
        "it depends", "as i mentioned", "to be honest", "at the end of the day"
    ]
    SPECIFICITY_MARKERS = ["specifically", "for instance", "in that case", "precisely",
                           "to be exact", "in particular", "concretely"]

    def evaluate(self, question: str, answer: str) -> Dict[str, Any]:
        q = question.lower()
        a = answer.lower()

        q_content = set(re.findall(r'\b[a-z]{4,}\b', q))
        a_words   = re.findall(r'\b[a-z]{3,}\b', a)

        # On-topic ratio
        on_topic_count = sum(1 for w in a_words if w in q_content)
        on_topic_ratio = min(1.0, (on_topic_count / max(1, len(a_words))) * 8.0)

        # Specificity: numbers, %, named specifics, or explicit markers
        has_number = bool(re.search(r'\d', answer))
        has_percent = '%' in answer
        has_specific_marker = any(m in a for m in self.SPECIFICITY_MARKERS)
        specificity = min(1.0, 0.30 + (int(has_number) + int(has_percent) + int(has_specific_marker)) * 0.25)

        # Generic filler penalty
        generic_hits = sum(1 for g in self.GENERIC_FILLERS if g in a)
        filler_penalty = min(0.40, generic_hits * 0.12)

        # Completeness: answer length relative to question complexity
        completeness = min(1.0, max(0.20, len(a_words) / max(5, len(q_content) * 4)))

        composite = (on_topic_ratio * 0.30 + completeness * 0.20 +
                     specificity * 0.40 + (1.0 - filler_penalty) * 0.10)

        return {
            "sub_ai": "qa_relevance",
            "on_topic_ratio": round(on_topic_ratio, 3),
            "specificity_score": round(specificity, 3),
            "completeness_score": round(completeness, 3),
            "filler_penalty": round(filler_penalty, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
