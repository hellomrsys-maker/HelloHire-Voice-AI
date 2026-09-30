"""
Hindustani Language Engine Ecosystem (Hindi / Urdu).
Exposes the HindustaniEngineOrchestrator and sub-modules adhering to The Zero-Bridge Synchronous Memory Rule.
"""

from .hindustani_engine_orchestrator import HindustaniEngineOrchestrator, HindustaniEngineAnalysisResult
from .brain.skills.tokenization import HindustaniTokenizer
from .brain.skills.pos_tagging import HindustaniPOSTagger
from .brain.skills.verb_conjugator import HindustaniVerbConjugator
from .brain.skills.ergative_engine import ErgativeSplitEngine
from .brain.skills.oblique_case_engine import ObliqueCaseEngine
from .brain.skills.compound_verb_engine import CompoundVerbEngine
from .brain.skills.pragmatics_engine import HindustaniPragmaticsEngine
from .brain.skills.parsing import HindustaniParser, HindustaniSentenceStructure
from .brain.skills.generation import HindustaniGenerator

from .brain.sub_ais.syntax_sub_ai import HindustaniSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import HindustaniPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import HindustaniPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import HindustaniEditorialSubAI

from .six_language_matrix.python.hindustani_matrix_bridge import HindustaniMatrixBridge

__all__ = [
    "HindustaniEngineOrchestrator",
    "HindustaniEngineAnalysisResult",
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
    "HindustaniSyntaxSubAI",
    "HindustaniPhonologySubAI",
    "HindustaniPragmaticSubAI",
    "HindustaniEditorialSubAI",
    "HindustaniMatrixBridge",
]
