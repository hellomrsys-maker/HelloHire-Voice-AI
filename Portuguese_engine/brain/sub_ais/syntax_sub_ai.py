"""
Portuguese Syntax Sub-AI.
Evaluates SVO constituent ordering, personal infinitive usage, clitic placement,
and subjunctive triggers.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import PortugueseTokenizer
from ..skills.parsing import PortugueseParser


@dataclass
class PortugueseSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_canonical_svo: bool
    has_verb: bool
    is_pro_drop: bool
    has_clitic: bool
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
PortugueseSyntaxEvaluation = PortugueseSyntaxEvaluationResult


class PortugueseSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for Portuguese Syntactic Invariants and Clausal Alignment.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = PortugueseTokenizer()
        self.parser = PortugueseParser()

    def evaluate(self, text: str) -> PortugueseSyntaxEvaluationResult:
        parsed = self.parser.parse_sentence(text)

        has_verb = parsed["verb"] is not None
        score = 0.65
        if has_verb:
            score += 0.15
        if parsed["is_svo"]:
            score += 0.10
        if parsed["subjunctive_trigger"] or parsed["has_clitic"]:
            score += 0.10

        score = min(1.0, score)
        is_valid = has_verb and parsed["is_svo"]

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return PortugueseSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=score,
            is_canonical_svo=parsed["is_svo"],
            has_verb=has_verb,
            is_pro_drop=parsed["is_pro_drop"],
            has_clitic=parsed["has_clitic"],
            amsv_synced=synced,
        )
