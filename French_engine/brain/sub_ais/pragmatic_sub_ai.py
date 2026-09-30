"""
French Pragmatic Sub-AI.
Evaluates sociolinguistic register, T-V distinction (tutoiement vs. vouvoiement),
and epistolary courtesy markers.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22) and Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import FrenchPragmaticsEngine


@dataclass
class FrenchPragmaticEvaluationResult:
    input_text: str
    assigned_register: str
    is_formal: bool
    is_informal: bool
    has_register_clash: bool
    has_courtesy_formula: bool
    politeness_score: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


# Public alias
FrenchPragmaticEvaluation = FrenchPragmaticEvaluationResult


class FrenchPragmaticSubAI:
    """
    Dedicated AI Sub-Engine for French Pragmatic Politeness and Register Alignment.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.engine = FrenchPragmaticsEngine()

    def evaluate(self, text: str) -> FrenchPragmaticEvaluationResult:
        res = self.engine.evaluate_register(text)
        score = res["politeness_score"]

        synced = False
        if self.amsv is not None:
            # Sync strictly to Capability 3 (Byte 22 / 0x16) and Register Score (Byte 54 / 0x36)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return FrenchPragmaticEvaluationResult(
            input_text=text,
            assigned_register=res["assigned_register"],
            is_formal=res["is_formal"],
            is_informal=res["is_informal"],
            has_register_clash=res["has_register_clash"],
            has_courtesy_formula=res["has_courtesy_formula"],
            politeness_score=score,
            amsv_synced=synced,
        )
