"""
Hausa Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import HausaSyntaxSubAI, HausaSyntaxEvaluation, HausaSyntaxEvaluationResult
from .phonology_sub_ai import HausaPhonologySubAI, HausaPhonologyEvaluation, HausaPhonologyEvaluationResult
from .pragmatic_sub_ai import HausaPragmaticSubAI, HausaPragmaticEvaluation, HausaPragmaticEvaluationResult
from .editorial_sub_ai import HausaEditorialSubAI, HausaEditorialEvaluation, HausaEditorialEvaluationResult

__all__ = [
    "HausaSyntaxSubAI", "HausaSyntaxEvaluation", "HausaSyntaxEvaluationResult",
    "HausaPhonologySubAI", "HausaPhonologyEvaluation", "HausaPhonologyEvaluationResult",
    "HausaPragmaticSubAI", "HausaPragmaticEvaluation", "HausaPragmaticEvaluationResult",
    "HausaEditorialSubAI", "HausaEditorialEvaluation", "HausaEditorialEvaluationResult",
]
