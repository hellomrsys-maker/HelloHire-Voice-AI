"""
interruption_recovery_ai.py — Evaluates candidate composure and graceful redirection when interrupted.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

REDIRECTION_CUES = [
    "hold on", "stop there", "let me interrupt", "let's pivot",
    "actually, before that", "forget that, tell me about", "wait a second"
]

GRACEFUL_ACKNOWLEDGEMENTS = [
    "certainly", "absolutely", "fair point", "sure", "happy to pivot",
    "to address that directly", "good question", "let's focus on that"
]

DEFENSIVE_MARKERS = [
    "as i was saying", "if you let me finish", "you didn't let me", "like i told you"
]


class InterruptionRecoveryAI:
    """
    Evaluates whether the candidate remains composed, non-defensive, and agile
    when the interviewer interrupts or redirects the conversation.
    """

    def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        p_clean = prompt.lower()
        r_clean = response.lower()

        was_interrupted = any(cue in p_clean for cue in REDIRECTION_CUES)

        if not was_interrupted:
            return {
                "was_interrupted": False,
                "composure_score": 0.85,
                "graceful_acknowledgement": False,
                "is_defensive": False
            }

        has_grace = any(ack in r_clean for ack in GRACEFUL_ACKNOWLEDGEMENTS)
        is_defensive = any(def_m in r_clean for def_m in DEFENSIVE_MARKERS)

        if is_defensive:
            composure = 0.25
        elif has_grace:
            composure = 0.95
        else:
            composure = 0.75

        return {
            "was_interrupted": True,
            "composure_score": round(composure, 3),
            "graceful_acknowledgement": has_grace,
            "is_defensive": is_defensive,
            "is_composed": composure >= 0.70
        }
