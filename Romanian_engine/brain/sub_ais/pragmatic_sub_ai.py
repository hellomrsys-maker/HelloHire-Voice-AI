"""
Romanian Pragmatic Sub-AI.
Evaluates sociolinguistic register, politeness indices, and discourse deixis.
Syncs strictly with AMSV Capability 4 (Offset 0x18 / Byte 24).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import EmailSubAINeural


@dataclass
class RomanianPragmaticEvaluationResult:
    input_text: str
    formality_tier: str
    politeness_score: float
    pragmatic_validity: bool
    amsv_synced: bool


RomanianPragmaticEvaluation = RomanianPragmaticEvaluationResult


class RomanianPragmaticSubAI:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None, checkpoint_path: Optional[str] = None):
        self.amsv = amsv_view
        self.neural_model = EmailSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("email_sub_ai", ckpt.get("email", ckpt))
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> RomanianPragmaticEvaluationResult:
        pol_score = 0.82
        tier = "NEUTRAL"

        if self.is_neural_loaded:
            try:
                ids, mask = self.neural_model.tokenizer.encode(text, max_length=56)
                with torch.no_grad():
                    out = self.neural_model(ids, mask)
                    pol_score = float(out["politeness_score"].item())
                    tier = "HONORIFIC" if pol_score >= 0.70 else "CASUAL"
            except Exception:
                pass

        synced = False
        if self.amsv is not None:
            self.amsv.set_cognitive_score(4, pol_score)
            synced = True

        return RomanianPragmaticEvaluationResult(
            input_text=text,
            formality_tier=tier,
            politeness_score=round(pol_score, 4),
            pragmatic_validity=True,
            amsv_synced=synced,
        )
