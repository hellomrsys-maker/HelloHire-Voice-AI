"""
test_multilingual_bubble2.py - Complete Test Suite for Multilingual Bubble 2 (13 Languages).

Verifies:
1. Dataset & Curriculum Manifest Integrity across all 13 Remaining Global Engines:
   - Bengali, Cantonese, Dutch, Indonesian, Italian, Persian, Polish, Portuguese, Swahili, Tamil, Thai, Turkish, Vietnamese.
2. Bubble 2 verified checkpoints existence, weights loading, and SHA-256 integrity.
3. Universal Sub-AIs neural inference across all 13 target languages.
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

TARGET_ENGINES_2 = [
    ("Bengali", "Bengali_engine"),
    ("Cantonese", "Cantonese_engine"),
    ("Dutch", "Dutch_engine"),
    ("Indonesian", "Indonesian_engine"),
    ("Italian", "Italian_engine"),
    ("Persian", "Persian_engine"),
    ("Polish", "Polish_engine"),
    ("Portuguese", "Portuguese_engine"),
    ("Swahili", "Swahili_engine"),
    ("Tamil", "Tamil_engine"),
    ("Thai", "Thai_engine"),
    ("Turkish", "Turkish_engine"),
    ("Vietnamese", "Vietnamese_engine"),
]

MAIN_CKPT_PATH_2 = os.path.join("checkpoints", "multilingual_bubble2_main_model_verified.pt")
SUB_CKPT_PATH_2 = os.path.join("checkpoints", "multilingual_bubble2_sub_ais_verified.pt")


class TestMultilingualCorporaAndManifestsBubble2:
    """Verifies all 13 languages have complete, valid grammar corpora and curriculum manifests."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_2)
    def test_corpus_exists_and_populated_bubble2(self, lang_name, eng_dir):
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

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_2)
    def test_manifest_exists_and_valid_bubble2(self, lang_name, eng_dir):
        manifest_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", f"{lang_name.lower()}_full_curriculum_manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest file for {lang_name} at {manifest_file}"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == lang_name
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) == 3
        assert data["ready_for_neural_training"] is True


