"""
French Engine Brain Skills Package.
Exposes tokenization, POS tagging, verb conjugation, liaison/elision,
agreement, clitic ordering, pragmatics, parsing, and generation.
"""

from .tokenization import FrenchTokenizer
from .pos_tagging import FrenchPOSTagger
from .verb_conjugator import FrenchVerbConjugator
from .liaison_elision_engine import LiaisonElisionEngine
from .agreement_engine import FrenchAgreementEngine
from .clitic_engine import FrenchCliticEngine
from .pragmatics_engine import FrenchPragmaticsEngine
from .parsing import FrenchParser, FrenchSentenceStructure
from .generation import FrenchGenerator

__all__ = [
    "FrenchTokenizer",
    "FrenchPOSTagger",
    "FrenchVerbConjugator",
    "LiaisonElisionEngine",
    "FrenchAgreementEngine",
    "FrenchCliticEngine",
    "FrenchPragmaticsEngine",
    "FrenchParser",
    "FrenchSentenceStructure",
    "FrenchGenerator",
]
