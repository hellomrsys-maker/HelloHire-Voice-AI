"""
Mandarin Syntax Sub-AI.
Evaluates topic-comment coherence, aspect completion, disposal (把), and passive (被) syntax.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import MandarinTokenizer
from ..skills.pos_tagging import MandarinPOSTagger
from ..skills.parsing import MandarinParser


@dataclass
class MandarinSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_topic_comment: bool
    is_ba_construction: bool
    is_bei_construction: bool
    aspect_markers: list
    amsv_synced: bool

    @property
    def has_ba_construction(self) -> bool:
        return self.is_ba_construction

    @property
    def has_bei_construction(self) -> bool:
        return self.is_bei_construction

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score

# Alias for consistent naming across engine interfaces
MandarinSyntaxEvaluation = MandarinSyntaxEvaluationResult


class MandarinSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for Mandarin Syntactic Structure and Grammar Invariants.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = MandarinTokenizer()
        self.tagger = MandarinPOSTagger()
        self.parser = MandarinParser()

    def evaluate(self, text: str) -> MandarinSyntaxEvaluationResult:
        tokens = self.tokenizer.segment(text)
        tagged = self.tagger.tag(tokens)
        parsed = self.parser.parse(tagged)

        # Evaluate syntactic integrity
        score = 0.60
        has_verb = any(t[1] in {"VV", "VC", "VE"} for t in tagged)
        if has_verb:
            score += 0.25
        if parsed.is_ba_construction and parsed.ba_disposed_object:
            score += 0.10
        if parsed.is_bei_construction:
            score += 0.05
        if parsed.is_topic_comment:
            score += 0.05

        score = min(1.0, score)
        synced = False

        # Zero-Bridge Sync strictly to Capability 1 (0x12) and Structural Score (0x34)
        if self.amsv is not None:
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return MandarinSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=has_verb,
            syntactic_integrity_score=round(score, 4),
            is_topic_comment=parsed.is_topic_comment,
            is_ba_construction=parsed.is_ba_construction,
            is_bei_construction=parsed.is_bei_construction,
            aspect_markers=parsed.aspect_markers,
            amsv_synced=synced,
        )
