"""
German Engine — Tasks Package
"""

from .grammar_check import GermanGrammarChecker
from .email_pipeline import GermanEmailPipeline
from .composition_pipeline import GermanCompositionPipeline

__all__ = [
    "GermanGrammarChecker",
    "GermanEmailPipeline",
    "GermanCompositionPipeline"
]
