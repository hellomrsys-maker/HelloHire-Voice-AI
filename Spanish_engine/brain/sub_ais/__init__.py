"""
Spanish Sub-AIs Package.
Dedicated AI Sub-Engines for Syntax, Phonology, Pragmatics, and Editorial Review.
"""

from .syntax_sub_ai import (
    SpanishSyntaxSubAI,
    SpanishSyntaxEvaluationResult,
    SpanishSyntaxEvaluation,
)
from .phonology_sub_ai import (
    SpanishPhonologySubAI,
    SpanishPhonologyEvaluationResult,
    SpanishPhonologyEvaluation,
)
from .pragmatic_sub_ai import (
    SpanishPragmaticSubAI,
    SpanishPragmaticEvaluationResult,
    SpanishPragmaticEvaluation,
)
from .editorial_sub_ai import (
    SpanishEditorialSubAI,
    SpanishEditorialEvaluationResult,
    SpanishEditorialEvaluation,
)

__all__ = [
    "SpanishSyntaxSubAI",
    "SpanishSyntaxEvaluationResult",
    "SpanishSyntaxEvaluation",
    "SpanishPhonologySubAI",
    "SpanishPhonologyEvaluationResult",
    "SpanishPhonologyEvaluation",
    "SpanishPragmaticSubAI",
    "SpanishPragmaticEvaluationResult",
    "SpanishPragmaticEvaluation",
    "SpanishEditorialSubAI",
    "SpanishEditorialEvaluationResult",
    "SpanishEditorialEvaluation",
]
