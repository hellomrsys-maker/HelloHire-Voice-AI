"""
discourse_repair_ai.py — Discourse Repair & Comprehension Signal Sub-AI (ALIE)

Active listeners ask clarification questions when needed.
This AI detects whether such repair signals are present, appropriate, and well-placed.
"""
from __future__ import annotations
import re
from typing import Dict, Any

class DiscourseRepairAI:
    REPAIR_CUES = [
        r"could you clarify", r"what do you mean by",
        r"did you mean", r"can you elaborate",
        r"just to confirm", r"are you (asking|referring) (about|to)",
        r"let me make sure i understood", r"so if i understand correctly",
        r"to paraphrase", r"in other words, you('re| are) saying"
    ]
    ACTIVE_COMPREHENSION = [
        "i see", "understood", "that makes sense", "absolutely",
        "right, so", "got it", "i follow"
    ]

    def evaluate(self, answer: str, question_was_ambiguous: bool = False) -> Dict[str, Any]:
        a = answer.lower()

        # Count repair signals
        repair_hits = sum(1 for p in self.REPAIR_CUES if re.search(p, a))

        # Count active comprehension signals
        comprehension_hits = sum(1 for c in self.ACTIVE_COMPREHENSION if c in a)

        # Appropriateness logic
        if question_was_ambiguous:
            # Repair is expected and rewarded
            if repair_hits >= 1:
                repair_appropriateness = min(1.0, 0.80 + repair_hits * 0.10)
            else:
                repair_appropriateness = 0.45  # Failed to probe ambiguity
        else:
            # Repair should be selective
            if repair_hits == 0:
                repair_appropriateness = 0.72  # Neutral — didn't need repair
            elif repair_hits <= 2:
                repair_appropriateness = 0.95  # Good active listening
            else:
                repair_appropriateness = max(0.3, 0.95 - (repair_hits - 2) * 0.20)

        comprehension_signal = min(1.0, 0.50 + comprehension_hits * 0.20)

        composite = repair_appropriateness * 0.60 + comprehension_signal * 0.40

        return {
            "sub_ai": "discourse_repair",
            "repair_attempts": repair_hits,
            "repair_appropriateness": round(repair_appropriateness, 3),
            "comprehension_signals": comprehension_hits,
            "comprehension_signal_score": round(comprehension_signal, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
