"""
Portuguese Pragmatic Sub-AI.
Evaluates address hierarchy (você vs tu vs o senhor), courtesy formulas,
and politeness stratification.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22) and Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import PortuguesePragmaticsEngine
from ..skills.tokenization import PortugueseTokenizer


@dataclass
class PortuguesePragmaticEvaluationResult:
    input_text: str
    address_tier: str
    is_formal: bool
    is_familiar: bool
    is_intimate: bool
    politeness_score: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


# Public alias
PortuguesePragmaticEvaluation = PortuguesePragmaticEvaluationResult


class PortuguesePragmaticSubAI:
    """
    Dedicated AI Sub-Engine for Portuguese Pragmatics and Social Deixis.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = PortugueseTokenizer()
        self.engine = PortuguesePragmaticsEngine()

    def evaluate(self, text: str) -> PortuguesePragmaticEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        res = self.engine.evaluate_pragmatics(tokens)
        score = res["politeness_score"]
        tier = res["tier"]

        synced = False
        if self.amsv is not None:
            # Sync strictly to Capability 3 (Byte 22 / 0x16) and Register Score (Byte 54 / 0x36)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return PortuguesePragmaticEvaluationResult(
            input_text=text,
            address_tier=tier,
            is_formal=tier == "formal",
            is_familiar=tier == "familiar",
            is_intimate=tier == "intimate",
            politeness_score=score,
            amsv_synced=synced,
        )
