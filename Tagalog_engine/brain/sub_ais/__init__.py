"""
Tagalog Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import TagalogSyntaxSubAI, TagalogSyntaxEvaluation, TagalogSyntaxEvaluationResult
from .phonology_sub_ai import TagalogPhonologySubAI, TagalogPhonologyEvaluation, TagalogPhonologyEvaluationResult
from .pragmatic_sub_ai import TagalogPragmaticSubAI, TagalogPragmaticEvaluation, TagalogPragmaticEvaluationResult
from .editorial_sub_ai import TagalogEditorialSubAI, TagalogEditorialEvaluation, TagalogEditorialEvaluationResult

__all__ = [
    "TagalogSyntaxSubAI", "TagalogSyntaxEvaluation", "TagalogSyntaxEvaluationResult",
    "TagalogPhonologySubAI", "TagalogPhonologyEvaluation", "TagalogPhonologyEvaluationResult",
    "TagalogPragmaticSubAI", "TagalogPragmaticEvaluation", "TagalogPragmaticEvaluationResult",
    "TagalogEditorialSubAI", "TagalogEditorialEvaluation", "TagalogEditorialEvaluationResult",
]
