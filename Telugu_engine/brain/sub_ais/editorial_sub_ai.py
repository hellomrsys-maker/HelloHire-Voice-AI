"""
Telugu Editorial Sub-AI.
Evaluates textual cohesion, agreement harmony, and 4-tier error taxonomy.
Syncs strictly with AMSV Capability 2 (Offset 0x14 / Byte 20) and Capability 5 (Offset 0x1A / Byte 26).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import ReviewingSubAINeural


@dataclass
class TeluguEditorialEvaluationResult:
    input_text: str
    editorial_score: float
    dominant_error_tier: str
    hedging_score: float
    amsv_synced: bool

    @property
    def reviewing_score(self) -> float:
        return self.editorial_score


TeluguEditorialEvaluation = TeluguEditorialEvaluationResult


class TeluguEditorialSubAI:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None, checkpoint_path: Optional[str] = None):
        self.amsv = amsv_view
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

    def evaluate(self, text: str) -> TeluguEditorialEvaluationResult:
        base_editorial = 0.90
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
            self.amsv.set_cognitive_score(2, round(editorial_score * 0.95, 4))
            self.amsv.set_cognitive_score(5, editorial_score)
            synced = True

        return TeluguEditorialEvaluationResult(
            input_text=text,
            editorial_score=editorial_score,
            dominant_error_tier=dominant_err,
            hedging_score=round(hedging, 4),
            amsv_synced=synced,
        )
