"""
Persian Language Engine Orchestrator
Master Cognitive Orchestrator for Persian (Farsi/Dari).
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from typing import Dict, Any, Optional
from Persian_engine.six_language_matrix.persian_matrix_bridge import PersianMatrixBridge
from Persian_engine.brain.sub_ais.syntax_sub_ai import PersianSyntaxSubAI
from Persian_engine.brain.sub_ais.phonology_sub_ai import PersianPhonologySubAI
from Persian_engine.brain.sub_ais.pragmatic_sub_ai import PersianPragmaticSubAI
from Persian_engine.brain.sub_ais.editorial_sub_ai import PersianEditorialSubAI
from Persian_engine.brain.task.grammar_check import PersianGrammarChecker
from Persian_engine.brain.task.email_pipeline import PersianEmailPipeline
from Persian_engine.brain.task.composition_pipeline import PersianCompositionPipeline
from Persian_engine.brain.skills.verb_conjugator import PersianVerbConjugator
from Persian_engine.brain.skills.generation import PersianGenerator

class PersianEngineOrchestrator:
    """
    Central sovereign command orchestrator for the Persian Language Engine.
    """

    def __init__(self, shared_memory_buffer: Optional[bytearray] = None):
        # 1. Initialize Zero-Bridge Physical Memory Bridge (64 bytes, 0x46415253 'FARS')
        self.bridge = PersianMatrixBridge(shared_memory_buffer)
        self.buffer = self.bridge.buffer

        # 2. Wire 4 Dedicated Sub-AIs directly to the physical memory space
        self.syntax_sub_ai = PersianSyntaxSubAI(self.buffer)
        self.phonology_sub_ai = PersianPhonologySubAI(self.buffer)
        self.pragmatic_sub_ai = PersianPragmaticSubAI(self.buffer)
        self.editorial_sub_ai = PersianEditorialSubAI(self.buffer)

        # 3. Production Task Pipelines
        self.grammar_checker = PersianGrammarChecker()
        self.email_pipeline = PersianEmailPipeline()
        self.composition_pipeline = PersianCompositionPipeline()

        # 4. Core Skills
        self.conjugator = PersianVerbConjugator()
        self.generator = PersianGenerator()

    def process_text(self, text: str, target_register: str = "formal") -> Dict[str, Any]:
        """
        Executes end-to-end cognitive analysis across all 4 Sub-AIs,
        updating the 64-byte AMSV physical memory vector in-place.
        """
        # Execute Sub-AIs with direct in-place hardware writes
        phon_res = self.phonology_sub_ai.process(text, self.buffer)
        syn_res = self.syntax_sub_ai.process(text, self.buffer)
        prag_res = self.pragmatic_sub_ai.process(text, self.buffer, target_register=target_register)
        edit_res = self.editorial_sub_ai.process(text, self.buffer)

        # Read back unified physical memory state
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
        """Runs the multi-layer proofreading pipeline."""
        return self.grammar_checker.check_text(text)

    def generate_formal_email(
        self,
        recipient_name: str,
        recipient_title: str,
        body: str,
        sender_name: str,
        is_high_taarof: bool = True
    ) -> str:
        """Synthesizes an authentic formal Persian administrative letter."""
        return self.email_pipeline.generate_formal_email(
            recipient_name=recipient_name,
            recipient_title=recipient_title,
            body_points=body,
            sender_name=sender_name,
            is_high_taarof=is_high_taarof
        )

    def compose_prose(self, base_text: str, theme: Optional[str] = None) -> str:
        """Normalizes colloquialisms and injects classical proverbs."""
        norm = self.composition_pipeline.normalize_colloquial_to_literary(base_text)
        if theme:
            return self.composition_pipeline.inject_classical_proverb(norm, theme)
        return norm

    def conjugate_verb(self, infinitive: str, tense: str, person: int, negative: bool = False) -> str:
        """Conjugates a Persian verb."""
        return self.conjugator.conjugate(infinitive, tense, person, negative)

    def synthesize_sov_sentence(
        self,
        subject: Optional[str],
        direct_object: Optional[str],
        verb_infinitive: str,
        tense: str = "past_simple",
        person: int = 1,
        is_definite_object: bool = True,
        negative: bool = False
    ) -> str:
        """Synthesizes an SOV sentence with DOM marker 'rā' and verbal agreement."""
        return self.generator.generate_sov_clause(
            subject=subject,
            direct_object=direct_object,
            verb_infinitive=verb_infinitive,
            tense=tense,
            person=person,
            is_definite_object=is_definite_object,
            negative=negative
        )
