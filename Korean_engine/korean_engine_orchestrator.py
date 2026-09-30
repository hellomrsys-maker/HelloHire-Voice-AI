"""
Korean Engine — Master Orchestrator
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
task pipelines, and Zero-Bridge 64-byte AMSV physical synchronization.
"""

from typing import Dict, Any, Optional
from .six_language_matrix.korean_matrix_bridge import KoreanMatrixBridge, KOREAN_AMSV_SIZE
from .brain.skills.tokenization import split_sentences, tokenize_eojeol
from .brain.skills.pos_tagging import tag_pos
from .brain.skills.particle_engine import attach_particle
from .brain.skills.verb_conjugator import conjugate_verb
from .brain.skills.generation import generate_clause
from .brain.sub_ais.syntax_sub_ai import KoreanSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import KoreanPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import KoreanPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import KoreanEditorialSubAI
from .brain.task.grammar_check import KoreanGrammarChecker
from .brain.task.email_pipeline import KoreanEmailPipeline
from .brain.task.composition_pipeline import KoreanCompositionPipeline

class KoreanEngineOrchestrator:
    """
    Master Orchestrator for the Korean Cognitive Language Engine.
    Operates with zero-bridge synchronous memory synchronization on a 64-byte physical AMSV.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.bridge = KoreanMatrixBridge(memory_buffer)
        self.syntax_sub_ai = KoreanSyntaxSubAI()
        self.phonology_sub_ai = KoreanPhonologySubAI()
        self.pragmatic_sub_ai = KoreanPragmaticSubAI()
        self.editorial_sub_ai = KoreanEditorialSubAI()
        self.grammar_checker = KoreanGrammarChecker()
        self.email_pipeline = KoreanEmailPipeline()
        self.composition_pipeline = KoreanCompositionPipeline()

    @property
    def amsv_buffer(self) -> bytearray:
        return self.bridge.buffer

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process Korean text through the 4 dedicated Sub-AIs and synchronize the 64-byte AMSV.
        """
        tokens = tokenize_eojeol(text)
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        buf = self.amsv_buffer
        
        # Initial token update
        self.bridge.update_metrics(
            token_count=len(tokens),
            sentence_count=len(sentences),
            clause_type_mask=0x0001,
            syntax_flags=buf[18],
            particle_error_flags=buf[19],
            phonology_flags=buf[20],
            irregular_verb_flags=buf[21],
            speech_level_code=buf[22],
            honorific_concord_flags=buf[23],
            confidence=1.0
        )
        
        # Execute Sub-AIs with physical buffer synchronization
        syntax_res = self.syntax_sub_ai.process(text, buf)
        phon_res = self.phonology_sub_ai.process(text, buf)
        prag_res = self.pragmatic_sub_ai.process(text, buf)
        edit_res = self.editorial_sub_ai.process(text, buf)
        
        amsv_state = self.bridge.read_metrics()
        
        is_valid = (
            syntax_res["is_valid"] and
            phon_res["is_valid"] and
            prag_res["is_valid"] and
            edit_res["is_valid"]
        )
        
        return {
            "text": text,
            "token_count": len(tokens),
            "sentence_count": len(sentences),
            "syntax": syntax_res,
            "phonology": phon_res,
            "pragmatics": prag_res,
            "editorial": edit_res,
            "amsv_state": amsv_state,
            "is_valid": is_valid
        }

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive end-to-end Korean grammar check."""
        return self.grammar_checker.check(text)

    def compose_email(
        self,
        form: str,
        recipient_name: str,
        body: str,
        sender_name: str,
        recipient_title: str = "팀장",
        company_name: str = "솔로락"
    ) -> str:
        """Compose business or polite Korean email."""
        return self.email_pipeline.compose(form, recipient_name, body, sender_name, recipient_title, company_name)

    def audit_email(self, email_text: str) -> Dict[str, Any]:
        """Audit email etiquette and politeness consistency."""
        return self.email_pipeline.audit(email_text)

    def conjugate_verb(self, verb: str, speech_level: str = "haeyo", honorific: bool = False, tense: str = "present") -> str:
        """Conjugate Korean verb across speech levels and tenses."""
        return conjugate_verb(verb, speech_level=speech_level, honorific=honorific, tense=tense)

    def attach_particle(self, noun: str, particle_type: str, honorific: bool = False) -> str:
        """Attach phonologically appropriate particle allomorph."""
        return attach_particle(noun, particle_type, honorific=honorific)

    def generate_clause(
        self,
        subject: str,
        object_noun: Optional[str],
        verb_infinitive: str,
        speech_level: str = "haeyo",
        honorific: bool = False,
        use_topic: bool = False
    ) -> str:
        """Synthesize SOV clause."""
        return generate_clause(subject, object_noun, verb_infinitive, speech_level, honorific, use_topic)

    def adapt_orthography(self, text: str, target_standard: str = "south") -> str:
        """Adapt text between South and North Korean orthography (두음법칙)."""
        return self.composition_pipeline.adapt_orthography(text, target_standard=target_standard)
