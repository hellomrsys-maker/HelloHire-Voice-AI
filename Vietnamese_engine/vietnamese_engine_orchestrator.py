"""
Vietnamese Language Engine Orchestrator
Master Cognitive Orchestrator for Vietnamese (Tiếng Việt).
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from typing import Dict, Any, Optional
from Vietnamese_engine.six_language_matrix.vietnamese_matrix_bridge import VietnameseMatrixBridge
from Vietnamese_engine.brain.sub_ais.syntax_sub_ai import VietnameseSyntaxSubAI
from Vietnamese_engine.brain.sub_ais.phonology_sub_ai import VietnamesePhonologySubAI
from Vietnamese_engine.brain.sub_ais.pragmatic_sub_ai import VietnamesePragmaticSubAI
from Vietnamese_engine.brain.sub_ais.editorial_sub_ai import VietnameseEditorialSubAI
from Vietnamese_engine.brain.task.grammar_check import VietnameseGrammarChecker
from Vietnamese_engine.brain.task.email_pipeline import VietnameseEmailPipeline
from Vietnamese_engine.brain.task.composition_pipeline import VietnameseCompositionPipeline
from Vietnamese_engine.brain.skills.generation import VietnameseGenerator
from Vietnamese_engine.brain.skills.tone_engine import VietnameseToneEngine

class VietnameseEngineOrchestrator:
    """
    Central sovereign command orchestrator for the Vietnamese Language Engine.
    """

    def __init__(self, shared_memory_buffer: Optional[bytearray] = None):
        # 1. Zero-Bridge Physical Memory Bridge (64 bytes, 0x56494554 'VIET')
        self.bridge = VietnameseMatrixBridge(shared_memory_buffer)
        self.buffer = self.bridge.buffer

        # 2. Wire 4 Dedicated Sub-AIs directly to physical memory space
        self.syntax_sub_ai = VietnameseSyntaxSubAI(self.buffer)
        self.phonology_sub_ai = VietnamesePhonologySubAI(self.buffer)
        self.pragmatic_sub_ai = VietnamesePragmaticSubAI(self.buffer)
        self.editorial_sub_ai = VietnameseEditorialSubAI(self.buffer)

        # 3. Production Task Pipelines
        self.grammar_checker = VietnameseGrammarChecker()
        self.email_pipeline = VietnameseEmailPipeline()
        self.composition_pipeline = VietnameseCompositionPipeline()

        # 4. Core Skills
        self.generator = VietnameseGenerator()
        self.tone_engine = VietnameseToneEngine()

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

    def check_grammar(self, text: str, speaker_term: Optional[str] = None, listener_term: Optional[str] = None) -> Dict[str, Any]:
        """Runs multi-layer proofreading pipeline."""
        return self.grammar_checker.check_text(text, speaker_term, listener_term)

    def generate_formal_email(
        self,
        recipient_name: str,
        recipient_title: str,
        body: str,
        sender_name: str
    ) -> str:
        """Synthesizes an administrative or corporate Vietnamese letter."""
        return self.email_pipeline.generate_formal_email(
            recipient_name=recipient_name,
            recipient_title=recipient_title,
            body=body,
            sender_name=sender_name
        )

    def compose_prose(self, text: str, theme: Optional[str] = None, adapt_dialect: bool = True) -> str:
        """Adapts regional vocabulary and optionally injects classical Thành ngữ idioms."""
        res = self.composition_pipeline.adapt_southern_to_northern_standard(text) if adapt_dialect else text
        if theme:
            res = self.composition_pipeline.inject_thanh_ngu(res, theme)
        return res

    def synthesize_svo_sentence(
        self,
        subject: Optional[str],
        verb: str,
        direct_object_noun: Optional[str] = None,
        quantifier: Optional[str] = None,
        classifier: Optional[str] = None,
        tense: Optional[str] = None,
        aspect: Optional[str] = None,
        negative: bool = False
    ) -> str:
        """Synthesizes an SVO sentence with classifiers and TAM markers."""
        return self.generator.generate_svo_clause(
            subject=subject,
            verb=verb,
            direct_object_noun=direct_object_noun,
            quantifier=quantifier,
            classifier=classifier,
            tense=tense,
            aspect=aspect,
            negative=negative
        )
