"""
grammar_parallel_cores package - BandhuPrime & Solo Rock Grammar Engines x 6 Languages Matrix.
"""

from .grammar_cores_orchestrator import GrammarParallelCoresOrchestrator
from .drive_core.linguistic_drive_core import LinguisticDriveCore
from .master_synthesis.master_grammar_synthesis import MasterGrammarSynthesisCore
from .engine_a_written_grammar.synthesis.engine_a_synthesis import EngineAWrittenGrammarSynthesis
from .engine_b_verbal_communication.synthesis.engine_b_synthesis import EngineBVerbalCommunicationSynthesis
from .engine_c_phonology_voice.synthesis.engine_c_synthesis import EngineCPhonologyVoiceSynthesis
from .engine_d_cognitive_examination.synthesis.engine_d_synthesis import EngineDCognitiveExaminationSynthesis

__all__ = [
    "GrammarParallelCoresOrchestrator",
    "LinguisticDriveCore",
    "MasterGrammarSynthesisCore",
    "EngineAWrittenGrammarSynthesis",
    "EngineBVerbalCommunicationSynthesis",
    "EngineCPhonologyVoiceSynthesis",
    "EngineDCognitiveExaminationSynthesis",
]
