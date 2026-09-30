"""
Ukrainian Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import UkrainianSyntaxSubAI, UkrainianSyntaxEvaluation, UkrainianSyntaxEvaluationResult
from .phonology_sub_ai import UkrainianPhonologySubAI, UkrainianPhonologyEvaluation, UkrainianPhonologyEvaluationResult
from .pragmatic_sub_ai import UkrainianPragmaticSubAI, UkrainianPragmaticEvaluation, UkrainianPragmaticEvaluationResult
from .editorial_sub_ai import UkrainianEditorialSubAI, UkrainianEditorialEvaluation, UkrainianEditorialEvaluationResult

__all__ = [
    "UkrainianSyntaxSubAI", "UkrainianSyntaxEvaluation", "UkrainianSyntaxEvaluationResult",
    "UkrainianPhonologySubAI", "UkrainianPhonologyEvaluation", "UkrainianPhonologyEvaluationResult",
    "UkrainianPragmaticSubAI", "UkrainianPragmaticEvaluation", "UkrainianPragmaticEvaluationResult",
    "UkrainianEditorialSubAI", "UkrainianEditorialEvaluation", "UkrainianEditorialEvaluationResult",
]
