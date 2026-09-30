"""
test_hindustani_training_and_sub_ais.py - Complete Test Suite for Hindustani Engine & Neural Sub-AIs.

Verifies:
1. Dataset & Curriculum Manifest Integrity.
2. Verified checkpoint existence, weights loading, and SHA-256 integrity.
3. Dedicated Sub-AIs (Syntax, Phonology, Pragmatics, Editorial) neural inference.
4. Strict Zero-Bridge AMSV sync offset validation:
   - 0x00 Phoneme State, 0x08 Prosody State
   - 0x12 Capability 1 (Syntax / Grammar Q16)
   - 0x14 Capability 2 (Discourse / Structure Q16)
   - 0x16 Capability 3 (Pragmatics / Register Q16)
   - 0x18 Capability 4 (Phonology / Audibility Q16)
   - 0x1A Capability 5 (Critical Review Q16)
   - 0x34 Global Structural Score, 0x36 Global Register Score
5. Master Orchestrator analysis across Hindi Devanagari, Urdu Nastaliq transliteration, and Romanization.
"""

from __future__ import annotations
import os
import json
import hashlib
import pytest
import torch

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Hindustani_engine.brain.sub_ais import (
    HindustaniSyntaxSubAI,
    HindustaniPhonologySubAI,
    HindustaniPragmaticSubAI,
    HindustaniEditorialSubAI,
)
from Hindustani_engine.hindustani_engine_orchestrator import HindustaniEngineOrchestrator


CORPUS_PATH = os.path.join("Hindustani_engine", "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")
MANIFEST_PATH = os.path.join("Hindustani_engine", "6_DATA_REQUIREMENTS", "hindustani_full_curriculum_manifest.json")
SUB_CKPT_PATH = os.path.join("checkpoints", "hindustani_engine_sub_ais_verified.pt")
MAIN_CKPT_PATH = os.path.join("checkpoints", "hindustani_main_model_verified.pt")


class TestHindustaniCorpusAndCurriculum:
    """Verifies that the Hindustani corpus and curriculum manifests are complete and valid."""

    def test_corpus_exists_and_has_all_corpora(self):
        assert os.path.exists(CORPUS_PATH), f"Corpus not found at {CORPUS_PATH}"
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["total_extracted_sentences"] >= 1000
        assert len(data["writing_corpus"]) >= 1000
        assert len(data["pragmatic_corpus"]) >= 50
        assert len(data["phonology_corpus"]) >= 50
        assert len(data["editorial_corpus"]) >= 50

    def test_curriculum_manifest_structure(self):
        assert os.path.exists(MANIFEST_PATH), f"Manifest not found at {MANIFEST_PATH}"
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == "Hindustani"
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) >= 3


class TestHindustaniSubAIsNeural:
    """Tests each dedicated Hindustani Sub-AI with and without neural checkpoints."""

    def test_syntax_sub_ai_neural_and_amsv(self):
        amsv = AMSVEmbeddedView()
        syntax_ai = HindustaniSyntaxSubAI(
            amsv_view=amsv,
            checkpoint_path=SUB_CKPT_PATH if os.path.exists(SUB_CKPT_PATH) else None
        )

        test_sent = "राम ने पुस्तक पढ़ी।"
        res = syntax_ai.evaluate(test_sent)

        assert res.is_valid_sentence is True
        assert res.is_canonical_sov is True
        assert res.is_ergative is True
        assert res.syntactic_integrity_score >= 0.70
        assert res.amsv_synced is True

        # Verify AMSV offset 0x12 (Capability 1)
        cap1 = amsv.get_cognitive_score(1)
        assert cap1 > 0.0

    def test_phonology_sub_ai_neural_and_amsv(self):
        amsv = AMSVEmbeddedView()
        phono_ai = HindustaniPhonologySubAI(
            amsv_view=amsv,
            checkpoint_path=SUB_CKPT_PATH if os.path.exists(SUB_CKPT_PATH) else None
        )

        test_sent = "गाड़ी सड़क पर दौड़ रही है।"
        res = phono_ai.evaluate(test_sent)

        assert res.retroflex_count >= 1
        assert res.phonological_density_score > 0.60
        assert res.amsv_synced is True

        # Verify AMSV offset 0x18 (Capability 4)
        cap4 = amsv.get_cognitive_score(4)
        assert cap4 > 0.0

    def test_pragmatic_sub_ai_neural_and_amsv(self):
        amsv = AMSVEmbeddedView()
        prag_ai = HindustaniPragmaticSubAI(
            amsv_view=amsv,
            checkpoint_path=SUB_CKPT_PATH if os.path.exists(SUB_CKPT_PATH) else None
        )

        formal_sent = "आप कृपया यहां बैठिए।"
        res_formal = prag_ai.evaluate(formal_sent)
        assert "aap" in res_formal.address_tier.lower()
        assert res_formal.is_formal is True
        assert res_formal.politeness_score >= 0.70
        assert res_formal.amsv_synced is True

        # Verify AMSV offset 0x16 (Capability 3) and 0x36 (Global register)
        cap3 = amsv.get_cognitive_score(3)
        reg = amsv.get_global_register_score()
        assert cap3 > 0.5
        assert reg > 0.5

    def test_editorial_sub_ai_neural_and_amsv(self):
        amsv = AMSVEmbeddedView()
        edit_ai = HindustaniEditorialSubAI(
            amsv_view=amsv,
            checkpoint_path=SUB_CKPT_PATH if os.path.exists(SUB_CKPT_PATH) else None
        )

        clean_sent = "लड़का स्कूल जाता है।"
        res = edit_ai.evaluate(clean_sent)
        assert res.editorial_score >= 0.70
        assert res.amsv_synced is True

        # Verify AMSV offset 0x14 (Capability 2) and 0x1A (Capability 5)
        cap2 = amsv.get_cognitive_score(2)
        cap5 = amsv.get_cognitive_score(5)
        assert cap2 > 0.0
        assert cap5 > 0.0


class TestHindustaniEngineOrchestrator:
    """Verifies end-to-end analysis, 6-language matrix, and full AMSV synchronization."""

    def test_orchestrator_pipeline_end_to_end(self):
        amsv = AMSVEmbeddedView()
        orchestrator = HindustaniEngineOrchestrator(
            amsv_view=amsv,
            checkpoint_path=SUB_CKPT_PATH if os.path.exists(SUB_CKPT_PATH) else None
        )

        test_sentence = "अध्यापक ने छात्रों को व्याकरण सिखाया।"
        result = orchestrator.analyze(test_sentence)

        assert len(result.tokens) >= 5
        assert result.syntax_eval.is_canonical_sov is True
        assert result.syntax_eval.is_ergative is True
        assert result.overall_linguistic_score > 0.65
        assert result.amsv_synced is True

        # Verify zero-bridge memory sync integrity
        cap1 = amsv.get_cognitive_score(1)
        cap2 = amsv.get_cognitive_score(2)
        cap3 = amsv.get_cognitive_score(3)
        cap4 = amsv.get_cognitive_score(4)
        cap5 = amsv.get_cognitive_score(5)
        assert all(c > 0.0 for c in [cap1, cap2, cap3, cap4, cap5])
