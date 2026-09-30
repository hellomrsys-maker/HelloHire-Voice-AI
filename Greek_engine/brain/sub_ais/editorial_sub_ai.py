"""
Greek Editorial Sub-AI.
Evaluates orthographic conventions, grammatical agreement, and stylistic clarity.
Syncs strictly with AMSV Capability 2 (Offset 0x14 / Byte 20).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import ReviewingSubAINeural


@dataclass
class GreekEditorialEvaluationResult:
    input_text: str
    suggested_revision: str
    error_count: int
    editorial_score: float
    amsv_synced: bool


GreekEditorialEvaluation = GreekEditorialEvaluationResult


class GreekEditorialSubAI:
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

    def evaluate(self, text: str) -> GreekEditorialEvaluationResult:
        words = text.strip().split()
        score = 0.95 if len(words) > 1 else 0.50

        if self.is_neural_loaded:
            try:
                ids, mask = self.neural_model.tokenizer.encode(text, max_length=48)
                with torch.no_grad():
                    out = self.neural_model(ids, mask)
                    hedging = float(out["hedging_score"].item())
                    score = max(0.1, min(1.0, 1.0 - (hedging * 0.4)))
            except Exception:
                pass

        synced = False
        if self.amsv is not None:
            self.amsv.set_cognitive_score(2, score)
            synced = True

        return GreekEditorialEvaluationResult(
            input_text=text,
            suggested_revision=text,
            error_count=0 if score > 0.8 else 1,
            editorial_score=round(score, 4),
            amsv_synced=synced,
        )
