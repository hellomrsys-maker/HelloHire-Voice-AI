"""Russian Pragmatic Sub-AI.

Evaluates address hierarchy ('ты' vs 'Вы'), patronymic presence,
epistolary markers, and communicative register.
Syncs strictly with AMSV Capability 3 (Offset 0x16 / Byte 22)
and Register Score (Offset 0x36 / Byte 54).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.pragmatics_engine import RussianPragmaticsEngine
from ..skills.tokenization import RussianTokenizer


@dataclass
class RussianPragmaticEvaluationResult:
    input_text: str
    register: str
    is_formal: bool
    is_informal: bool
    has_patronymic: bool
    politeness_score: float
    amsv_synced: bool

    @property
    def pragmatic_score(self) -> float:
        return self.politeness_score


# Public alias
RussianPragmaticEvaluation = RussianPragmaticEvaluationResult


class RussianPragmaticSubAI:
    """Dedicated AI Sub-Engine for Russian Pragmatics, Register, and Social Deixis."""

    PATRONYMIC_ENDINGS = ("ович", "евич", "ич", "овна", "евна", "ична")

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.tokenizer = RussianTokenizer()
        self.engine = RussianPragmaticsEngine()

    def evaluate(self, text: str) -> RussianPragmaticEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        reg = self.engine.detect_register(text)

        has_patronymic = any(
            t.lower().endswith(self.PATRONYMIC_ENDINGS) and len(t) > 5
            for t in tokens
        )

        score = 0.70
        if reg == "formal_business":
            score += 0.15
        elif reg == "informal_friendly":
            score += 0.05

        if has_patronymic:
            score += 0.10

        score = min(1.0, score)

        synced = False
        if self.amsv is not None:
            # Sync to Capability 3 (Byte 22 / 0x16) and Register Score (Byte 54 / 0x36)
            self.amsv.set_cognitive_score(3, score)
            self.amsv.set_global_register_score(score)
            synced = True

        return RussianPragmaticEvaluationResult(
            input_text=text,
            register=reg,
            is_formal=(reg == "formal_business"),
            is_informal=(reg == "informal_friendly"),
            has_patronymic=has_patronymic,
            politeness_score=score,
            amsv_synced=synced
        )
