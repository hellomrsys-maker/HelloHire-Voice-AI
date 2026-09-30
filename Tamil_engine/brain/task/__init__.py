"""Tamil Brain Task Pipelines Package."""

from Tamil_engine.brain.task.grammar_check import TamilGrammarChecker
from Tamil_engine.brain.task.email_pipeline import TamilEmailPipeline
from Tamil_engine.brain.task.composition_pipeline import TamilCompositionPipeline

__all__ = [
    "TamilGrammarChecker",
    "TamilEmailPipeline",
    "TamilCompositionPipeline"
]
