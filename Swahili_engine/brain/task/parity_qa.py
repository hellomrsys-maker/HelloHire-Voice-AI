"""
Swahili parity Q&A task. Understands both question and context in English
first (English-pivot), then selects the best-matching context sentence.
"""

from __future__ import annotations
from typing import Dict, Any, List

from engine_common.english_pivot import EnglishPivotComprehension
from engine_common.language_profile import get_profile


class SwahiliParityQA:
    def __init__(self) -> None:
        self.profile = get_profile("Swahili_engine")
        self.pivot = EnglishPivotComprehension(self.profile)

    def answer(self, question: str, context: str) -> Dict[str, Any]:
        q_tokens = set(self.pivot.comprehend(question).english_tokens)
        best, best_overlap, best_sent = None, -1, ""
        buf: List[str] = []
        cur = ""
        for ch in context:
            cur += ch
            if ch in self.profile.sentence_terminators:
                buf.append(cur.strip()); cur = ""
        if cur.strip():
            buf.append(cur.strip())
        for sent in buf or [context]:
            s_tokens = set(self.pivot.comprehend(sent).english_tokens)
            overlap = len(q_tokens & s_tokens)
            if overlap > best_overlap:
                best_overlap, best_sent = overlap, sent
        return {
            "language": self.profile.language_name,
            "question": question,
            "answer": best_sent,
            "english_question": " ".join(sorted(q_tokens)),
            "token_overlap": max(0, best_overlap),
        }
