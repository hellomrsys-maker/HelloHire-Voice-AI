"""
Indonesian Engine — Master Orchestrator
Coordinates all 9 cognitive layers, 4 dedicated Sub-AIs, and task pipelines under
The Zero-Bridge Synchronous Memory Rule with 0-ns AMSV physical vector synchronization.
"""

from typing import Dict, Any, Optional
from .six_language_matrix.indonesian_matrix_bridge import (
    IndonesianMatrixBridge,
    INDONESIAN_AMSV_MAGIC,
    INDONESIAN_AMSV_SIZE
)
from .brain.skills.tokenization import tokenize_words, split_sentences
from .brain.sub_ais.syntax_sub_ai import IndonesianSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import IndonesianPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import IndonesianPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import IndonesianEditorialSubAI
from .brain.task.grammar_check import IndonesianGrammarChecker
from .brain.task.email_pipeline import IndonesianEmailPipeline
from .brain.task.composition_pipeline import IndonesianCompositionPipeline

class IndonesianEngineOrchestrator:
    """Master orchestrator for the Indonesian Computational Cognitive Language Engine."""

    def __init__(self, shared_amsv_buffer: Optional[bytearray] = None):
        self.bridge = IndonesianMatrixBridge(shared_amsv_buffer)
        self.amsv_buffer = self.bridge.buffer
        
        # Initialize Sub-AIs
        self.syntax_sub_ai = IndonesianSyntaxSubAI()
        self.phonology_sub_ai = IndonesianPhonologySubAI()
        self.pragmatic_sub_ai = IndonesianPragmaticSubAI()
        self.editorial_sub_ai = IndonesianEditorialSubAI()
        
        # Initialize Task Pipelines
        self.grammar_checker = IndonesianGrammarChecker()
        self.email_pipeline = IndonesianEmailPipeline()
        self.composition_pipeline = IndonesianCompositionPipeline()

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process Indonesian text through the complete cognitive pipeline,
        synchronously updating physical AMSV memory offsets.
        """
        tokens = tokenize_words(text)
        sentences = split_sentences(text)
        
        # 1. Syntax Sub-AI execution (AMSV byte 18 & 52)
        syn_res = self.syntax_sub_ai.process(text, self.amsv_buffer)
        
        # 2. Phonology Sub-AI execution (AMSV byte 20 & 53)
        phon_res = self.phonology_sub_ai.process(text, self.amsv_buffer)
        
        # 3. Pragmatic Sub-AI execution (AMSV bytes 22, 23 & 54)
        prag_res = self.pragmatic_sub_ai.process(text, self.amsv_buffer)
        
        # 4. Editorial Sub-AI execution (AMSV bytes 19, 21, 24..27 & 55)
        ed_res = self.editorial_sub_ai.process(text, self.amsv_buffer)
        
        # Update high-level token & sentence counters in AMSV
        self.bridge.update_metrics(
            token_count=len(tokens),
            sentence_count=len(sentences),
            syntax_flags=syn_res.get("flags", 0),
            morphology_flags=ed_res.get("flags", 0),
            phonology_flags=phon_res.get("flags", 0),
            register_tier=prag_res.get("register_tier", 0),
            pragmatic_flags=prag_res.get("flags", 0),
            confidence=ed_res.get("confidence", 1.0)
        )
        
        amsv_state = self.bridge.read_metrics()
        is_overall_valid = syn_res["is_valid"] and phon_res["is_valid"] and ed_res["is_valid"]
        
        return {
            "text": text,
            "token_count": len(tokens),
            "sentence_count": len(sentences),
            "is_valid": is_overall_valid,
            "syntax": syn_res,
            "phonology": phon_res,
            "pragmatics": prag_res,
            "editorial": ed_res,
            "amsv_state": amsv_state
        }

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """Audit text for voice affixation, nasal assimilation, and reduplication accuracy."""
        return self.grammar_checker.check(text)

    def compose_email(
        self,
        form: str = "formal",
        recipient_name: str = "Santoso",
        recipient_title: str = "Direktur Utama",
        body: str = "",
        sender_name: str = "Budi Wijaya",
        organization: Optional[str] = "Solo Rock"
    ) -> str:
        """Compose a structured formal or informal Indonesian email."""
        return self.email_pipeline.compose(
            form=form,
            recipient_name=recipient_name,
            recipient_title=recipient_title,
            body=body,
            sender_name=sender_name,
            organization=organization
        )

    def audit_email(self, email_text: str) -> Dict[str, Any]:
        """Audit register consistency in an Indonesian email."""
        return self.email_pipeline.audit(email_text)

    def compose_prose(self, topic: str, style: str = "standard_formal") -> str:
        """Synthesize prose in Indonesian."""
        return self.composition_pipeline.compose_prose(topic, style)

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analyze literary and rhetorical features in Indonesian prose."""
        return self.composition_pipeline.analyze_style(text)

    def adapt_dialect(self, text: str, target: str = "baku") -> str:
        """Adapt colloquial Jakartan slang (Bahasa Gaul) to standard Bahasa Baku."""
        return self.composition_pipeline.adapt_dialect(text, target)
