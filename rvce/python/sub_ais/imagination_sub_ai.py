"""
imagination_sub_ai.py - RVCE Imagination & Future Forecasting Sub-AI

Evaluates:
1. Counterfactual simulation ("what-if" exploration, retrospective branch analysis)
2. Prospective forecasting (forward trajectory projection, future-proofing)
3. Theory of Mind & empathy modeling (understanding diverse stakeholder perspectives)
4. Strategic future-state vision articulation
"""

from __future__ import annotations
import re
from typing import Dict, Any

class ImaginationSubAI:
    def __init__(self):
        self.counterfactual_cues = [
            "what if", "suppose", "in a scenario where", "had we chosen",
            "alternatively", "counterfactual", "in hindsight", "if we assumed"
        ]
        self.prospective_cues = [
            "projecting forward", "in the next five years", "scale to",
            "future-proofing", "long-term horizon", "anticipating that", "vision"
        ]
        self.theory_of_mind_cues = [
            "from the customer's perspective", "user experience", "stakeholder alignment",
            "team's point of view", "empathy", "interviewer's concern", "from their standpoint"
        ]

    def evaluate(self, transcript: str) -> Dict[str, Any]:
        lower = transcript.lower()

        # 1. Counterfactual simulation
        cf_hits = [c for c in self.counterfactual_cues if c in lower]
        counterfactual_score = 0.92 if cf_hits else 0.40

        # 2. Prospective forecasting
        pf_hits = [c for c in self.prospective_cues if c in lower]
        prospective_score = 0.94 if pf_hits else 0.42

        # 3. Theory of Mind
        tom_hits = [c for c in self.theory_of_mind_cues if c in lower]
        theory_of_mind_score = 0.90 if tom_hits else 0.38

        # 4. Vision articulation clarity
        vision_clarity = min(1.0, max(0.2, (counterfactual_score + prospective_score + theory_of_mind_score) / 3.0))

        composite = (
            counterfactual_score * 0.30 +
            prospective_score * 0.30 +
            theory_of_mind_score * 0.25 +
            vision_clarity * 0.15
        )

        return {
            "sub_ai": "imagination",
            "counterfactual_score": round(counterfactual_score, 3),
            "prospective_forecasting_score": round(prospective_score, 3),
            "theory_of_mind_score": round(theory_of_mind_score, 3),
            "vision_clarity": round(vision_clarity, 3),
            "composite_score": round(min(1.0, max(0.0, composite)), 3)
        }
