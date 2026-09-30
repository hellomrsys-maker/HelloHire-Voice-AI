"""
Polish Sovereign Language Engine Orchestrator — v2.0
====================================================
Upgraded to implement the full Four-Stage 6-Language Matrix Pattern:

  Stage 1: Reserved Entry Boundary (validation & contract)
  Stage 2: Base Matrix ↔ AI Model (skills + sub-AIs + AMSV writes)
  Stage 3: Connected Internal Groups (2×2 network with Hub + cyclic feedback)
  Stage 4: Verify, Learn, Analyze, Result (recursive quality verification)

New in v2.0:
  • AMSV Resonance Protocol: sub-AIs share buf sequentially, each reading
    the previous sub-AI's writes before computing its own scores.
  • Stage 3 Network: 2×2 topology (Group A: Syntax+Editorial | Group B: Phonology+Pragmatic)
    with Hub arbitration and cyclic refinement loop on conflict detection.
  • Stage 4 Verifier: recursive quality verification with feedback passes.
  • AMSV Hierarchical Namespace: engine result published to master AMSV
    Verbal Reasoning slot (0x1C-0x1D) via AMSVHierarchicalNamespace.
  • Prefix Semantic Engine: validates Polish verbal prefix usage and
    aspect-tense compatibility.
  • Open-Vocabulary Morpheme Generator: classifies unknown/loanword words
    via productive morphological patterns before POS fallback.

Zero-Bridge Synchronous Memory Rule:
  All state synchronization is direct in-place memory mutation of the
  64-byte bytearray (buf). No serialization. No deserialization.
"""

import time
import zlib
from typing import Dict, Any, Optional

from .brain.skills.tokenization import PolishTokenizer
from .brain.skills.pos_tagging import PolishPOSTagger
from .brain.skills.genitive_negation_engine import PolishGenitiveNegationEngine
from .brain.skills.aspect_engine import PolishAspectEngine
from .brain.skills.honorific_deixis_engine import PolishHonorificDeixisEngine
from .brain.skills.phonology_sibilant_engine import PolishPhonologySibilantEngine
from .brain.skills.generation import PolishGenerator
from .brain.skills.prefix_semantic_engine import PolishPrefixSemanticEngine
from .brain.skills.morpheme_generator import PolishOpenVocabClassifier

from .brain.sub_ais.syntax_sub_ai import PolishSyntaxSubAI
from .brain.sub_ais.phonology_sub_ai import PolishPhonologySubAI
from .brain.sub_ais.pragmatic_sub_ai import PolishPragmaticSubAI
from .brain.sub_ais.editorial_sub_ai import PolishEditorialSubAI

from .brain.stage3_network import Stage3Network
from .brain.stage4_verifier import Stage4Verifier

from .brain.task.grammar_check import PolishGrammarChecker
from .brain.task.email_pipeline import PolishEmailPipeline
from .brain.task.composition_pipeline import PolishCompositionPipeline

from .six_language_matrix.polish_matrix_bridge import (
    POLISH_AMSV_MAGIC,
    POLISH_ENGINE_ID,
    PolishMatrixMemoryBridge
)

from amsv.amsv_namespace import AMSVHierarchicalNamespace, COGNITIVE_PROFILES


