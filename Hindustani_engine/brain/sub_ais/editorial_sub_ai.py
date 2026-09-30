"""
Hindustani Editorial Sub-AI.
Evaluates textual cohesion, oblique case consistency, and syntactic polish
combined with neural review and error taxonomy analysis.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView:
- Capability 2 (Discourse / Cohesion Q16): Offset 0x14 (Byte 20)
- Capability 5 (Critical Review / Error Analysis Q16): Offset 0x1A (Byte 26)
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..task.grammar_check import HindustaniGrammarChecker
from gra_voi.bandhu.sub_ai_neural import ReviewingSubAINeural


@dataclass
class HindustaniEditorialEvaluationResult:
    input_text: str
    grammar_score: float
    is_clean: bool
    issues_detected: int
    editorial_score: float
    dominant_error_tier: str
    hedging_score: float
    amsv_synced: bool

    @property
    def reviewing_score(self) -> float:
        return self.editorial_score


# Public alias
HindustaniEditorialEvaluation = HindustaniEditorialEvaluationResult


class HindustaniEditorialSubAI:
    """
    Dedicated AI Sub-Engine for Hindustani Editorial Quality, Critical Review,
    and Error Taxonomy Analysis.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None
    ):
        self.amsv = amsv_view
        self.checker = HindustaniGrammarChecker()

        # Neural backbone
        self.neural_model = ReviewingSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("reviewing_sub_ai", ckpt.get("reviewing", ckpt))
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> HindustaniEditorialEvaluationResult:
        check_res = self.checker.check(text)
        grammar_score = float(check_res["score"])
        issues_count = int(check_res["issues_count"])

        base_editorial = max(0.0, min(1.0, grammar_score))

        dominant_err = "None"
        hedging = 0.50
        if self.is_neural_loaded:
            try:
                n_res = self.neural_model.analyze_text(text)
                dominant_err = str(n_res.get("dominant_error_tier", "None"))
                hedging = float(n_res.get("hedging_score", 0.50))
                editorial_score = 0.70 * base_editorial + 0.30 * (1.0 - (0.15 if dominant_err == "Fatal" else 0.05))
            except Exception:
                editorial_score = base_editorial
        else:
            editorial_score = base_editorial

        editorial_score = round(max(0.0, min(1.0, editorial_score)), 4)

        synced = False
        if self.amsv is not None:
            # Sync to Capability 2 (Byte 20 / 0x14) and Capability 5 (Byte 26 / 0x1A)
            self.amsv.set_cognitive_score(2, round(editorial_score * 0.95, 4))
            self.amsv.set_cognitive_score(5, editorial_score)
            synced = True

        return HindustaniEditorialEvaluationResult(
            input_text=text,
            grammar_score=grammar_score,
            is_clean=issues_count == 0,
            issues_detected=issues_count,
            editorial_score=editorial_score,
            dominant_error_tier=dominant_err,
            hedging_score=round(hedging, 4),
            amsv_synced=synced,
        )
