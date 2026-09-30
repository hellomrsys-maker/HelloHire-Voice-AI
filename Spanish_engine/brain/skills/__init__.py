"""
Spanish Brain Skills Package.
"""

from .tokenization import SpanishTokenizer, SpanishToken
from .pos_tagging import SpanishPOSTagger
from .parsing import SpanishParser, SpanishSentenceStructure
from .verb_conjugator import SpanishVerbConjugator
from .ser_estar_engine import SerEstarEngine
from .por_para_engine import PorParaEngine
from .clitic_engine import CliticEngine
from .pragmatics_engine import SpanishPragmaticsEngine
from .generation import SpanishGenerator

__all__ = [
    "SpanishTokenizer",
    "SpanishToken",
    "SpanishPOSTagger",
    "SpanishParser",
    "SpanishSentenceStructure",
    "SpanishVerbConjugator",
    "SerEstarEngine",
    "PorParaEngine",
    "CliticEngine",
    "SpanishPragmaticsEngine",
    "SpanishGenerator",
]
