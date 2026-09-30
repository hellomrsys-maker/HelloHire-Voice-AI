"""
English Brain Analysis Package.
Includes high-level cognitive and pragmatic analysis modules:
ambiguity ranking, discourse parsing (RST), figurative language detection,
intent mapping (speech acts), presupposition checking, and semantic drift monitoring.
"""

from English_engine.brain.Analysis.ambiguity_ranker import AmbiguityRanker, AmbiguityReport, AmbiguityCandidate
from English_engine.brain.Analysis.discourse_parser import DiscourseParser, DiscourseTree, ElementaryDiscourseUnit, RhetoricalRelation
from English_engine.brain.Analysis.figurative_detector import FigurativeDetector, FigurativeAnalysisReport, FigurativeInstance
from English_engine.brain.Analysis.intent_mapper import IntentMapper, SpeechActClassification
from English_engine.brain.Analysis.presupposition_check import PresuppositionChecker, PresuppositionReport, PresuppositionTrigger
from English_engine.brain.Analysis.drift_monitor import DriftMonitor, DriftMetrics

__all__ = [
    "AmbiguityRanker",
    "AmbiguityReport",
    "AmbiguityCandidate",
    "DiscourseParser",
    "DiscourseTree",
    "ElementaryDiscourseUnit",
    "RhetoricalRelation",
    "FigurativeDetector",
    "FigurativeAnalysisReport",
    "FigurativeInstance",
    "IntentMapper",
    "SpeechActClassification",
    "PresuppositionChecker",
    "PresuppositionReport",
    "PresuppositionTrigger",
    "DriftMonitor",
    "DriftMetrics",
]
