"""
French Syntax Sub-AI.
Evaluates Gallo-Romance non-pro-drop subject overtness, SVO canonical order,
bipartite negation (ne...pas), and subjunctive triggers.
Syncs strictly with AMSV Capability 1 (Offset 0x12 / Byte 18) and Structural Score (Offset 0x34 / Byte 52).
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import FrenchTokenizer
from ..skills.pos_tagging import FrenchPOSTagger
from ..skills.parsing import FrenchParser, FrenchSentenceStructure


@dataclass
class FrenchSyntaxEvaluationResult:
    input_text: str
    is_valid_sentence: bool
    syntactic_integrity_score: float
    has_overt_subject: bool
    is_expletive: bool
    has_bipartite_negation: bool
    has_subjunctive_trigger: bool
    clitic_count: int
    amsv_synced: bool

    @property
    def syntax_score(self) -> float:
        return self.syntactic_integrity_score


# Public alias
FrenchSyntaxEvaluation = FrenchSyntaxEvaluationResult


class FrenchSyntaxSubAI:
    """
    Dedicated AI Sub-Engine for French Syntactic Invariants and Agreement.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = FrenchTokenizer()
        self.tagger = FrenchPOSTagger()
        self.parser = FrenchParser()

    def evaluate(self, text: str) -> FrenchSyntaxEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed: FrenchSentenceStructure = self.parser.parse(tagged)

        has_verb = any(t[1] in {"VERB", "AUX"} for t in tagged)
        score = 0.65
        if has_verb:
            score += 0.20
        if parsed.has_overt_subject or parsed.is_imperative:
            score += 0.05
        if parsed.has_bipartite_negation:
            score += 0.05
        if parsed.has_subjunctive_trigger:
            score += 0.05

        score = min(1.0, score)
        is_valid = (parsed.has_overt_subject or parsed.is_imperative) and has_verb

        synced = False
        if self.amsv is not None:
            # Sync to Capability 1 (Byte 18 / 0x12) and Structural Score (Byte 52 / 0x34)
            self.amsv.set_cognitive_score(1, score)
            self.amsv.set_global_structural_score(score)
            synced = True

        return FrenchSyntaxEvaluationResult(
            input_text=text,
            is_valid_sentence=is_valid,
            syntactic_integrity_score=score,
            has_overt_subject=parsed.has_overt_subject,
            is_expletive=parsed.is_expletive_subject,
            has_bipartite_negation=parsed.has_bipartite_negation,
            has_subjunctive_trigger=parsed.has_subjunctive_trigger,
            clitic_count=len(parsed.clitics),
            amsv_synced=synced,
        )
