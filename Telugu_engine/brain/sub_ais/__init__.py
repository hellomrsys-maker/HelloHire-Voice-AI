"""
Telugu Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import TeluguSyntaxSubAI, TeluguSyntaxEvaluation, TeluguSyntaxEvaluationResult
from .phonology_sub_ai import TeluguPhonologySubAI, TeluguPhonologyEvaluation, TeluguPhonologyEvaluationResult
from .pragmatic_sub_ai import TeluguPragmaticSubAI, TeluguPragmaticEvaluation, TeluguPragmaticEvaluationResult
from .editorial_sub_ai import TeluguEditorialSubAI, TeluguEditorialEvaluation, TeluguEditorialEvaluationResult

__all__ = [
    "TeluguSyntaxSubAI", "TeluguSyntaxEvaluation", "TeluguSyntaxEvaluationResult",
    "TeluguPhonologySubAI", "TeluguPhonologyEvaluation", "TeluguPhonologyEvaluationResult",
    "TeluguPragmaticSubAI", "TeluguPragmaticEvaluation", "TeluguPragmaticEvaluationResult",
    "TeluguEditorialSubAI", "TeluguEditorialEvaluation", "TeluguEditorialEvaluationResult",
]
