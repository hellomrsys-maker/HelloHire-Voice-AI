"""
Spanish Pragmatic Sub-AI.
Evaluates address hierarchy (tuteo, voseo, ustedeo), courtesy markers, and socio-pragmatic distance.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22) and Global Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import SpanishPragmaticsEngine


@dataclass
class SpanishPragmaticEvaluationResult:
    input_text: str
    address_tier: str
    is_formal: bool
    politeness_score: float
    detected_courtesy_markers: List[str]
    has_pragmatic_mitigation: bool
    amsv_synced: bool


# Public alias
SpanishPragmaticEvaluation = SpanishPragmaticEvaluationResult


class SpanishPragmaticSubAI:
    """
    Dedicated AI Sub-Engine for Spanish Pragmatics, Deference, and Register Modulation.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.engine = SpanishPragmaticsEngine()

    def evaluate(self, text: str) -> SpanishPragmaticEvaluationResult:
        res = self.engine.evaluate_pragmatics(text)
        score = res["politeness_score"]

        synced = False
        if self.amsv is not None:
            # Sync strictly to Capability 3 (0x16 / Byte 22) and Register Score (0x36 / Byte 54)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return SpanishPragmaticEvaluationResult(
            input_text=text,
            address_tier=res["address_tier"],
            is_formal=res["is_formal"],
            politeness_score=score,
            detected_courtesy_markers=res["detected_courtesy_markers"],
            has_pragmatic_mitigation=res["has_pragmatic_mitigation"],
            amsv_synced=synced,
        )
