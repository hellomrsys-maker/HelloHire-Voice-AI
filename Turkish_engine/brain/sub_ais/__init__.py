"""Turkish Dedicated Sub-AIs Package."""

from .syntax_sub_ai import TurkishSyntaxSubAI, TurkishSyntaxEvaluation, TurkishSyntaxEvaluationResult
from .phonology_sub_ai import TurkishPhonologySubAI, TurkishPhonologyEvaluation, TurkishPhonologyEvaluationResult
from .pragmatic_sub_ai import TurkishPragmaticSubAI, TurkishPragmaticEvaluation, TurkishPragmaticEvaluationResult
from .editorial_sub_ai import TurkishEditorialSubAI, TurkishEditorialEvaluation, TurkishEditorialEvaluationResult

__all__ = [
    "TurkishSyntaxSubAI",
    "TurkishSyntaxEvaluation",
    "TurkishSyntaxEvaluationResult",
    "TurkishPhonologySubAI",
    "TurkishPhonologyEvaluation",
    "TurkishPhonologyEvaluationResult",
    "TurkishPragmaticSubAI",
    "TurkishPragmaticEvaluation",
    "TurkishPragmaticEvaluationResult",
    "TurkishEditorialSubAI",
    "TurkishEditorialEvaluation",
    "TurkishEditorialEvaluationResult"
]
