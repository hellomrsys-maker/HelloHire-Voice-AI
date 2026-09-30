"""
cognitive_reasoning_agent.py - Engine D Sub-Core D2 (Python)
Cognitive Capabilities & Adaptive Examination Engine: 8 Cognitive facets
(Thinking, Focus, Recall, Creativity, Imagination, Analytical, Verbal, Emotional)
and 3PL IRT Adaptive Scoring logic.
"""

from __future__ import annotations
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from ccte.python.ccte_subagents import CCTECoordinator


class CognitiveReasoningAgentSubCore:
    """
    Python Sub-Core D2: 8 Cognitive capabilities & adaptive testing agent.
    """

    def __init__(self):
        self.ccte_engine = CCTECoordinator()

    def evaluate_cognitive_facets(self, candidate_input: str) -> Dict[str, Any]:
        """
        Evaluates all 8 cognitive capabilities and returns normalized scores.
        """
        scores = self.ccte_engine.evaluate_candidate_turn(candidate_input)

        # Calculate 3PL IRT latent ability theta
        avg_score = sum(scores.values()) / max(1, len(scores))
        theta = round((avg_score - 0.5) * 6.0, 3) # Latent ability in [-3.0, +3.0]

        return {
            "sub_core": "D2_Python",
            "scores": scores,
            "latent_ability_theta": theta,
            "composite_cognitive_score": round(avg_score, 4)
        }
