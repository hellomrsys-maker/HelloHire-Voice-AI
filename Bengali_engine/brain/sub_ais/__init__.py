"""
Bengali Engine Dedicated Sub-AIs Package.
Syncs with 64-byte physical Atomic Memory State Vector (AMSV).
"""

from .syntax_sub_ai import BengaliSyntaxSubAI, BengaliSyntaxEvaluation, BengaliSyntaxEvaluationResult
from .phonology_sub_ai import BengaliPhonologySubAI, BengaliPhonologyEvaluation, BengaliPhonologyEvaluationResult
from .pragmatic_sub_ai import BengaliPragmaticSubAI, BengaliPragmaticEvaluation, BengaliPragmaticEvaluationResult
from .editorial_sub_ai import BengaliEditorialSubAI, BengaliEditorialEvaluation, BengaliEditorialEvaluationResult

__all__ = [
    "BengaliSyntaxSubAI",
    "BengaliSyntaxEvaluation",
    "BengaliSyntaxEvaluationResult",
    "BengaliPhonologySubAI",
    "BengaliPhonologyEvaluation",
    "BengaliPhonologyEvaluationResult",
    "BengaliPragmaticSubAI",
    "BengaliPragmaticEvaluation",
    "BengaliPragmaticEvaluationResult",
    "BengaliEditorialSubAI",
    "BengaliEditorialEvaluation",
    "BengaliEditorialEvaluationResult",
]
