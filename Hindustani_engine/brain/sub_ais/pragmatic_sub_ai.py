"""
Hindustani Pragmatic Sub-AI.
Evaluates 3-tier social deixis (aap vs. tum vs. tu), honorific particle ji, and polite correspondence markers
combined with neural politeness modeling.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView:
- Capability 3 (Pragmatics / Register Q16): Offset 0x16 (Byte 22)
- Global Register Score (Q16): Offset 0x36 (Byte 54)
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import HindustaniPragmaticsEngine
from gra_voi.bandhu.sub_ai_neural import EmailSubAINeural


@dataclass
class HindustaniPragmaticEvaluationResult:
    input_text: str
    address_tier: str
    is_formal: bool
    is_familiar: bool
    is_intimate: bool
    has_honorific_particle_ji: bool
    politeness_score: float
    neural_politeness_index: float
    pragmatic_transfer_risk: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


# Public alias
HindustaniPragmaticEvaluation = HindustaniPragmaticEvaluationResult


class HindustaniPragmaticSubAI:
    """
    Dedicated AI Sub-Engine for Hindustani Pragmatics, Honorific Hierarchy,
    and Neural Register / Politeness Alignment.
    """

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None
    ):
        self.amsv = amsv_view
        self.engine = HindustaniPragmaticsEngine()

        # Neural backbone
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

    def evaluate(self, text: str) -> HindustaniPragmaticEvaluationResult:
        res = self.engine.evaluate_pragmatics(text)
        base_score = float(res["politeness_score"])

        neural_politeness = 0.85
        transfer_risk = 0.10
        if self.is_neural_loaded:
            try:
                n_res = self.neural_model.analyze_text(text)
                neural_politeness = float(n_res.get("politeness_index", 0.85))
                transfer_risk = float(n_res.get("pragmatic_transfer_risk", 0.10))
                composite_score = 0.75 * base_score + 0.25 * neural_politeness
            except Exception:
                composite_score = base_score
        else:
            composite_score = base_score

        composite_score = round(min(1.0, max(0.0, composite_score)), 4)

        synced = False
        if self.amsv is not None:
            # Sync strictly to Capability 3 (Byte 22 / 0x16) and Register Score (Byte 54 / 0x36)
            self.amsv.set_cognitive_score(3, composite_score)
            self.amsv.set_global_register_score(composite_score)
            synced = True

        return HindustaniPragmaticEvaluationResult(
            input_text=text,
            address_tier=res["address_tier"],
            is_formal=res["is_formal"],
            is_familiar=res["is_familiar"],
            is_intimate=res["is_intimate"],
            has_honorific_particle_ji=res["has_honorific_particle_ji"],
            politeness_score=composite_score,
            neural_politeness_index=round(neural_politeness, 4),
            pragmatic_transfer_risk=round(transfer_risk, 4),
            amsv_synced=synced,
        )
