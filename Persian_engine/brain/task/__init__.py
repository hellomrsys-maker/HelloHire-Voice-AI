"""
Persian Brain Task Package
"""

from Persian_engine.brain.task.grammar_check import PersianGrammarChecker
from Persian_engine.brain.task.email_pipeline import PersianEmailPipeline
from Persian_engine.brain.task.composition_pipeline import PersianCompositionPipeline

__all__ = [
    "PersianGrammarChecker",
    "PersianEmailPipeline",
    "PersianCompositionPipeline",
]