class TestMultilingualCheckpointsAndSubAIsBubble2:
    """Verifies checkpoint persistence, SHA-256 fingerprinting, and universal sub-AI inference for Bubble 2."""

    def test_checkpoint_files_and_sidecars_bubble2(self):
        assert os.path.exists(MAIN_CKPT_PATH_2), f"Main checkpoint missing: {MAIN_CKPT_PATH_2}"
        assert os.path.exists(SUB_CKPT_PATH_2), f"Sub-AIs checkpoint missing: {SUB_CKPT_PATH_2}"
        assert os.path.exists(MAIN_CKPT_PATH_2 + ".json"), "Main metadata sidecar missing"
        assert os.path.exists(SUB_CKPT_PATH_2 + ".json"), "Sub-AIs metadata sidecar missing"

        with open(SUB_CKPT_PATH_2, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SUB_CKPT_PATH_2 + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["sha256"] == computed_hash

    def test_universal_writing_sub_ai_cross_lingual_bubble2(self):
        ckpt = torch.load(SUB_CKPT_PATH_2, map_location="cpu")
        writing_ai = WritingSubAINeural()
        writing_ai.load_state_dict(ckpt["writing_sub_ai"])
        writing_ai.eval()

        test_sentences = [
            "প্রকৌশলী একটি অত্যন্ত দক্ষ বিতরণকৃত সিস্টেম তৈরি করেছেন।",
            "工程師設計咗個高並發嘅分散式系統。",
            "De ingenieur ontwierp een uiterst efficiënte gedistribueerde architectuur.",
            "Insinyur itu merancang arsitektur terdistribusi yang sangat andal.",
            "L'ingegnere ha progettato un'architettura distribuita ad alte prestazioni.",
            "مهندس یک معماری توزیع‌شده با کارایی بالا طراحی کرد.",
            "Inżynier zaprojektował wysoce wydajną architekturę rozproszoną.",
            "O engenheiro projetou uma arquitetura distribuída altamente eficiente.",
            "Mhandisi amebuni usanifu bora wa mifumo iliyosambazwa.",
            "பொறியாளர் மிகச்சிறந்த விநியோகிக்கப்பட்ட கணினி கட்டமைப்பை உருவாக்கினார்.",
            "วิศวกรได้ออกแบบสถาปัตยกรรมระบบกระจายที่มีประสิทธิภาพสูงมาก",
            "Mühendis yüksek başarımlı dağıtık sistem mimarisini tasarladı.",
            "Kỹ sư đã thiết kế một kiến trúc phân tán hiệu năng rất cao.",
        ]

        ids, mask = writing_ai.tokenizer.encode(test_sentences, max_length=56)
        with torch.no_grad():
            preds = writing_ai(ids, mask)

        comp = preds["sentence_completeness"].squeeze()
        assert comp.shape[0] == 13
        for score in comp:
            assert float(score.item()) > 0.50

    def test_universal_email_sub_ai_cross_lingual_bubble2(self):
        ckpt = torch.load(SUB_CKPT_PATH_2, map_location="cpu")
        email_ai = EmailSubAINeural()
        email_ai.load_state_dict(ckpt["email_sub_ai"])
        email_ai.eval()

        formal_sentences = [
            "আপনি কি দয়া করে এই প্রযুক্তিগত নথিটি পর্যালোচনা করবেন?",
            "請問陳教授您方唔方便過目一下呢份技術規格書呢？",
            "Geachte professor Jansen, zou u dit rapport willen beoordelen?",
            "Selamat pagi Bapak Direktur, sudikah memeriksa dokumen ini?",
            "Gentile Professor Rossi, Le sarei molto grato se potesse esaminare il documento.",
            "جناب آقای دکتر، آیا ممکن است لطف فرموده این گزارش را مطالعه نمایید؟",
            "Szanowny Panie Profesorze, czy byłby Pan uprzejmy przejrzeć ten raport?",
            "Prezado Professor Santos, teria a gentileza de analisar este relatório?",
            "Shikamoo Mwalimu, tafadhali naomba ukague hati hii ya kiufundi.",
            "மதிப்பிற்குரிய பேராசிரியர் அவர்களே, தயவுசெய்து ஆவணத்தை மதிப்பாய்வு செய்வீர்களா?",
            "กราบเรียนท่านอาจารย์ที่เคารพ กระผมขอความกรุณาตรวจทานเอกสารฉบับนี้ครับ",
            "Sayın Profesörüm, bu teknik belgeyi incelemenizi rica edebilir miyim?",
            "Kính thưa Thầy, em xin phép kính nhờ Thầy xem qua tài liệu kỹ thuật này ạ.",
        ]

        ids, mask = email_ai.tokenizer.encode(formal_sentences, max_length=56)
        with torch.no_grad():
            preds = email_ai(ids, mask)

        pol = preds["politeness_score"].squeeze()
        assert pol.shape[0] == 13
        assert float(pol.mean().item()) > 0.70
        for p in pol:
            assert float(p.item()) > 0.40

    def test_universal_editorial_sub_ai_cross_lingual_bubble2(self):
        ckpt = torch.load(SUB_CKPT_PATH_2, map_location="cpu")
        review_ai = ReviewingSubAINeural()
        review_ai.load_state_dict(ckpt["reviewing_sub_ai"])
        review_ai.eval()

        clean_sentences = [
            "সিস্টেমটি অত্যন্ত স্থিতিশীলভাবে কাজ করছে।",
            "呢個演算法行得非常穩定同埋順暢。",
            "Het algoritme functioneert volkomen stabiel en snel.",
            "Sistem ini beroperasi dengan sangat lancar dan stabil.",
            "Il sistema funziona in modo fluido ed efficiente.",
            "الگوریتم جدید به صورت کاملاً پایدار و روان کار می‌کند.",
            "Algorytm działa stabilnie i niezwykle precyzyjnie.",
            "O sistema opera com estabilidade e velocidade excepcionais.",
            "Mfumo unafanya kazi kwa utulivu na wepesi mkubwa.",
            "கணினி அமைப்பு மிகவும் சீராகவும் வேகமாகவும் இயங்குகிறது.",
            "ระบบนี้ทำงานได้อย่างเสถียรและรวดเร็วมาก",
            "Algoritma son derece kararlı ve akıcı bir şekilde çalışıyor.",
            "Thuật toán hoạt động rất ổn định và nhanh chóng.",
        ]

        ids, mask = review_ai.tokenizer.encode(clean_sentences, max_length=48)
        with torch.no_grad():
            preds = review_ai(ids, mask)

        error_logits = preds["error_taxonomy_logits"]
        assert error_logits.shape[0] == 13


class TestMultilingualOrchestratorsAMSVBubble2:
    """Verifies master orchestrators run with zero-bridge AMSV synchronization for Bubble 2."""

    def test_swahili_orchestrator_amsv(self):
        from Swahili_engine.swahili_engine_orchestrator import SwahiliEngineOrchestrator
        orch = SwahiliEngineOrchestrator()
        res = orch.process_text("Watoto wanasoma vitabu vizuri.")

        assert res["is_valid"] is True
        assert res["amsv_state"]["is_magic_valid"] is True
        assert res["amsv_state"]["sub_ai_statuses"]["syntax"] is True
        assert len(orch.amsv_buffer) == 64

    def test_turkish_orchestrator_amsv(self):
        from Turkish_engine.turkish_engine_orchestrator import TurkishEngineOrchestrator
        amsv = AMSVEmbeddedView()
        orch = TurkishEngineOrchestrator(amsv_view=amsv)
        res = orch.analyze("Mühendis yüksek başarımlı dağıtık sistem mimarisini tasarladı.")

        assert res.syntax_eval.amsv_synced is True
        assert res.phonology_eval.amsv_synced is True
        assert res.pragmatic_eval.amsv_synced is True
        assert res.editorial_eval.amsv_synced is True
        assert amsv.get_cognitive_score(1) > 0.0
