"""
German Engine — Master Orchestrator
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
task pipelines, and Zero-Bridge 64-byte AMSV physical synchronization.
"""

from typing import Dict, Any, Optional
from .six_language_matrix.german_matrix_bridge import GermanMatrixBridge, GERMAN_AMSV_SIZE
from .brain.skills.tokenization import tokenize_words, split_sentences, normalize_orthography
from .brain.skills.pos_tagging import tag_pos
from .brain.skills.generation import generate_noun_phrase
from .brain.skills.verb_conjugator import conjugate_present
from .brain.sub_ais.syntax_sub_ai import GermanSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import GermanPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import GermanPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import GermanEditorialSubAI
from .brain.task.grammar_check import GermanGrammarChecker
from .brain.task.email_pipeline import GermanEmailPipeline
from .brain.task.composition_pipeline import GermanCompositionPipeline

class GermanEngineOrchestrator:
    """
    Master Orchestrator for the German Cognitive Language Engine.
    Operates with zero-bridge synchronous memory synchronization on a 64-byte physical AMSV.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.bridge = GermanMatrixBridge(memory_buffer)
        self.syntax_sub_ai = GermanSyntaxSubAI()
        self.phonology_sub_ai = GermanPhonologySubAI()
        self.pragmatic_sub_ai = GermanPragmaticSubAI()
        self.editorial_sub_ai = GermanEditorialSubAI()
        self.grammar_checker = GermanGrammarChecker()
        self.email_pipeline = GermanEmailPipeline()
        self.composition_pipeline = GermanCompositionPipeline()

    @property
    def amsv_buffer(self) -> bytearray:
        return self.bridge.buffer

    def process_text(self, text: str, swiss_mode: bool = False) -> Dict[str, Any]:
        """
        Process German text through the 4 dedicated Sub-AIs and synchronize the 64-byte AMSV.
        """
        tokens = tokenize_words(text)
        sentences = split_sentences(text)
        
        # Zero-bridge pass to Sub-AIs sharing the exact same physical bytearray
        buf = self.amsv_buffer
        
        # Update token and sentence counts in buffer
        self.bridge.update_metrics(
            token_count=len(tokens),
            sentence_count=len(sentences),
            clause_type_mask=0x0001,
            satzklammer_flags=buf[18],
            case_error_flags=buf[19],
            orthography_flags=buf[20],
            adjective_decl_flags=buf[21],
            register_type=buf[22],
            modal_particle_count=buf[23],
            confidence=1.0
        )
        
        # Execute Sub-AIs
        syntax_res = self.syntax_sub_ai.process(text, buf)
        phon_res = self.phonology_sub_ai.process(text, buf, swiss_mode=swiss_mode)
        prag_res = self.pragmatic_sub_ai.process(text, buf)
        edit_res = self.editorial_sub_ai.process(text, buf)
        
        # Read final synchronized metrics directly from memory
        amsv_state = self.bridge.read_metrics()
        
        return {
            "text": text,
            "token_count": len(tokens),
            "sentence_count": len(sentences),
            "syntax": syntax_res,
            "phonology": phon_res,
            "pragmatics": prag_res,
            "editorial": edit_res,
            "amsv_state": amsv_state,
            "is_valid": syntax_res["is_valid"] and phon_res["is_valid"] and edit_res["is_valid"] and prag_res["register_consistent"]
        }

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive end-to-end grammar check."""
        return self.grammar_checker.check(text)

    def compose_email(self, form: str, recipient_name: str, body: str, sender_name: str, title: str = "Herr") -> str:
        """Compose formal or informal German email."""
        return self.email_pipeline.compose(form, recipient_name, body, sender_name, title)

    def audit_email(self, email_text: str) -> Dict[str, Any]:
        """Audit email etiquette and register consistency."""
        return self.email_pipeline.audit(email_text)

    def inflect_noun_phrase(self, determiner: Optional[str], adjective: Optional[str], noun: str, gender: str, case: str) -> str:
        """Inflect German noun phrase according to gender and case."""
        return generate_noun_phrase(determiner, adjective, noun, gender, case)

    def conjugate_verb(self, verb: str, pronoun: str) -> str:
        """Conjugate German verb in Präsens."""
        return conjugate_present(verb, pronoun)

    def adapt_to_swiss(self, text: str) -> str:
        """Convert standard German text to Swiss standard orthography (ß -> ss)."""
        return self.composition_pipeline.adapt_orthography(text, swiss_mode=True)
