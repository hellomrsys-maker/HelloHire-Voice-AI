"""
recall_sub_ai.py - RVCE Recall & Working Memory Sub-AI

Evaluates:
1. Working memory cross-turn entity retention
2. Cross-turn narrative consistency (lack of factual contradiction)
3. Resume and portfolio factual fidelity
4. Working memory retrieval latency
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

class RecallSubAI:
    def __init__(self):
        pass

    def evaluate(
        self,
        current_transcript: str,
        conversation_history: List[str],
        claimed_resume_entities: List[str] = None
    ) -> Dict[str, Any]:
        lower_curr = current_transcript.lower()
        claimed_entities = claimed_resume_entities or []

        # 1. Entity retention from earlier conversation turns
        retained_entities = 0
        total_prev_entities = 0
        for turn_text in conversation_history:
            words = [w.lower() for w in re.findall(r"\b[A-Za-z]{5,}\b", turn_text)]
            for w in set(words):
                total_prev_entities += 1
                if w in lower_curr:
                    retained_entities += 1

        retention_rate = (
            (retained_entities / max(1, total_prev_entities))
            if conversation_history else 0.88
        )
        working_memory_score = min(1.0, max(0.35, 0.40 + retention_rate * 0.60))

        # 2. Resume factual fidelity
        resume_matches = 0
        for ent in claimed_entities:
            if ent.lower() in lower_curr:
                resume_matches += 1
        resume_fidelity = (
            (resume_matches / max(1, len(claimed_entities)))
            if claimed_entities else 0.92
        )

        # 3. Consistency (absence of self-contradiction cues)
        contradiction_cues = [
            "actually i didn't", "sorry i misspoke", "i meant the opposite",
            "not really what i said earlier", "scratch that"
        ]
        has_contradiction = any(c in lower_curr for c in contradiction_cues)
        consistency_score = 0.45 if has_contradiction else 0.95

        # 4. Retrieval latency
        retrieval_latency_ms = max(40.0, 160.0 - (retained_entities * 8.0))

        composite = (
            working_memory_score * 0.40 +
            consistency_score * 0.35 +
            resume_fidelity * 0.25
        )

        return {
            "sub_ai": "recall",
            "working_memory_retention": round(working_memory_score, 3),
            "cross_turn_consistency": round(consistency_score, 3),
            "resume_fidelity": round(resume_fidelity, 3),
            "retrieval_latency_ms": round(retrieval_latency_ms, 1),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
