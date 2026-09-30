"""
Thai Language Engine Orchestrator
Master Cognitive Orchestrator for Thai (ภาษาไทย).
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from typing import Dict, Any, Optional
from Thai_engine.six_language_matrix.thai_matrix_bridge import ThaiMatrixBridge
from Thai_engine.brain.sub_ais.syntax_sub_ai import ThaiSyntaxSubAI
from Thai_engine.brain.sub_ais.phonology_sub_ai import ThaiPhonologySubAI
from Thai_engine.brain.sub_ais.pragmatic_sub_ai import ThaiPragmaticSubAI
from Thai_engine.brain.sub_ais.editorial_sub_ai import ThaiEditorialSubAI
from Thai_engine.brain.task.grammar_check import ThaiGrammarChecker
from Thai_engine.brain.task.email_pipeline import ThaiEmailPipeline
from Thai_engine.brain.task.composition_pipeline import ThaiCompositionPipeline
from Thai_engine.brain.skills.generation import generate_thai_sentence
from Thai_engine.brain.skills.classifier_engine import get_classifier_for_noun, audit_classifier_syntax
from Thai_engine.brain.skills.politeness_engine import audit_politeness_particles
from Thai_engine.brain.skills.tone_engine import calculate_syllable_tone
from Thai_engine.brain.skills.tokenization import tokenize_thai
from Thai_engine.brain.skills.rachasap_engine import detect_register

class ThaiEngineOrchestrator:
    """
    Central sovereign command orchestrator for the Thai Language Engine.
    """

    def __init__(self, shared_memory_buffer: Optional[bytearray] = None):
        # 1. Zero-Bridge Physical Memory Bridge (64 bytes, 0x54484149 'THAI')
        self.bridge = ThaiMatrixBridge(shared_memory_buffer)
        self.buffer = self.bridge.buffer

        # 2. Wire 4 Dedicated Sub-AIs directly to physical memory space
        self.syntax_sub_ai = ThaiSyntaxSubAI(self.buffer)
        self.phonology_sub_ai = ThaiPhonologySubAI(self.buffer)
        self.pragmatic_sub_ai = ThaiPragmaticSubAI(self.buffer)
        self.editorial_sub_ai = ThaiEditorialSubAI(self.buffer)

        # 3. Production Task Pipelines
        self.grammar_checker = ThaiGrammarChecker()
        self.email_pipeline = ThaiEmailPipeline()
        self.composition_pipeline = ThaiCompositionPipeline()

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Executes end-to-end cognitive analysis across all 4 Sub-AIs,
        updating the 64-byte AMSV physical memory vector in-place.
        """
        phon_res = self.phonology_sub_ai.process(text, self.buffer)
        syn_res = self.syntax_sub_ai.process(text, self.buffer)
        prag_res = self.pragmatic_sub_ai.process(text, self.buffer)
        edit_res = self.editorial_sub_ai.process(text, self.buffer)

        amsv_state = self.bridge.read_state()

        return {
            "text": text,
            "phonology": phon_res,
            "syntax": syn_res,
            "pragmatics": prag_res,
            "editorial": edit_res,
            "amsv_state": amsv_state
        }

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Runs multi-layer proofreading pipeline."""
        return self.grammar_checker.check(text)

    def generate_email(
        self,
        recipient: str,
        subject: str,
        message: str,
        gender: str = "male"
    ) -> Dict[str, Any]:
        """Synthesizes formal or polite Thai correspondence."""
        return self.email_pipeline.compose(
            recipient=recipient,
            subject=subject,
            message=message,
            gender=gender
        )

    def compose_prose(self, theme: str = "โอกาส", include_proverb: bool = True) -> Dict[str, Any]:
        """Synthesizes expressive prose with classifiers and proverbs."""
        return self.composition_pipeline.compose_narrative(theme=theme, include_proverb=include_proverb)

    def synthesize_sentence(
        self,
        subject: str,
        verb: str,
        object_noun: Optional[str] = None,
        numeral: Optional[str] = None,
        aspect_preverbal: Optional[str] = None,
        polite_particle: Optional[str] = None
    ) -> str:
        """Synthesizes an authentic Thai SVO sentence with numeral classifier and particles."""
        return generate_thai_sentence(
            subject=subject,
            verb=verb,
            object_noun=object_noun,
            numeral=numeral,
            aspect_preverbal=aspect_preverbal,
            polite_particle=polite_particle
        )
