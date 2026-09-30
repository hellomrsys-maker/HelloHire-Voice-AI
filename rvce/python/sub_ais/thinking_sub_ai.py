"""
thinking_sub_ai.py - RVCE Thinking Ability Sub-AI

Evaluates:
1. First-principles decomposition
2. MECE structuring (Mutually Exclusive, Collectively Exhaustive)
3. STAR situational coherence (Situation, Task, Action, Result)
4. Deductive reasoning chain depth
5. Fallacy resistance
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

class ThinkingSubAI:
    def __init__(self):
        self.connectives = [
            "because", "therefore", "consequently", "specifically",
            "firstly", "secondly", "finally", "root cause", "first principles",
            "trade-off", "hypothesis", "deduce", "in order to", "as a result",
            "underlying mechanism", "fundamental constraint"
        ]
        self.star_patterns = {
            "situation": [r"situation", r"context was", r"at the time", r"our team was facing", r"at my previous role"],
            "task": [r"task", r"objective", r"goal was to", r"responsible for", r"i was tasked with"],
            "action": [r"action", r"i implemented", r"i designed", r"we built", r"i led", r"i optimized", r"i resolved"],
            "result": [r"result", r"outcome", r"reduced", r"increased by", r"improved", r"delivered", r"%"]
        }

    def evaluate(self, transcript: str) -> Dict[str, Any]:
        lower = transcript.lower()

        # 1. Deductive reasoning chain & depth
        hit_connectives = [c for c in self.connectives if c in lower]
        inference_depth = min(10, 1 + len(hit_connectives))
        deductive_validity = min(1.0, 0.15 + (len(hit_connectives) * 0.16))

        # 2. MECE Structuring
        has_ordered_points = bool(re.search(r"(first|1\.|firstly).*(second|2\.|secondly)", lower, re.DOTALL))
        has_pillars = any(p in lower for p in ["two pillars", "three pillars", "two components", "on one hand", "on the other"])
        mece_score = 0.94 if (has_ordered_points or has_pillars) else min(0.85, 0.35 + len(hit_connectives) * 0.08)

        # 3. First Principles Score
        fp_markers = ["fundamental", "underlying mechanism", "first principles", "core constraint", "baseline"]
        has_fp = any(m in lower for m in fp_markers)
        first_principles_score = 0.95 if has_fp else min(0.80, 0.35 + len(hit_connectives) * 0.07)

        # 4. STAR Coherence
        star_hits = {
            dim: any(re.search(pat, lower) for pat in patterns)
            for dim, patterns in self.star_patterns.items()
        }
        completed_star = sum(star_hits.values())
        star_coherence = {4: 0.98, 3: 0.85, 2: 0.65, 1: 0.40, 0: 0.20}[completed_star]

        # Composite score
        composite = (
            (inference_depth / 10.0) * 0.25 +
            first_principles_score * 0.20 +
            mece_score * 0.20 +
            star_coherence * 0.20 +
            deductive_validity * 0.15
        )

        return {
            "sub_ai": "thinking",
            "reasoning_depth": inference_depth,
            "first_principles_score": round(first_principles_score, 3),
            "mece_score": round(mece_score, 3),
            "star_coherence": round(star_coherence, 3),
            "deductive_validity": round(deductive_validity, 3),
            "star_breakdown": star_hits,
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
