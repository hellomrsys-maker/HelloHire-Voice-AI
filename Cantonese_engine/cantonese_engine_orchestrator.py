"""
Cantonese Language Engine Orchestrator
Master Cognitive Orchestrator for Cantonese (粵語 / 廣東話).
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from typing import Dict, Any, Optional
from Cantonese_engine.six_language_matrix.cantonese_matrix_bridge import CantoneseMatrixBridge
from Cantonese_engine.brain.sub_ais.syntax_sub_ai import CantoneseSyntaxSubAI
from Cantonese_engine.brain.sub_ais.phonology_sub_ai import CantonesePhonologySubAI
from Cantonese_engine.brain.sub_ais.pragmatic_sub_ai import CantonesePragmaticSubAI
from Cantonese_engine.brain.sub_ais.editorial_sub_ai import CantoneseEditorialSubAI
from Cantonese_engine.brain.task.grammar_check import CantoneseGrammarChecker
from Cantonese_engine.brain.task.email_pipeline import CantoneseEmailPipeline
from Cantonese_engine.brain.task.composition_pipeline import CantoneseCompositionPipeline
from Cantonese_engine.brain.skills.generation import generate_cantonese_sentence, generate_comparative
from Cantonese_engine.brain.skills.tone_engine import text_to_jyutping, analyze_character_tone
from Cantonese_engine.brain.skills.tokenization import tokenize_cantonese
from Cantonese_engine.brain.skills.classifier_engine import get_classifier_for_noun, parse_classifier_phrase

class CantoneseEngineOrchestrator:
    """
    Central sovereign command orchestrator for the Cantonese Language Engine.
    """

    def __init__(self, shared_memory_buffer: Optional[bytearray] = None):
        # 1. Zero-Bridge Physical Memory Bridge (64 bytes, 0x59554554 'YUET')
        self.bridge = CantoneseMatrixBridge(shared_memory_buffer)
        self.buffer = self.bridge.buffer

        # 2. Wire 4 Dedicated Sub-AIs directly to physical memory space
        self.syntax_sub_ai = CantoneseSyntaxSubAI(self.buffer)
        self.phonology_sub_ai = CantonesePhonologySubAI(self.buffer)
        self.pragmatic_sub_ai = CantonesePragmaticSubAI(self.buffer)
        self.editorial_sub_ai = CantoneseEditorialSubAI(self.buffer)

        # 3. Production Task Pipelines
        self.grammar_checker = CantoneseGrammarChecker()
        self.email_pipeline = CantoneseEmailPipeline()
        self.composition_pipeline = CantoneseCompositionPipeline()

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
        register: str = "formal"
    ) -> Dict[str, Any]:
        """Synthesizes formal or colloquial business correspondence."""
        return self.email_pipeline.compose(
            recipient=recipient,
            subject=subject,
            message=message,
            register=register
        )

    def compose_prose(self, topic: str, include_idiom: bool = True) -> Dict[str, Any]:
        """Synthesizes rich prose with cultural idioms."""
        return self.composition_pipeline.compose_narrative(topic=topic, include_idiom=include_idiom)

    def synthesize_sentence(
        self,
        subject: str,
        verb: str,
        theme_object: Optional[str] = None,
        recipient_io: Optional[str] = None,
        aspect: Optional[str] = None,
        adverb: Optional[str] = None,
        sfp: Optional[str] = None
    ) -> str:
        """Synthesizes an authentic Cantonese sentence enforcing DOC inversion."""
        return generate_cantonese_sentence(
            subject=subject,
            verb=verb,
            theme_object=theme_object,
            recipient_io=recipient_io,
            aspect=aspect,
            adverb=adverb,
            sfp=sfp
        )

    def synthesize_comparative(self, subject_a: str, subject_b: str, adjective: str) -> str:
        """Synthesizes a canonical comparative clause (A + Adj + 過 + B)."""
        return generate_comparative(subject_a, subject_b, adjective)
