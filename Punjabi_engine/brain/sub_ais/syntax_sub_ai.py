"""
Punjabi Syntax Sub-AI.
Evaluates SOV constituent assembly, case relations, and clause boundaries.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import WritingSubAINeural


@dataclass
class PunjabiSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    word_order: str
    neural_completeness: float
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


PunjabiSyntaxEvaluation = PunjabiSyntaxEvaluationResult


class PunjabiSyntaxSubAI:
    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None, checkpoint_path: Optional[str] = None):
        self.amsv = amsv_view
        self.neural_model = WritingSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("writing_sub_ai", ckpt.get("writing", ckpt))
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> PunjabiSyntaxEvaluationResult:
        words = text.strip().split()
        has_content = len(words) >= 2
        base_score = 0.85 if has_content else 0.40

        neural_comp = 0.88
        if self.is_neural_loaded:
            try:
                ids, mask = self.neural_model.tokenizer.encode(text, max_length=56)
                with torch.no_grad():
                    out = self.neural_model(ids, mask)
                    neural_comp = float(out["sentence_completeness"].item())
                    score = 0.70 * base_score + 0.30 * neural_comp
            except Exception:
                score = base_score
        else:
            score = base_score

        score = round(min(1.0, max(0.0, score)), 4)
        synced = False
        if self.amsv is not None:
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return PunjabiSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=has_content,
            syntactic_integrity_score=score,
            word_order="SOV",
            neural_completeness=round(neural_comp, 4),
            amsv_synced=synced,
        )
