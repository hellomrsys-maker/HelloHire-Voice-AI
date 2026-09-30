"""
Tamil Language Engine Orchestrator
Master Cognitive Orchestrator for Tamil (தமிழ்).
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from typing import Dict, Any, Optional
from Tamil_engine.six_language_matrix.tamil_matrix_bridge import TamilMatrixBridge
from Tamil_engine.brain.sub_ais.syntax_sub_ai import TamilSyntaxSubAI
from Tamil_engine.brain.sub_ais.phonology_sub_ai import TamilPhonologySubAI
from Tamil_engine.brain.sub_ais.pragmatic_sub_ai import TamilPragmaticSubAI
from Tamil_engine.brain.sub_ais.editorial_sub_ai import TamilEditorialSubAI
from Tamil_engine.brain.task.grammar_check import TamilGrammarChecker
from Tamil_engine.brain.task.email_pipeline import TamilEmailPipeline
from Tamil_engine.brain.task.composition_pipeline import TamilCompositionPipeline
from Tamil_engine.brain.skills.generation import (
    generate_sov_sentence,
    generate_dative_experiencer_sentence
)
from Tamil_engine.brain.skills.case_engine import inflect_case, analyze_noun_case
from Tamil_engine.brain.skills.sandhi_engine import audit_sandhi, apply_sandhi
from Tamil_engine.brain.skills.retroflex_engine import analyze_phonological_profile

class TamilEngineOrchestrator:
    """
    Central sovereign command orchestrator for the Tamil Language Engine.
    """

    def __init__(self, shared_memory_buffer: Optional[bytearray] = None):
        # 1. Zero-Bridge Physical Memory Bridge (64 bytes, 0x54414D4C 'TAML')
        self.bridge = TamilMatrixBridge(shared_memory_buffer)
        self.buffer = self.bridge.buffer

        # 2. Wire 4 Dedicated Sub-AIs directly to physical memory space
        self.syntax_sub_ai = TamilSyntaxSubAI(self.buffer)
        self.phonology_sub_ai = TamilPhonologySubAI(self.buffer)
        self.pragmatic_sub_ai = TamilPragmaticSubAI(self.buffer)
        self.editorial_sub_ai = TamilEditorialSubAI(self.buffer)

        # 3. Production Task Pipelines
        self.grammar_checker = TamilGrammarChecker()
        self.email_pipeline = TamilEmailPipeline()
        self.composition_pipeline = TamilCompositionPipeline()

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
        """Synthesizes formal administrative or colloquial correspondence."""
        return self.email_pipeline.compose(
            recipient=recipient,
            subject=subject,
            message=message,
            register=register
        )

    def compose_prose(self, theme: str = "அறிவு", include_proverb: bool = True) -> Dict[str, Any]:
        """Synthesizes prose with classical motifs and proverbs."""
        return self.composition_pipeline.compose_narrative(theme=theme, include_proverb=include_proverb)

    def synthesize_sov_sentence(
        self,
        subject: str,
        verb: str,
        object_noun: Optional[str] = None,
        indirect_object: Optional[str] = None,
        adverb: Optional[str] = None
    ) -> str:
        """Synthesizes an authentic Tamil SOV sentence with case and sandhi."""
        return generate_sov_sentence(
            subject=subject,
            verb=verb,
            object_noun=object_noun,
            indirect_object=indirect_object,
            adverb=adverb
        )

    def synthesize_dative_experiencer(
        self,
        experiencer: str,
        modal_verb: str,
        theme: Optional[str] = None
    ) -> str:
        """Synthesizes a dative experiencer sentence (e.g. எனக்கு தமிழ் தெரியும்)."""
        return generate_dative_experiencer_sentence(
            experiencer=experiencer,
            modal_verb=modal_verb,
            theme=theme
        )
