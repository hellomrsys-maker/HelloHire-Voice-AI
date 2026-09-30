"""
Hindustani Engine Brain Skills Package.
Exposes tokenization, POS tagging, verb conjugation, ergative split, oblique case,
compound verbs, pragmatics, parsing, and generation.
"""

from .tokenization import HindustaniTokenizer
from .pos_tagging import HindustaniPOSTagger
from .verb_conjugator import HindustaniVerbConjugator
from .ergative_engine import ErgativeSplitEngine
from .oblique_case_engine import ObliqueCaseEngine
from .compound_verb_engine import CompoundVerbEngine
from .pragmatics_engine import HindustaniPragmaticsEngine
from .parsing import HindustaniParser, HindustaniSentenceStructure
from .generation import HindustaniGenerator

__all__ = [
    "HindustaniTokenizer",
    "HindustaniPOSTagger",
    "HindustaniVerbConjugator",
    "ErgativeSplitEngine",
    "ObliqueCaseEngine",
    "CompoundVerbEngine",
    "HindustaniPragmaticsEngine",
    "HindustaniParser",
    "HindustaniSentenceStructure",
    "HindustaniGenerator",
]
