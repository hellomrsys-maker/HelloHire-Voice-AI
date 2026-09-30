"""
Portuguese Engine Dedicated Sub-AIs Package.
Syncs with 64-byte physical Atomic Memory State Vector (AMSV).
"""

from .syntax_sub_ai import PortugueseSyntaxSubAI, PortugueseSyntaxEvaluation, PortugueseSyntaxEvaluationResult
from .phonology_sub_ai import PortuguesePhonologySubAI, PortuguesePhonologyEvaluation, PortuguesePhonologyEvaluationResult
from .pragmatic_sub_ai import PortuguesePragmaticSubAI, PortuguesePragmaticEvaluation, PortuguesePragmaticEvaluationResult
from .editorial_sub_ai import PortugueseEditorialSubAI, PortugueseEditorialEvaluation, PortugueseEditorialEvaluationResult

__all__ = [
    "PortugueseSyntaxSubAI",
    "PortugueseSyntaxEvaluation",
    "PortugueseSyntaxEvaluationResult",
    "PortuguesePhonologySubAI",
    "PortuguesePhonologyEvaluation",
    "PortuguesePhonologyEvaluationResult",
    "PortuguesePragmaticSubAI",
    "PortuguesePragmaticEvaluation",
    "PortuguesePragmaticEvaluationResult",
    "PortugueseEditorialSubAI",
    "PortugueseEditorialEvaluation",
    "PortugueseEditorialEvaluationResult",
]
