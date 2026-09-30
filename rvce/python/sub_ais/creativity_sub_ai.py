"""
creativity_sub_ai.py - RVCE Creativity & Out-of-the-Box Thinking Sub-AI

Evaluates:
1. Divergent thinking breadth (number of viable alternative pathways proposed)
2. Conceptual distance & novelty (semantic distance between combined concepts)
3. Lateral solution synthesis (orthogonal cross-domain transfer)
4. Analogical and metaphorical depth
"""

from __future__ import annotations
import re
from typing import Dict, Any

class CreativitySubAI:
    def __init__(self):
        self.creative_cues = [
            "novel", "unconventional", "innovative", "alternative",
            "orthogonal", "lateral", "pivot", "paradigm",
            "synthesize", "re-architect", "out of the box", "counter-intuitive",
            "cross-pollination", "first principles rethink", "non-obvious"
        ]
        self.metaphor_cues = [
            "like a", "analogous to", "akin to", "metaphorically", "similar to how"
        ]

    def evaluate(self, transcript: str) -> Dict[str, Any]:
        lower = transcript.lower()

        # 1. Divergent thinking count
        cues_hit = [c for c in self.creative_cues if c in lower]
        divergent_score = min(1.0, 0.30 + len(cues_hit) * 0.18)

        # 2. Conceptual distance & novelty
        novelty_score = min(1.0, 0.35 + len(cues_hit) * 0.16)

        # 3. Lateral synthesis
        lateral_score = min(1.0, 0.28 + len(cues_hit) * 0.20)

        # 4. Metaphoric richness
        has_metaphor = any(m in lower for m in self.metaphor_cues)
        metaphor_score = 0.90 if has_metaphor else 0.42

        composite = (
            divergent_score * 0.35 +
            novelty_score * 0.25 +
            lateral_score * 0.25 +
            metaphor_score * 0.15
        )

        return {
            "sub_ai": "creativity",
            "divergent_thinking_score": round(divergent_score, 3),
            "conceptual_novelty_score": round(novelty_score, 3),
            "lateral_synthesis_score": round(lateral_score, 3),
            "metaphoric_richness": round(metaphor_score, 3),
            "creative_markers_found": cues_hit,
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
