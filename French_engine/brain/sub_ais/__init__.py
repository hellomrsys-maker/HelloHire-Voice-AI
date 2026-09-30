"""
French Sub-AIs Package.
Exports FrenchSyntaxSubAI, FrenchPhonologySubAI, FrenchPragmaticSubAI, FrenchEditorialSubAI.
"""

from .syntax_sub_ai import FrenchSyntaxSubAI, FrenchSyntaxEvaluation, FrenchSyntaxEvaluationResult
from .phonology_sub_ai import FrenchPhonologySubAI, FrenchPhonologyEvaluation, FrenchPhonologyEvaluationResult
from .pragmatic_sub_ai import FrenchPragmaticSubAI, FrenchPragmaticEvaluation, FrenchPragmaticEvaluationResult
from .editorial_sub_ai import FrenchEditorialSubAI, FrenchEditorialEvaluation, FrenchEditorialEvaluationResult

__all__ = [
    "FrenchSyntaxSubAI",
    "FrenchSyntaxEvaluation",
    "FrenchSyntaxEvaluationResult",
    "FrenchPhonologySubAI",
    "FrenchPhonologyEvaluation",
    "FrenchPhonologyEvaluationResult",
    "FrenchPragmaticSubAI",
    "FrenchPragmaticEvaluation",
    "FrenchPragmaticEvaluationResult",
    "FrenchEditorialSubAI",
    "FrenchEditorialEvaluation",
    "FrenchEditorialEvaluationResult",
]
