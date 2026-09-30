"""
Mandarin Sub-AIs Package.
Dedicated AI Sub-Engines for Syntax, Phonology, Pragmatics, and Editorial Review.
"""

from .syntax_sub_ai import (
    MandarinSyntaxSubAI,
    MandarinSyntaxEvaluationResult,
    MandarinSyntaxEvaluation,
)
from .phonology_sub_ai import (
    MandarinPhonologySubAI,
    MandarinPhonologyEvaluationResult,
    MandarinPhonologyEvaluation,
)
from .pragmatic_sub_ai import (
    MandarinPragmaticSubAI,
    MandarinPragmaticEvaluationResult,
    MandarinPragmaticEvaluation,
)
from .editorial_sub_ai import (
    MandarinEditorialSubAI,
    MandarinEditorialEvaluationResult,
    MandarinEditorialEvaluation,
)

__all__ = [
    "MandarinSyntaxSubAI",
    "MandarinSyntaxEvaluationResult",
    "MandarinSyntaxEvaluation",
    "MandarinPhonologySubAI",
    "MandarinPhonologyEvaluationResult",
    "MandarinPhonologyEvaluation",
    "MandarinPragmaticSubAI",
    "MandarinPragmaticEvaluationResult",
    "MandarinPragmaticEvaluation",
    "MandarinEditorialSubAI",
    "MandarinEditorialEvaluationResult",
    "MandarinEditorialEvaluation",
]
