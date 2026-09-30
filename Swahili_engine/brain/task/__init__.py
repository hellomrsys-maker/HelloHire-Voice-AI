"""
Swahili Engine Task Pipelines
"""

from .grammar_check import SwahiliGrammarChecker
from .email_pipeline import SwahiliEmailPipeline
from .composition_pipeline import SwahiliCompositionPipeline

__all__ = [
    "SwahiliGrammarChecker",
    "SwahiliEmailPipeline",
    "SwahiliCompositionPipeline"
]
