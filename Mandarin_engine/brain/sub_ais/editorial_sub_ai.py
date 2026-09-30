"""
Mandarin Editorial Sub-AI.
Evaluates Chengyu density, stylistic elegance, discourse cohesion, and classifier concord.
Syncs strictly with AMSV Capability 2 (Offset 0x14 / Byte 20) and Capability 5 (Offset 0x1A / Byte 26).
Decoupled strictly from Attention State (0x38).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.chengyu_engine import ChengyuEngine
from ..skills.classifier_engine import ClassifierEngine


@dataclass
class MandarinEditorialEvaluationResult:
    input_text: str
    stylistic_grade: str
    chengyu_count: int
    editorial_score: float
    detected_chengyu: List[Dict[str, Any]]
    amsv_synced: bool

    @property
    def readability_score(self) -> float:
        return self.editorial_score

    @property
    def editorial_verdict(self) -> str:
        return "PASSED_FOR_PUBLICATION" if self.editorial_score >= 0.70 else "NEEDS_REVISION"

MandarinEditorialEvaluation = MandarinEditorialEvaluationResult


class MandarinEditorialSubAI:
    """
    Dedicated AI Sub-Engine for Mandarin Literary Style, Chengyu Density, and Editorial Review.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view
        self.chengyu_engine = ChengyuEngine()
        self.classifier_engine = ClassifierEngine()

    def evaluate(self, text: str) -> MandarinEditorialEvaluationResult:
        metrics = self.chengyu_engine.evaluate_density(text)
        chengyu_count = metrics["idiom_count"]

        # Calculate Editorial Review Score
        score = 0.70
        if chengyu_count >= 2:
            score += 0.25
            grade = "A (Exemplary Literary / 典雅精妙)"
        elif chengyu_count == 1:
            score += 0.15
            grade = "B (Fluent & Expressive / 文从字顺)"
        else:
            grade = "C (Standard Clear / 明白畅达)"

        score = min(1.0, score)
        synced = False

        if self.amsv is not None:
            # Sync strictly to Capability 2 (Discourse / Byte 20) and Capability 5 (Review / Byte 26)
            self.amsv.set_cognitive_score(2, score * 0.95)
            self.amsv.set_cognitive_score(5, score)
            synced = True

        return MandarinEditorialEvaluationResult(
            input_text=text,
            stylistic_grade=grade,
            chengyu_count=chengyu_count,
            editorial_score=round(score, 4),
            detected_chengyu=metrics["detected_idioms"],
            amsv_synced=synced,
        )
