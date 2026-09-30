"""
Mandarin Pragmatic Sub-AI.
Evaluates Mianzi (面子) politeness, indirectness, and communicative social registers.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22) and Global Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.sentiment_mianzi import MianziPragmaticSkill


@dataclass
class MandarinPragmaticEvaluationResult:
    input_text: str
    mianzi_score: float
    register_tier: str
    has_honorific: bool
    has_indirect_refusal: bool
    face_preservation: str
    amsv_synced: bool

    @property
    def is_formal(self) -> bool:
        return self.mianzi_score >= 0.70 or "Formal" in self.register_tier or self.has_honorific

MandarinPragmaticEvaluation = MandarinPragmaticEvaluationResult


class MandarinPragmaticSubAI:
    """
    Dedicated AI Sub-Engine for Mandarin Pragmatic Register and Mianzi Politeness.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.skill = MianziPragmaticSkill()

    def evaluate(self, text: str) -> MandarinPragmaticEvaluationResult:
        metrics = self.skill.evaluate_pragmatics(text)
        score = metrics["mianzi_score"]

        synced = False
        if self.amsv is not None:
            # Sync strictly to Capability 3 (0x16 / Byte 22) and Register Score (0x36 / Byte 54)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return MandarinPragmaticEvaluationResult(
            input_text=text,
            mianzi_score=score,
            register_tier=metrics["register_tier"],
            has_honorific=metrics["has_honorific"],
            has_indirect_refusal=metrics["has_indirect_refusal"],
            face_preservation=metrics["face_preservation"],
            amsv_synced=synced,
        )
