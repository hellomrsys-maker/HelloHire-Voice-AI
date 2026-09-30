"""
Hindustani Task Pipelines Package.
Exports grammar check, email generation, and composition pipelines.
"""

from .grammar_check import HindustaniGrammarChecker
from .email_pipeline import HindustaniEmailPipeline
from .composition_pipeline import HindustaniCompositionPipeline

__all__ = [
    "HindustaniGrammarChecker",
    "HindustaniEmailPipeline",
    "HindustaniCompositionPipeline",
]
