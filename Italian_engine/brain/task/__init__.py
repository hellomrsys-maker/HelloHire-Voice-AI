"""
Italian Engine — Task Pipelines Package
"""

from .grammar_check import ItalianGrammarChecker
from .email_pipeline import ItalianEmailPipeline
from .composition_pipeline import ItalianCompositionPipeline

__all__ = [
    "ItalianGrammarChecker",
    "ItalianEmailPipeline",
    "ItalianCompositionPipeline"
]
