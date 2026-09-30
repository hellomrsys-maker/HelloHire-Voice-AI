"""
English Brain Task Pipeline Package.
Provides end-to-end task execution pipelines:
grammar checking, summarization, translation, TTS, STT, QA, and register rewriting.
"""

from English_engine.brain.task.grammar_check import GrammarCheckerPipeline, GrammarCheckResult
from English_engine.brain.task.summarize import Summarizer, SummaryResult
from English_engine.brain.task.translate import CrossLingualTranslator, TranslationResult
from English_engine.brain.task.tts_pipeline import TTSPipeline, TTSOutput, PhonemeFrame
from English_engine.brain.task.stt_pipeline import STTPipeline, STTOutput, TimedWord
from English_engine.brain.task.qa import QuestionAnsweringEngine, QAResult
from English_engine.brain.task.rewrite_register import RegisterRewriter, RewriteResult

__all__ = [
    "GrammarCheckerPipeline",
    "GrammarCheckResult",
    "Summarizer",
    "SummaryResult",
    "CrossLingualTranslator",
    "TranslationResult",
    "TTSPipeline",
    "TTSOutput",
    "PhonemeFrame",
    "STTPipeline",
    "STTOutput",
    "TimedWord",
    "QuestionAnsweringEngine",
    "QAResult",
    "RegisterRewriter",
    "RewriteResult",
]
