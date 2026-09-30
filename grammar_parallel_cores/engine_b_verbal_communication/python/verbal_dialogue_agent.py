"""
verbal_dialogue_agent.py - Engine B Sub-Core B2 (Python)
Spoken & Verbal Communication Engine: Neural interview dialogue agent,
register compliance, STAR methodology coherence, and confidence index.
"""

from __future__ import annotations
import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from rsse.python.verbal_sub_ai_neural import RecruitmentVerbalSubAINeural


class VerbalDialogueAgentSubCore:
    """
    Python Sub-Core B2: Neural recruitment dialogue and verbal communication evaluator.
    """

    def __init__(self):
        self.neural_model = RecruitmentVerbalSubAINeural(vocab_size=4096, d_model=128)
        self.neural_model.eval()

    def evaluate_verbal_turn(self, candidate_response: str, scenario_type: str = "technical") -> Dict[str, Any]:
        """
        Evaluates candidate speech transcript across STAR, register, and professional vocabulary.
        """
        import torch
        words = candidate_response.strip().split()
        word_count = len(words)

        # Neural evaluation via analyze_verbal_response
        res = self.neural_model.analyze_verbal_response(candidate_response)

        star_score = float(res.get("star_coherence", 0.75))
        reg_score = float(res.get("register_compliance", 0.80))
        vocab_density = float(res.get("jargon_density", 0.70))
        confidence = float(res.get("candidate_confidence", 0.85))

        composite = round(
            0.30 * star_score + 0.30 * reg_score + 0.20 * vocab_density + 0.20 * confidence,
            4
        )

        return {
            "sub_core": "B2_Python",
            "scenario_type": scenario_type,
            "word_count": word_count,
            "star_score": round(star_score, 4),
            "register_compliance": round(reg_score, 4),
            "vocabulary_density": round(vocab_density, 4),
            "confidence_index": round(confidence, 4),
            "verbal_neural_composite": composite
        }