class PolishEngineOrchestrator:
    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        # Memory Bridge (engine-private Tier 2 AMSV)
        self.bridge = PolishMatrixMemoryBridge()

        # Master AMSV reference (Tier 1 — may be None if standalone)
        self._master_buf = master_amsv_buffer
        self._ahn = None
        if self._master_buf is not None and len(self._master_buf) == 64:
            self._ahn = AMSVHierarchicalNamespace(self._master_buf)

        # ── Computational Skills ─────────────────────────────────────────────
        self.tokenizer        = PolishTokenizer()
        self.pos_tagger       = PolishPOSTagger()
        self.negation_engine  = PolishGenitiveNegationEngine()
        self.aspect_engine    = PolishAspectEngine()
        self.honorific_engine = PolishHonorificDeixisEngine()
        self.phonology_engine = PolishPhonologySibilantEngine()
        self.generator        = PolishGenerator()

        # ── NEW: Tier 8 — Prefix Semantic Engine ────────────────────────────
        self.prefix_engine = PolishPrefixSemanticEngine()

        # ── NEW: Tier 4 — Open-Vocabulary Classifier ────────────────────────
        self.open_vocab = PolishOpenVocabClassifier()

        # ── Dedicated Sub-AIs ────────────────────────────────────────────────
        self.syntax_sub_ai    = PolishSyntaxSubAI()
        self.phonology_sub_ai = PolishPhonologySubAI()
        self.pragmatic_sub_ai = PolishPragmaticSubAI()
        self.editorial_sub_ai = PolishEditorialSubAI()

        # ── NEW: Stage 3 Network (2×2 topology) ─────────────────────────────
        self.stage3 = Stage3Network(
            syntax_sub_ai=self.syntax_sub_ai,
            editorial_sub_ai=self.editorial_sub_ai,
            phonology_sub_ai=self.phonology_sub_ai,
            pragmatic_sub_ai=self.pragmatic_sub_ai,
        )

        # ── NEW: Stage 4 Verifier (recursive feedback) ──────────────────────
        self.stage4 = Stage4Verifier()

        # ── Task Pipelines ───────────────────────────────────────────────────
        self.grammar_checker      = PolishGrammarChecker()
        self.email_pipeline       = PolishEmailPipeline()
        self.composition_pipeline = PolishCompositionPipeline()

    def process(self, text: str) -> Dict[str, Any]:
        """
        Full Four-Stage zero-bridge cognitive linguistic pass.
        Executes Stage 1 → Stage 2 → Stage 3 → Stage 4 → AHN publish.
        """
        start_ns = time.perf_counter_ns()

        # ── Stage 1: Entry Boundary ──────────────────────────────────────────
        self.bridge.reset()
        buf = self.bridge.get_bytearray()

        tokens   = self.tokenizer.tokenize(text)
        token_count  = len(tokens)
        sentences    = self.tokenizer.split_sentences(text)
        clause_count = max(1, len(sentences))

        # Write token/clause counts directly to AMSV
        buf[8:12]  = token_count.to_bytes(4, byteorder="little")
        buf[12:16] = clause_count.to_bytes(4, byteorder="little")

        # ── NEW: Open-Vocab pre-scan — classify unknown tokens before Stage 2 ──
        open_vocab_hits = []
        for tok in tokens:
            low = tok.lower()
            if not any(c in "ąęóśźżćńł" for c in low) and len(low) > 4:
                result = self.open_vocab.classify(tok)
                if result.get("classification") != "UNKNOWN" and result.get("is_loanword"):
                    open_vocab_hits.append(result)

        # ── NEW: Prefix Semantic Analysis (runs before Stage 2 sub-AIs) ─────
        prefix_analysis = self.prefix_engine.analyze(text)

        # Write prefix semantic flag to AMSV (byte 0x3C: 1 if prefix violation, else 0)
        buf[0x3C] = 0 if prefix_analysis["prefix_semantics_ok"] else 1

        # ── Stage 2: Base Matrix ↔ Sub-AI Execution ─────────────────────────
        # Replaced flat linear execution with Stage 3 Network
        stage3_result = self.stage3.execute(text, buf)

        # ── Stage 3 complete — record latency so far ─────────────────────────
        elapsed_ns = time.perf_counter_ns() - start_ns
        buf[28:32] = elapsed_ns.to_bytes(4, byteorder="little")

        # ── Stage 4: Verify, Learn, Analyze, Result ──────────────────────────
        stage4_result = self.stage4.execute(stage3_result, buf, text)

        # ── Compute checksum over first 60 bytes (bytes 60-64 reserved for checksum) ──
        cksum = zlib.crc32(buf[0:60])
        buf[60:64] = cksum.to_bytes(4, byteorder="little")

        # ── Sync back to engine bridge ────────────────────────────────────────
        self.bridge.sync_from_bytes(buf)

        # ── Tier 9: AHN — Publish Engine Result to Master AMSV ──────────────
        if self._ahn is not None:
            aggregate_score = stage4_result["final_quality"] / 100.0
            self._ahn.publish_engine_result(
                engine_name="Polish",
                aggregate_linguistic_score=aggregate_score,
                cognitive_diff_byte=COGNITIVE_PROFILES["Polish"],
                resonance_conflict=stage3_result["hub"]["conflict_detected"]
            )

        final_elapsed_ns = time.perf_counter_ns() - start_ns

        return {
            "engine":   "Polish Sovereign Language Engine",
            "version":  "2.0.0",
            "text":     text,
            "tokens":   tokens,
            "token_count":  token_count,
            "clause_count": clause_count,
            "prefix_analysis": prefix_analysis,
            "open_vocab_loanwords": open_vocab_hits,
            "stage3": stage3_result,
            "stage4": stage4_result,
            "amsv_state": self.bridge.to_dict(),
            "master_amsv_published": self._ahn is not None,
            "latency_ns": final_elapsed_ns
        }

    def check_grammar(self, text: str) -> Dict[str, Any]:
        """
        Grammar check with prefix semantic validation integrated.
        """
        base_result = self.grammar_checker.check(text)
        prefix_result = self.prefix_engine.analyze(text)

        # Merge prefix violations into grammar check warnings
        all_errors = list(base_result.get("errors", []))
        for misuse in prefix_result["prefix_misuse_flags"]:
            all_errors.append({"type": "PREFIX_MISUSE", "message": misuse})
        for violation in prefix_result["aspect_tense_violations"]:
            all_errors.append({"type": "ASPECT_TENSE", "message": violation})

        return {
            **base_result,
            "errors": all_errors,
            "prefix_analysis": prefix_result,
            "prefix_semantics_integrated": True
        }

    def generate_email(self, surname: str, gender: str, purpose: str, register: str = "formal") -> Dict[str, Any]:
        return self.email_pipeline.generate(surname, gender, purpose, register)

    def compose_aspectual_contrast(self, subject: str, verb_impf: str, noun_lemma: str) -> Dict[str, str]:
        return self.composition_pipeline.compose_aspectual_contrast(subject, verb_impf, noun_lemma)

    def get_aspect_pair(self, verb: str) -> Optional[Dict[str, str]]:
        return self.aspect_engine.get_aspect_pair(verb)

    def get_prefix_frame(self, verb_or_prefix: str) -> Optional[Dict[str, Any]]:
        """Returns the semantic frame for a prefixed verb or raw prefix string."""
        frame = self.prefix_engine.get_semantic_frame(verb_or_prefix)
        if frame is None:
            frame = self.prefix_engine.explain_prefix(verb_or_prefix)
        return frame

    def classify_unknown_word(self, word: str) -> Dict[str, Any]:
        """Classifies an unknown or loanword using the open-vocabulary morpheme generator."""
        return self.open_vocab.classify(word)

    def generate_clause(self, subject: Optional[str], verb: str, noun_lemma: str, negate: bool = False) -> str:
        return self.generator.generate_clause(subject, verb, noun_lemma, negate)

    def get_memory_state(self) -> Dict[str, Any]:
        return self.bridge.to_dict()
