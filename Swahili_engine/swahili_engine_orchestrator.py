"""
Swahili Engine — Master Orchestrator
Coordinates the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
task pipelines, and Zero-Bridge 64-byte AMSV physical synchronization.
"""

from typing import Dict, Any, Optional
from .six_language_matrix.swahili_matrix_bridge import SwahiliMatrixBridge, SWAHILI_AMSV_SIZE
from .brain.skills.tokenization import split_sentences, tokenize_words
from .brain.skills.pos_tagging import tag_pos
from .brain.skills.noun_class_engine import identify_noun_class
from .brain.skills.concord_engine import generate_concordial_np
from .brain.skills.verbal_template_engine import synthesize_verb
from .brain.skills.verbal_extensions_engine import derive_extension
from .brain.skills.generation import generate_svo_clause
from .brain.sub_ais.syntax_sub_ai import SwahiliSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import SwahiliPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import SwahiliPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import SwahiliEditorialSubAI
from .brain.task.grammar_check import SwahiliGrammarChecker
from .brain.task.email_pipeline import SwahiliEmailPipeline
from .brain.task.composition_pipeline import SwahiliCompositionPipeline

class SwahiliEngineOrchestrator:
    """
    Master Orchestrator for the Swahili Cognitive Language Engine.
    Operates with zero-bridge synchronous memory synchronization on a 64-byte physical AMSV.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        self.bridge = SwahiliMatrixBridge(memory_buffer)
        self.syntax_sub_ai = SwahiliSyntaxSubAI()
        self.phonology_sub_ai = SwahiliPhonologySubAI()
        self.pragmatic_sub_ai = SwahiliPragmaticSubAI()
        self.editorial_sub_ai = SwahiliEditorialSubAI()
        self.grammar_checker = SwahiliGrammarChecker()
        self.email_pipeline = SwahiliEmailPipeline()
        self.composition_pipeline = SwahiliCompositionPipeline()

    @property
    def amsv_buffer(self) -> bytearray:
        return self.bridge.buffer

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process Swahili text through the 4 dedicated Sub-AIs and synchronize the 64-byte AMSV.
        """
        tokens = tokenize_words(text)
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
            concord_error_flags=buf[19],
            phonology_flags=buf[20],
            verbal_extension_flags=buf[21],
            noun_class_head=buf[22],
            pragmatic_flags=buf[23],
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
        """Perform comprehensive end-to-end Swahili grammar check."""
        return self.grammar_checker.check(text)

    def compose_email(
        self,
        form: str,
        recipient_name: str,
        body: str,
        sender_name: str,
        recipient_title: str = "Mkurugenzi",
        organization: str = "Solo Rock"
    ) -> str:
        """Compose formal or polite everyday Swahili email."""
        return self.email_pipeline.compose(form, recipient_name, body, sender_name, recipient_title, organization)

    def audit_email(self, email_text: str) -> Dict[str, Any]:
        """Audit email etiquette, greetings, and closing consistency."""
        return self.email_pipeline.audit(email_text)

    def synthesize_verb(
        self,
        subject: str,
        root: str,
        tense: str = "present",
        object_marker: Optional[str] = None,
        negative: bool = False
    ) -> str:
        """Synthesize 8-slot Swahili finite verb form."""
        return synthesize_verb(subject=subject, root=root, tense=tense, object_marker=object_marker, negative=negative)

    def derive_extension(self, verb_infinitive: str, extension_type: str) -> str:
        """Derive extended verb form adhering to Bantu vowel harmony."""
        return derive_extension(verb_infinitive, extension_type)

    def generate_svo_clause(
        self,
        subject_noun: str,
        verb_root: str,
        object_noun: Optional[str] = None,
        tense: str = "present",
        include_object_prefix: bool = False
    ) -> str:
        """Generate canonical Swahili SVO clause with verified concordial agreement."""
        return generate_svo_clause(subject_noun, verb_root, object_noun, tense, include_object_prefix)

    def generate_concordial_np(
        self,
        noun: str,
        poss_stem: Optional[str] = None,
        dem_type: Optional[str] = None,
        adj_stem: Optional[str] = None
    ) -> str:
        """Generate agreement-governed Swahili noun phrase."""
        return generate_concordial_np(noun, poss_stem=poss_stem, dem_type=dem_type, adj_stem=adj_stem)

    def adapt_dialect(self, text: str, target: str = "standard") -> str:
        """Adapt between Sheng youth slang and Standard Kiunguja Swahili."""
        return self.composition_pipeline.adapt_dialect(text, target=target)

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary style, proverb density, idioms, and reduplication."""
        return self.composition_pipeline.analyze_style(text)
