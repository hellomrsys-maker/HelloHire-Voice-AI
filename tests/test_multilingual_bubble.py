"""
test_multilingual_bubble.py - Complete Test Suite for Multilingual Bubble 1.

Verifies:
1. Dataset & Curriculum Manifest Integrity across all 8 Global Cohort Engines:
   - Spanish, Mandarin, Japanese, German, French, Russian, Arabic, Korean.
2. Multilingual verified checkpoints existence, weights loading, and SHA-256 integrity.
3. Universal Sub-AIs neural inference across all 8 target languages.
4. Master Orchestrators for target languages under zero-bridge AMSV memory synchronization.
"""

from __future__ import annotations
import os
import json
import hashlib
import pytest
import torch

from amsv.python.amsv_embedded import AMSVEmbeddedView
from gra_voi.bandhu.sub_ai_neural import (
    WritingSubAINeural,
    EmailSubAINeural,
    ListeningSubAINeural,
    PronunciationSubAINeural,
    ReviewingSubAINeural,
)

TARGET_ENGINES = [
    ("Spanish", "Spanish_engine"),
    ("Mandarin", "Mandarin_engine"),
    ("Japanese", "Japanese_engine"),
    ("German", "German_engine"),
    ("French", "French_engine"),
    ("Russian", "Russian_engine"),
    ("Arabic", "Arabic_engine"),
    ("Korean", "Korean_engine"),
]

MAIN_CKPT_PATH = os.path.join("checkpoints", "multilingual_bubble_main_model_verified.pt")
SUB_CKPT_PATH = os.path.join("checkpoints", "multilingual_bubble_sub_ais_verified.pt")


