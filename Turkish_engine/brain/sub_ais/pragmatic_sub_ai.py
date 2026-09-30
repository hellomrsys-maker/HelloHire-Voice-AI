"""Turkish Pragmatic Sub-AI.

Evaluates address hierarchy ('sen' vs 'siz'), postpositive honorific titles,
politeness formulas, and communicative register.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22)
and Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import TurkishPragmaticsEngine
from ..skills.tokenization import TurkishTokenizer


@dataclass
class TurkishPragmaticEvaluationResult:
    input_text: str
    register: str
    is_formal: bool
    is_informal: bool
    has_honorific_title: bool
    politeness_score: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


# Public alias
TurkishPragmaticEvaluation = TurkishPragmaticEvaluationResult


class TurkishPragmaticSubAI:
    """Dedicated AI Sub-Engine for Turkish Pragmatics, Social Deixis, and Honorific Titles."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = TurkishTokenizer()
        self.engine = TurkishPragmaticsEngine()

    def evaluate(self, text: str) -> TurkishPragmaticEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        reg = self.engine.detect_register(text)

        has_honorific = any(
            TurkishTokenizer.turkish_lower(t) in self.engine.HONORIFIC_POSTPOSITIVES
            for t in tokens
        )

        score = 0.70
        if reg in ("formal_business", "academic"):
            score += 0.15
        elif reg == "informal":
            score += 0.05

        if has_honorific:
            score += 0.10

        score = min(1.0, score)

        synced = False
        if self.amsv is not None:
            # Sync to Capability 3 (Byte 22 / 0x16) and Register Score (Byte 54 / 0x36)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return TurkishPragmaticEvaluationResult(
            input_text=text,
            register=reg,
            is_formal=(reg in ("formal_business", "academic")),
            is_informal=(reg == "informal"),
            has_honorific_title=has_honorific,
            politeness_score=score,
            amsv_synced=synced
        )
