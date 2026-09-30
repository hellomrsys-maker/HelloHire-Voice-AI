"""
register_shift_ai.py — Evaluates candidate register modulation (formal executive vs collaborative peer).
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

FORMAL_MARKERS = [
    "good morning", "good afternoon", "furthermore", "subsequently", "with respect to",
    "herein", "statutory", "fiduciary", "governance", "in accordance with"
]

CASUAL_MARKERS = [
    "hey", "cool", "hack", "pretty neat", "awesome", "messy", "super quick", "stuff"
]


class RegisterShiftAI:
    """
    Evaluates whether the candidate mirrors the interviewer's register appropriately
    (adapting to executive formality without sounding robotic, or technical peer banter without slang).
    """

    def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        p_clean = prompt.lower()
        r_clean = response.lower()

        p_formal = sum(1 for m in FORMAL_MARKERS if m in p_clean)
        p_casual = sum(1 for m in CASUAL_MARKERS if m in p_clean)

        r_formal = sum(1 for m in FORMAL_MARKERS if m in r_clean)
        r_casual = sum(1 for m in CASUAL_MARKERS if m in r_clean)

        if p_formal > p_casual:
            prompt_reg = "FORMAL"
            if r_formal > 0 and r_casual == 0:
                match_score = 0.95
            elif r_casual > 0:
                match_score = 0.40  # too casual for formal prompt
            else:
                match_score = 0.80
        elif p_casual > p_formal:
            prompt_reg = "CASUAL"
            if r_casual > 0:
                match_score = 0.90
            elif r_formal >= 2:
                match_score = 0.50  # overly stiff
            else:
                match_score = 0.80
        else:
            prompt_reg = "PROFESSIONAL_NEUTRAL"
            match_score = 0.85

        return {
            "prompt_register": prompt_reg,
            "match_score": round(match_score, 3),
            "response_formal_hits": r_formal,
            "response_casual_hits": r_casual,
            "is_matched": match_score >= 0.70
        }