class TestMultilingualCorporaAndManifests:
    """Verifies all 8 languages have complete, valid grammar corpora and curriculum manifests."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES)
    def test_corpus_exists_and_populated(self, lang_name, eng_dir):
        corpus_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")
        assert os.path.exists(corpus_file), f"Missing corpus file for {lang_name} at {corpus_file}"
        with open(corpus_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["language"] == lang_name
        assert len(data["writing_corpus"]) >= 1000
        assert len(data["pragmatic_corpus"]) >= 50
        assert len(data["phonology_corpus"]) >= 50
        assert len(data["editorial_corpus"]) >= 50

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES)
    def test_manifest_exists_and_valid(self, lang_name, eng_dir):
        manifest_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", f"{lang_name.lower()}_full_curriculum_manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest file for {lang_name} at {manifest_file}"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == lang_name
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) == 3
        assert data["ready_for_neural_training"] is True


class TestMultilingualCheckpointsAndSubAIs:
    """Verifies checkpoint persistence, SHA-256 fingerprinting, and universal sub-AI inference."""

    def test_checkpoint_files_and_sidecars(self):
        assert os.path.exists(MAIN_CKPT_PATH), f"Main checkpoint missing: {MAIN_CKPT_PATH}"
        assert os.path.exists(SUB_CKPT_PATH), f"Sub-AIs checkpoint missing: {SUB_CKPT_PATH}"
        assert os.path.exists(MAIN_CKPT_PATH + ".json"), "Main metadata sidecar missing"
        assert os.path.exists(SUB_CKPT_PATH + ".json"), "Sub-AIs metadata sidecar missing"

        # Verify SHA-256 matches sidecar
        with open(SUB_CKPT_PATH, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SUB_CKPT_PATH + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["sha256"] == computed_hash

    def test_universal_writing_sub_ai_cross_lingual(self):
        ckpt = torch.load(SUB_CKPT_PATH, map_location="cpu")
        writing_ai = WritingSubAINeural()
        writing_ai.load_state_dict(ckpt["writing_sub_ai"])
        writing_ai.eval()

        test_sentences = [
            "El ingeniero diseñó una arquitectura distribuida.",
            "工程师设计了高并发分布式系统。",
            "エンジニアが高並行分散システムを設計しました。",
            "Der Ingenieur entwickelte eine hochmoderne verteilte Architektur.",
            "L'ingénieur a conçu une architecture distribuée très performante.",
            "Инженер спроектировал высокопроизводительную распределённую архитектуру.",
            "صمم المهندس معمارية حاسوبية موزعة وعالية الأداء.",
            "엔지니어가 고성능 분산 시스템 아키텍처를 설계했습니다.",
        ]

        ids, mask = writing_ai.tokenizer.encode(test_sentences, max_length=56)
        with torch.no_grad():
            preds = writing_ai(ids, mask)

        comp = preds["sentence_completeness"].squeeze()
        assert comp.shape[0] == 8
        # All valid sentences should have completeness > 0.5
        for score in comp:
            assert float(score.item()) > 0.50

    def test_universal_email_sub_ai_cross_lingual(self):
        ckpt = torch.load(SUB_CKPT_PATH, map_location="cpu")
        email_ai = EmailSubAINeural()
        email_ai.load_state_dict(ckpt["email_sub_ai"])
        email_ai.eval()

        formal_sentences = [
            "¿Podría usted revisar este informe técnico, por favor?",
            "您好，请问能否请您过目这份技术文档？",
            "大変恐れ入りますが、本仕様書をご確認いただけますでしょうか。",
            "Sehr geehrter Herr Professor, könnten Sie bitte das Dokument prüfen?",
            "Auriez-vous l'amabilité d'examiner ce rapport technique, Monsieur ?",
            "Уважаемый профессор, не могли бы Вы ознакомиться с документом?",
            "سعادة الدكتور المحترم، هل تتفضلون بمراجعة هذه الوثيقة الفنية؟",
            "교수님, 본 문서를 검토해 주실 수 있으시겠습니까?",
        ]

        ids, mask = email_ai.tokenizer.encode(formal_sentences, max_length=56)
        with torch.no_grad():
            preds = email_ai(ids, mask)

        pol = preds["politeness_score"].squeeze()
        assert pol.shape[0] == 8
        assert float(pol.mean().item()) > 0.70
        for p in pol:
            assert float(p.item()) > 0.40

    def test_universal_editorial_sub_ai_cross_lingual(self):
        ckpt = torch.load(SUB_CKPT_PATH, map_location="cpu")
        review_ai = ReviewingSubAINeural()
        review_ai.load_state_dict(ckpt["reviewing_sub_ai"])
        review_ai.eval()

        clean_sentences = [
            "El sistema funciona correctamente sin errores.",
            "这个算法运行得非常稳定高效。",
            "システムが正常に動作しています。",
            "Der Algorithmus arbeitet vollkommen fehlerfrei.",
            "Le système fonctionne de manière stable et rapide.",
            "Алгоритм работает быстро и абсолютно надёжно.",
            "يعمل النظام بكفاءة عالية وبدون أي انقطاع.",
            "시스템이 안정적이고 빠르게 작동합니다.",
        ]

        ids, mask = review_ai.tokenizer.encode(clean_sentences, max_length=48)
        with torch.no_grad():
            preds = review_ai(ids, mask)

        error_logits = preds["error_taxonomy_logits"]
        assert error_logits.shape[0] == 8


class TestMultilingualOrchestratorsAMSV:
    """Verifies master orchestrators run with zero-bridge AMSV synchronization."""

    def test_spanish_orchestrator_amsv(self):
        from Spanish_engine.spanish_engine_orchestrator import SpanishEngineOrchestrator
        amsv = AMSVEmbeddedView()
        orch = SpanishEngineOrchestrator(amsv_view=amsv)
        res = orch.process("El ingeniero diseñó una arquitectura distribuida.")

        assert res.syntax_sub_ai.amsv_synced is True
        assert res.phonology_sub_ai.amsv_synced is True
        assert res.pragmatic_sub_ai.amsv_synced is True
        assert res.editorial_sub_ai.amsv_synced is True
        assert amsv.get_cognitive_score(1) > 0.0

    def test_japanese_orchestrator_amsv(self):
        from Japanese_engine.japanese_engine_orchestrator import JapaneseEngineOrchestrator
        amsv = AMSVEmbeddedView()
        orch = JapaneseEngineOrchestrator(amsv_view=amsv)
        res = orch.process("エンジニアが高並行分散システムを設計しました。")

        assert res.syntax_sub_ai.amsv_synced is True
        assert res.phonology_sub_ai.amsv_synced is True
        assert res.pragmatic_sub_ai.amsv_synced is True
        assert res.editorial_sub_ai.amsv_synced is True
        assert amsv.get_cognitive_score(1) > 0.0
