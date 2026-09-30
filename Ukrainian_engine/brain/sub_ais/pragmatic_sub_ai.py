"""
Ukrainian Pragmatic Sub-AI.
Evaluates communicative intent, register formality, and honorific deference deixis.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22) and Register Score (Offset 0x36 / Byte 54).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import EmailSubAINeural


@dataclass
class UkrainianPragmaticEvaluationResult:
    input_text: str
    formality_tier: str
    is_formal: bool
    politeness_score: float
    neural_politeness_index: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


UkrainianPragmaticEvaluation = UkrainianPragmaticEvaluationResult


class UkrainianPragmaticSubAI:
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

    def evaluate(self, text: str) -> UkrainianPragmaticEvaluationResult:
        # Heuristic register check
        is_formal = any(w in text.lower() for w in ["please", "sir", "dr", "doctor", "aap", "usted", "vous", "sie", "thầy", "ji", "గారు", "साहेब", "пан", "уважаемый", "tuan"])
        base_pol = 0.92 if is_formal else 0.72

        neural_pol = 0.85
        if self.is_neural_loaded:
            try:
                n_res = self.neural_model.analyze_text(text)
                neural_pol = float(n_res.get("politeness_index", 0.85))
                score = 0.75 * base_pol + 0.25 * neural_pol
            except Exception:
                score = base_pol
        else:
            score = base_pol

        score = round(min(1.0, max(0.0, score)), 4)
        synced = False
        if self.amsv is not None:
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return UkrainianPragmaticEvaluationResult(
            input_text=text,
            formality_tier="FORMAL" if is_formal else "STANDARD",
            is_formal=is_formal,
            politeness_score=score,
            neural_politeness_index=round(neural_pol, 4),
            amsv_synced=synced,
        )
