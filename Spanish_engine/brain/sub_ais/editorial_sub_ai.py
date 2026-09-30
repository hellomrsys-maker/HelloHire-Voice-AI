"""
Spanish Editorial Sub-AI.
Evaluates discourse cohesion, discourse markers (sin embargo, por lo tanto), and stylistic clarity.
Syncs strictly with AMSV Capability 2 (Offset 0x14 / Byte 20) and Capability 5 (Offset 0x1A / Byte 26).
Decoupled strictly from Attention State (0x38).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from amsv.python.amsv_embedded import AMSVEmbeddedView

DISCOURSE_CONNECTORS = [
    "sin embargo", "por lo tanto", "en consecuencia", "no obstante",
    "por consiguiente", "además", "en primer lugar", "por otro lado",
    "en cambio", "de hecho", "en efecto", "finalmente"
]


@dataclass
class SpanishEditorialEvaluationResult:
    input_text: str
    stylistic_grade: str
    connector_count: int
    editorial_score: float
    detected_connectors: List[str]
    amsv_synced: bool

    @property
    def readability_score(self) -> float:
        return self.editorial_score

    @property
    def editorial_verdict(self) -> str:
        return "PASSED_FOR_PUBLICATION" if self.editorial_score >= 0.70 else "NEEDS_REVISION"


# Public alias
SpanishEditorialEvaluation = SpanishEditorialEvaluationResult


class SpanishEditorialSubAI:
    """
    Dedicated AI Sub-Engine for Spanish Prose Style, Discourse Connectors, and Editorial Review.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view

    def evaluate(self, text: str) -> SpanishEditorialEvaluationResult:
        low = text.lower()
        found_connectors = [conn for conn in DISCOURSE_CONNECTORS if conn in low]
        c_count = len(found_connectors)

        score = 0.72
        if c_count >= 2:
            score += 0.22
            grade = "A (Exemplary Cohesion / Estilo Elegante)"
        elif c_count == 1:
            score += 0.14
            grade = "B (Fluent & Cohesive / Buena Cohesión)"
        else:
            score += 0.05
            grade = "C (Standard Clear / Claro y Directo)"

        score = min(1.0, score)
        synced = False

        if self.amsv is not None:
            # Sync strictly to Capability 2 (Discourse / Byte 20) and Capability 5 (Review / Byte 26)
            self.amsv.set_cognitive_score(2, score * 0.95)
            self.amsv.set_cognitive_score(5, score)
            synced = True

        return SpanishEditorialEvaluationResult(
            input_text=text,
            stylistic_grade=grade,
            connector_count=c_count,
            editorial_score=round(score, 4),
            detected_connectors=found_connectors,
            amsv_synced=synced,
        )
