"""
Punjabi Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import PunjabiSyntaxSubAI, PunjabiSyntaxEvaluation, PunjabiSyntaxEvaluationResult
from .phonology_sub_ai import PunjabiPhonologySubAI, PunjabiPhonologyEvaluation, PunjabiPhonologyEvaluationResult
from .pragmatic_sub_ai import PunjabiPragmaticSubAI, PunjabiPragmaticEvaluation, PunjabiPragmaticEvaluationResult
from .editorial_sub_ai import PunjabiEditorialSubAI, PunjabiEditorialEvaluation, PunjabiEditorialEvaluationResult

__all__ = [
    "PunjabiSyntaxSubAI", "PunjabiSyntaxEvaluation", "PunjabiSyntaxEvaluationResult",
    "PunjabiPhonologySubAI", "PunjabiPhonologyEvaluation", "PunjabiPhonologyEvaluationResult",
    "PunjabiPragmaticSubAI", "PunjabiPragmaticEvaluation", "PunjabiPragmaticEvaluationResult",
    "PunjabiEditorialSubAI", "PunjabiEditorialEvaluation", "PunjabiEditorialEvaluationResult",
]
