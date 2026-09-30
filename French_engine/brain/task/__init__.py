"""
French Task Pipelines Package.
Exports grammar check, email generation, and composition pipelines.
"""

from .grammar_check import FrenchGrammarChecker
from .email_pipeline import FrenchEmailPipeline
from .composition_pipeline import FrenchCompositionPipeline

__all__ = [
    "FrenchGrammarChecker",
    "FrenchEmailPipeline",
    "FrenchCompositionPipeline",
]
