"""
Marathi Dedicated Sub-AIs Package.
"""
from .syntax_sub_ai import MarathiSyntaxSubAI, MarathiSyntaxEvaluation, MarathiSyntaxEvaluationResult
from .phonology_sub_ai import MarathiPhonologySubAI, MarathiPhonologyEvaluation, MarathiPhonologyEvaluationResult
from .pragmatic_sub_ai import MarathiPragmaticSubAI, MarathiPragmaticEvaluation, MarathiPragmaticEvaluationResult
from .editorial_sub_ai import MarathiEditorialSubAI, MarathiEditorialEvaluation, MarathiEditorialEvaluationResult

__all__ = [
    "MarathiSyntaxSubAI", "MarathiSyntaxEvaluation", "MarathiSyntaxEvaluationResult",
    "MarathiPhonologySubAI", "MarathiPhonologyEvaluation", "MarathiPhonologyEvaluationResult",
    "MarathiPragmaticSubAI", "MarathiPragmaticEvaluation", "MarathiPragmaticEvaluationResult",
    "MarathiEditorialSubAI", "MarathiEditorialEvaluation", "MarathiEditorialEvaluationResult",
]
