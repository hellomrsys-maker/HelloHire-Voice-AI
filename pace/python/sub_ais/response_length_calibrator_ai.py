"""
response_length_calibrator_ai.py — Evaluates candidate conciseness vs elaboration calibration.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

BREVITY_CUES = [
    "in one sentence", "briefly", "yes or no", "quick check",
    "in 10 seconds", "just a quick summary", "short answer"
]

ELABORATION_CUES = [
    "walk me through", "tell me about a time", "detailed overview",
    "describe the full architecture", "comprehensive analysis", "deep dive"
]


class ResponseLengthCalibratorAI:
    """
    Evaluates whether the candidate respects length constraints: giving crisp,
    concise answers when requested, or providing thorough elaboration when invited.
    """

    def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        p_clean = prompt.lower()
        words = re.findall(r"\b\w+\b", response)
        word_count = len(words)

        wants_brief = any(cue in p_clean for cue in BREVITY_CUES)
        wants_detailed = any(cue in p_clean for cue in ELABORATION_CUES)

        if wants_brief:
            target = "CONCISE"
            if word_count <= 25:
                score = 1.00
            elif word_count <= 45:
                score = 0.75
            elif word_count <= 80:
                score = 0.40
            else:
                score = 0.20  # rambling after being asked for brevity
        elif wants_detailed:
            target = "ELABORATE"
            if word_count >= 60:
                score = 1.00
            elif word_count >= 35:
                score = 0.75
            else:
                score = 0.40  # too short for an architecture walkthrough
        else:
            target = "STANDARD"
            if 20 <= word_count <= 150:
                score = 0.85
            else:
                score = 0.70

        return {
            "length_target": target,
            "word_count": word_count,
            "compliance_score": round(score, 3),
            "wants_brevity": wants_brief,
            "wants_elaboration": wants_detailed,
            "is_calibrated": score >= 0.70
        }
