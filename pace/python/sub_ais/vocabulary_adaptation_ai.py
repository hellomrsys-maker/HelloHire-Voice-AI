"""
vocabulary_adaptation_ai.py — Evaluates vocabulary complexity adjustment based on interviewer cues.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

SIMPLIFICATION_CUES = [
    "in simple terms", "simply put", "explain like i'm 5", "eli5",
    "high-level summary", "for a non-technical", "in layman's terms",
    "give me the elevator pitch", "plain english"
]

DEEP_DIVE_CUES = [
    "deep dive", "technical specifics", "exact algorithm", "mathematical formulation",
    "low-level details", "under the hood", "concrete implementation details", "edge cases"
]

TECHNICAL_JARGON = [
    "idempotency", "linearizability", "byzantine", "concurrency", "asynchronous",
    "microservices", "raft", "paxos", "sharding", "backpressure", "hashmap", "mutex"
]


class VocabularyAdaptationAI:
    """
    Evaluates whether the candidate tunes their vocabulary complexity
    when prompted for simple explanations or deep dives.
    """

    def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        p_clean = prompt.lower()
        r_clean = response.lower()

        wants_simple = any(cue in p_clean for cue in SIMPLIFICATION_CUES)
        wants_deep = any(cue in p_clean for cue in DEEP_DIVE_CUES)

        words = re.findall(r"\b[a-z0-9\-]+\b", r_clean)
        jargon_count = sum(1 for term in TECHNICAL_JARGON if term in r_clean)

        if wants_simple:
            target = "SIMPLE"
            # When asked for simplicity, jargon should be minimized
            if jargon_count == 0:
                compliance = 0.95
            elif jargon_count <= 1:
                compliance = 0.70
            else:
                compliance = max(0.20, 0.60 - jargon_count * 0.15)
        elif wants_deep:
            target = "DEEP"
            # When asked for depth, substantive technical markers should be present
            if jargon_count >= 2:
                compliance = 0.95
            elif jargon_count == 1:
                compliance = 0.75
            else:
                compliance = 0.40
        else:
            target = "BALANCED"
            compliance = 0.80

        return {
            "target_complexity": target,
            "compliance_score": round(compliance, 3),
            "jargon_detected": jargon_count,
            "wants_simplification": wants_simple,
            "wants_deep_dive": wants_deep,
            "is_adapted": compliance >= 0.70
        }
