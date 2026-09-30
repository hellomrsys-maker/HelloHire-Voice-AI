"""
Bengali Syntax Sub-AI.
Evaluates SOV canonical constituent order, non-ergative nominative agreement,
and clausal integrity.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import BengaliTokenizer
from ..skills.pos_tagging import BengaliPOSTagger
from ..skills.parsing import BengaliParser


@dataclass
class BengaliSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_canonical_sov: bool
    has_verb: bool
    is_pro_drop: bool
    agreement_valid: bool
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
BengaliSyntaxEvaluation = BengaliSyntaxEvaluationResult


class BengaliSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for Bengali Syntactic Invariants and SOV Grammar.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = BengaliTokenizer()
        self.tagger = BengaliPOSTagger()
        self.parser = BengaliParser()

    def evaluate(self, text: str) -> BengaliSyntaxEvaluationResult:
        parsed = self.parser.parse_sentence(text)

        has_verb = parsed["verb"] is not None
        score = 0.65
        if has_verb:
            score += 0.15
        if parsed["is_sov"]:
            score += 0.10
        if parsed["agreement_valid"]:
            score += 0.10

        score = min(1.0, score)
        is_valid = has_verb and parsed["is_sov"] and parsed["agreement_valid"]

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return BengaliSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=score,
            is_canonical_sov=parsed["is_sov"],
            has_verb=has_verb,
            is_pro_drop=parsed["is_pro_drop"],
            agreement_valid=parsed["agreement_valid"],
            amsv_synced=synced,
        )
