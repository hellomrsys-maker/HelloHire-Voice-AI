"""
Hindustani Sub-AIs Package.
Exports HindustaniSyntaxSubAI, HindustaniPhonologySubAI, HindustaniPragmaticSubAI, HindustaniEditorialSubAI.
"""

from .syntax_sub_ai import HindustaniSyntaxSubAI, HindustaniSyntaxEvaluation, HindustaniSyntaxEvaluationResult
from .phonology_sub_ai import HindustaniPhonologySubAI, HindustaniPhonologyEvaluation, HindustaniPhonologyEvaluationResult
from .pragmatic_sub_ai import HindustaniPragmaticSubAI, HindustaniPragmaticEvaluation, HindustaniPragmaticEvaluationResult
from .editorial_sub_ai import HindustaniEditorialSubAI, HindustaniEditorialEvaluation, HindustaniEditorialEvaluationResult

__all__ = [
    "HindustaniSyntaxSubAI",
    "HindustaniSyntaxEvaluation",
    "HindustaniSyntaxEvaluationResult",
    "HindustaniPhonologySubAI",
    "HindustaniPhonologyEvaluation",
    "HindustaniPhonologyEvaluationResult",
    "HindustaniPragmaticSubAI",
    "HindustaniPragmaticEvaluation",
    "HindustaniPragmaticEvaluationResult",
    "HindustaniEditorialSubAI",
    "HindustaniEditorialEvaluation",
    "HindustaniEditorialEvaluationResult",
]
