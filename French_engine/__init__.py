"""
French Language Engine Ecosystem.
Exposes the FrenchEngineOrchestrator and sub-modules adhering to The Zero-Bridge Synchronous Memory Rule.
"""

from .french_engine_orchestrator import FrenchEngineOrchestrator, FrenchEngineAnalysisResult
from .brain.skills.tokenization import FrenchTokenizer
from .brain.skills.pos_tagging import FrenchPOSTagger
from .brain.skills.verb_conjugator import FrenchVerbConjugator
from .brain.skills.liaison_elision_engine import LiaisonElisionEngine
from .brain.skills.agreement_engine import FrenchAgreementEngine
from .brain.skills.clitic_engine import FrenchCliticEngine
from .brain.skills.pragmatics_engine import FrenchPragmaticsEngine
from .brain.skills.parsing import FrenchParser, FrenchSentenceStructure
from .brain.skills.generation import FrenchGenerator

from .brain.sub_ais.syntax_sub_ai import FrenchSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import FrenchPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import FrenchPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import FrenchEditorialSubAI

from .six_language_matrix.python.french_matrix_bridge import FrenchMatrixBridge

__all__ = [
    "FrenchEngineOrchestrator",
    "FrenchEngineAnalysisResult",
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
    "FrenchSyntaxSubAI",
    "FrenchPhonologySubAI",
    "FrenchPragmaticSubAI",
    "FrenchEditorialSubAI",
    "FrenchMatrixBridge",
]
