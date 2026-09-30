"""
Spanish Brain Task Pipelines Package.
"""

from .grammar_check import SpanishGrammarChecker
from .email_pipeline import SpanishEmailPipeline
from .composition_pipeline import SpanishCompositionPipeline

__all__ = [
    "SpanishGrammarChecker",
    "SpanishEmailPipeline",
    "SpanishCompositionPipeline",
]
