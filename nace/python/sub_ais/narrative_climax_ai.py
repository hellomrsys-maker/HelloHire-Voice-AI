"""
narrative_climax_ai.py — Detects signature stories, STAR method structure, and turnaround climaxes.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

SITUATION_MARKERS = [
    "we were facing", "the problem was", "the system crashed", "outage occurred",
    "legacy codebase", "technical debt", "initial situation", "at that time"
]

TASK_MARKERS = [
    "my role was", "my task was", "i was responsible for", "i needed to",
    "our goal was", "the mandate was", "we set out to"
]

ACTION_MARKERS = [
    "i implemented", "i designed", "i led the refactoring", "we built",
    "we replaced", "we migrated", "i rewrote", "i instrumented", "we introduced"
]

RESULT_MARKERS = [
    "as a result", "ultimately", "this reduced", "saving", "improved by",
    "we achieved", "successfully delivered", "revenue increased", "zero downtime"
]


class NarrativeClimaxAI:
    """
    Evaluates whether the candidate presents structured narrative climaxes (STAR format)
    with a clear conflict, decisive action, and quantifiable outcome.
    """

    def evaluate(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()

        sit_hits = [m for m in SITUATION_MARKERS if m in cleaned]
        task_hits = [m for m in TASK_MARKERS if m in cleaned]
        action_hits = [m for m in ACTION_MARKERS if m in cleaned]
        res_hits = [m for m in RESULT_MARKERS if m in cleaned]

        stages_found = {
            "situation": len(sit_hits) > 0,
            "task": len(task_hits) > 0,
            "action": len(action_hits) > 0,
            "result": len(res_hits) > 0
        }

        stage_count = sum(1 for v in stages_found.values() if v)
        star_complete = (stage_count >= 3)

        # Quantifiable outcome check
        has_quantifier = bool(re.search(r"\b\d+(?:\.\d+)?(?:%|ms|k|m|gb|req/s|rps)?\b", cleaned))

        base_score = stage_count * 0.22
        if has_quantifier and stages_found["result"]:
            base_score += 0.12

        climax_score = min(1.0, max(0.0, base_score))

        return {
            "climax_score": round(climax_score, 3),
            "stages_found": stages_found,
            "stage_count": stage_count,
            "has_star_structure": star_complete,
            "has_quantifiable_outcome": has_quantifier and stages_found["result"]
        }
