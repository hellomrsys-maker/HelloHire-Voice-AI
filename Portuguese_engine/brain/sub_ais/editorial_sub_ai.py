"""
Portuguese Editorial Sub-AI.
Evaluates textual cohesion, clitic placement, crase accentuation, and prepositional contractions.
Syncs strictly with AMSV Capability 2 (Offset 0x14 / Byte 20) and Capability 5 (Offset 0x1A / Byte 26).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..task.grammar_check import PortugueseGrammarCheckTask


@dataclass
class PortugueseEditorialEvaluationResult:
    input_text: str
    grammar_score: float
    is_clean: bool
    issues_detected: int
    editorial_score: float
    amsv_synced: bool


# Public alias
PortugueseEditorialEvaluation = PortugueseEditorialEvaluationResult


class PortugueseEditorialSubAI:
    """
    Dedicated AI Sub-Engine for Portuguese Editorial Quality and Orthographic Review.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.checker = PortugueseGrammarCheckTask()

    def evaluate(self, text: str) -> PortugueseEditorialEvaluationResult:
        check_res = self.checker.run(text)
        grammar_score = check_res["overall_score"]
        issues_count = check_res["diagnostics_count"]

        editorial_score = max(0.0, min(1.0, grammar_score))

        synced = False
        if self.amsv is not None:
            # Sync to Capability 2 (Byte 20 / 0x14) and Capability 5 (Byte 26 / 0x1A)
            self.amsv.set_cognitive_score(2, editorial_score * 0.95)
            self.amsv.set_cognitive_score(5, editorial_score)
            synced = True

        return PortugueseEditorialEvaluationResult(
            input_text=text,
            grammar_score=grammar_score,
            is_clean=issues_count == 0,
            issues_detected=issues_count,
            editorial_score=editorial_score,
            amsv_synced=synced,
        )
