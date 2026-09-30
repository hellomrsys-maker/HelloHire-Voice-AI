"""
Spanish Syntax Sub-AI.
Evaluates pro-drop subject recovery, SVO canonical order, clitic chains, and subjunctive triggers.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import SpanishTokenizer
from ..skills.pos_tagging import SpanishPOSTagger
from ..skills.parsing import SpanishParser, SpanishSentenceStructure


@dataclass
class SpanishSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    is_pro_drop: bool
    has_overt_subject: bool
    has_subjunctive_trigger: bool
    has_clitic_chain: bool
    has_personal_a: bool
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
SpanishSyntaxEvaluation = SpanishSyntaxEvaluationResult


class SpanishSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for Spanish Syntactic Invariants and Agreement.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = SpanishTokenizer()
        self.tagger = SpanishPOSTagger()
        self.parser = SpanishParser()

    def evaluate(self, text: str) -> SpanishSyntaxEvaluationResult:
        tokens = self.tokenizer.segment(text)
        tagged = self.tagger.tag(tokens)
        parsed: SpanishSentenceStructure = self.parser.parse(tagged)

        has_verb = any(t[1] in {"VERB", "AUX"} for t in tagged)
        score = 0.65
        if has_verb:
            score += 0.20
        if parsed.has_overt_subject or parsed.is_pro_drop:
            score += 0.05
        if parsed.has_subjunctive_trigger:
            score += 0.05
        if parsed.has_personal_a:
            score += 0.05

        score = min(1.0, score)
        synced = False

        if self.amsv is not None:
            # Sync strictly to Capability 1 (0x12) and Structural Score (0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return SpanishSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=has_verb,
            syntactic_integrity_score=round(score, 4),
            is_pro_drop=parsed.is_pro_drop,
            has_overt_subject=parsed.has_overt_subject,
            has_subjunctive_trigger=parsed.has_subjunctive_trigger,
            has_clitic_chain=parsed.has_clitic_chain,
            has_personal_a=parsed.has_personal_a,
            amsv_synced=synced,
        )
