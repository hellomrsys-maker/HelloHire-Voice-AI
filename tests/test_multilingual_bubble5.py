"""
test_multilingual_bubble5.py - Complete Test Suite for Multilingual Bubble 5 (8 Languages).

Verifies:
1. Dataset & Curriculum Manifest Integrity across all 8 Global Expansion Engines:
   - Hebrew, Burmese, Amharic, Yoruba, Malay, Odia, Finnish, Danish.
2. Bubble 5 verified checkpoints existence, weights loading, and SHA-256 integrity.
3. Universal Sub-AIs neural inference across all 8 target languages.
4. Master Orchestrators for target languages under zero-bridge AMSV memory synchronization.
"""

from __future__ import annotations
import os
import sys
import json
import hashlib
import importlib
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

TARGET_ENGINES_5 = [
    ("Hebrew", "Hebrew_engine"),
    ("Burmese", "Burmese_engine"),
    ("Amharic", "Amharic_engine"),
    ("Yoruba", "Yoruba_engine"),
    ("Malay", "Malay_engine"),
    ("Odia", "Odia_engine"),
    ("Finnish", "Finnish_engine"),
    ("Danish", "Danish_engine"),
]

MAIN_CKPT_PATH_5 = os.path.join("checkpoints", "multilingual_bubble5_main_model_verified.pt")
SUB_CKPT_PATH_5 = os.path.join("checkpoints", "multilingual_bubble5_sub_ais_verified.pt")


class TestMultilingualCorporaAndManifestsBubble5:
    """Verifies all 8 languages have complete, valid grammar corpora and curriculum manifests."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_5)
    def test_corpus_exists_and_populated_bubble5(self, lang_name, eng_dir):
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

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_5)
    def test_manifest_exists_and_valid_bubble5(self, lang_name, eng_dir):
        manifest_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", f"{lang_name.lower()}_full_curriculum_manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest file for {lang_name} at {manifest_file}"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == lang_name
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) == 3
        assert data["ready_for_neural_training"] is True


class TestMultilingualCheckpointsAndSubAIsBubble5:
    """Verifies checkpoint persistence, SHA-256 fingerprinting, and universal sub-AI inference for Bubble 5."""

    def test_checkpoint_files_and_sidecars_bubble5(self):
        assert os.path.exists(MAIN_CKPT_PATH_5), f"Main checkpoint missing: {MAIN_CKPT_PATH_5}"
        assert os.path.exists(SUB_CKPT_PATH_5), f"Sub-AIs checkpoint missing: {SUB_CKPT_PATH_5}"
        assert os.path.exists(MAIN_CKPT_PATH_5 + ".json"), "Main metadata sidecar missing"
        assert os.path.exists(SUB_CKPT_PATH_5 + ".json"), "Sub-AIs metadata sidecar missing"

        with open(SUB_CKPT_PATH_5, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SUB_CKPT_PATH_5 + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["sha256"] == computed_hash

    def test_universal_writing_sub_ai_cross_lingual_bubble5(self):
        ckpt = torch.load(SUB_CKPT_PATH_5, map_location="cpu")
        writing_ai = WritingSubAINeural()
        writing_ai.load_state_dict(ckpt["writing_sub_ai"])
        writing_ai.eval()

        test_sentences = [
            "המהנדס תכנן מערכת מבוזרת יעילה ביותר.",
            "အင်ဂျင်နီယာသည် အလွန်ထိရောက်သော ဖြန့်ဝေစနစ်ကို တည်ဆောက်ခဲ့သည်။",
            "መሐንዲሱ በጣም ቀልጣፋ የሆነ የተከፋፈለ ሥርዓት ሠራ።",
            "Onimọ-ẹrọ kọ eto pinpin ti o munadoko pupọ.",
            "Jurutera itu mereka bentuk sistem teragih yang sangat cekap.",
            "ଇଞ୍ଜିନିୟର ଏକ ଅତ୍ୟନ୍ତ ଦକ୍ଷ ବିତରିତ ପ୍ରଣାଳୀ ବିକଶିତ କରିଛନ୍ତି।",
            "Insinööri suunnitteli erittäin tehokkaan hajautetun järjestelmän.",
            "Ingeniøren designede et yderst effektivt distribueret system.",
        ]

        ids, mask = writing_ai.tokenizer.encode(test_sentences, max_length=56)
        with torch.no_grad():
            preds = writing_ai(ids, mask)

        comp = preds["sentence_completeness"].squeeze()
        assert comp.shape[0] == 8
        for score in comp:
            assert float(score.item()) > 0.50

    def test_universal_email_sub_ai_cross_lingual_bubble5(self):
        ckpt = torch.load(SUB_CKPT_PATH_5, map_location="cpu")
        email_ai = EmailSubAINeural()
        email_ai.load_state_dict(ckpt["email_sub_ai"])
        email_ai.eval()

        formal_sentences = [
            "האם תוכל בבקשה לעיין במסמך טכני זה?",
            "ဤနည်းပညာဆိုင်ရာ စာရွက်စာတမ်းကို ကျေးဇူးပြု၍ စစ်ဆေးပေးနိုင်ပါသလား ခင်ဗျာ။",
            "እባክዎ ይህንን የቴክኒክ ሰነድ ሊገመግሙት ይችላሉ?",
            "Ẹ jọ̀wọ́, ṣé ẹ le ṣe àtúnyẹ̀wò ìwé ẹ̀rọ yìí fún mi?",
            "Sudikah Tuan/Puan menyemak dokumen teknikal ini dengan teliti?",
            "ଆପଣ କଣ ଦୟାକରି ଏହି ବୈଷୟିକ ଦସ୍ତାବିଜ ସମୀକ୍ଷା କରିବେ କି?",
            "Voisitteko ystävällisesti tarkistaa tämän teknisen asiakirjan?",
            "Ville De have venlighed til at gennemse dette tekniske dokument?",
        ]

        ids, mask = email_ai.tokenizer.encode(formal_sentences, max_length=56)
        with torch.no_grad():
            preds = email_ai(ids, mask)

        pol = preds["politeness_score"].squeeze()
        assert pol.shape[0] == 8
        assert float(pol.mean().item()) > 0.65
        for p in pol:
            assert float(p.item()) > 0.35

    def test_universal_phonology_and_listening_sub_ai_bubble5(self):
        ckpt = torch.load(SUB_CKPT_PATH_5, map_location="cpu")
        pron_ai = PronunciationSubAINeural()
        pron_ai.load_state_dict(ckpt["pronunciation_sub_ai"])
        pron_ai.eval()

        list_ai = ListeningSubAINeural()
        list_ai.load_state_dict(ckpt["listening_sub_ai"])
        list_ai.eval()

        samples = [
            "שמש שוקעת מעל הרי ירושלים בערב.",
            "မိုးရွာတုန်း ရေခံ သာတုန်း ဗျိုင်းပျံ။",
            "ዝናብ ሲዘንብ እንቁራሪቶች ይጮኻሉ።",
            "Kò sí ẹni tí ó mọ ọ̀la àfi Ọlọ́run.",
            "Burung merpati terbang tinggi di langit membiru.",
            "ଝିପିଝିପି ବର୍ଷା ହେଉଥିଲା ଏବଂ ପବନ ବହୁଥିଲା।",
            "Vesihiisi sihisi hississä hiljaisena iltana.",
            "Rødgrød med fløde smager dejligt i sommervarmen.",
        ]

        for text in samples:
            p_ids, p_mask = pron_ai.tokenizer.encode([text], max_length=48)
            with torch.no_grad():
                p_out = pron_ai(p_ids, p_mask)
                l_out = list_ai(p_ids, p_mask)
            assert 0.0 <= p_out["ending_audibility"].item() <= 1.0
            assert 0.0 <= p_out["tonal_accuracy"].item() <= 1.0
            assert "rhythm_logits" in l_out
            assert "boundary_entropy" in l_out

    def test_universal_reviewing_sub_ai_bubble5(self):
        ckpt = torch.load(SUB_CKPT_PATH_5, map_location="cpu")
        rev_ai = ReviewingSubAINeural()
        rev_ai.load_state_dict(ckpt["reviewing_sub_ai"])
        rev_ai.eval()

        sentences = [
            "המערכת פועלת באופן יציב ומהיר לחלוטין.",
            "စနစ်သည် အလွန်တည်ငြိမ်စွာ အလုပ်လုပ်လျက်ရှိသည်။",
            "ስርዓቱ በጣም በተረጋጋ እና ፈጣን ሁኔታ እየሰራ ነው።",
            "Ètò náà ń ṣiṣẹ́ dáadáa láìsí ìṣòro kankan.",
            "Sistem ini berfungsi dengan amat stabil dan lancar.",
            "ପ୍ରଣାଳୀଟି ଅତ୍ୟନ୍ତ ସ୍ଥିର ଏବଂ ଦ୍ରୁତ ଗତିରେ କାର୍ଯ୍ୟ କରୁଛି।",
            "Järjestelmä toimii täydellisen vakaasti ja erittäin nopeasti.",
            "Systemet fungerer fuldstændig stabilt og bemærkelsesværdigt hurtigt.",
        ]

        ids, mask = rev_ai.tokenizer.encode(sentences, max_length=48)
        with torch.no_grad():
            preds = rev_ai(ids, mask)

        error_logits = preds["error_taxonomy_logits"]
        assert error_logits.shape[0] == 8
        assert "hedging_score" in preds


class TestMasterOrchestratorsBubble5:
    """Verifies that all 8 Bubble 5 master orchestrators initialize and synchronize cleanly with AMSV."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_5)
    def test_engine_orchestrator_initialization_bubble5(self, lang_name, eng_dir):
        mod_name = f"{eng_dir}.{lang_name.lower()}_engine_orchestrator"
        cls_name = f"{lang_name}EngineOrchestrator"

        mod = importlib.import_module(mod_name)
        orchestrator_cls = getattr(mod, cls_name)

        amsv = AMSVEmbeddedView()
        orch = orchestrator_cls(amsv_view=amsv)

        # Zero-bridge AMSV verification
        assert isinstance(orch.amsv, AMSVEmbeddedView)
        assert orch.amsv._view.nbytes == 64

        # Run process cycle
        res = orch.analyze("Global cohort benchmark testing with zero-latency memory synchronization.")
        assert res.amsv_synced is True
        assert res.syntax_eval.amsv_synced is True
        assert res.phonology_eval.amsv_synced is True
        assert res.pragmatic_eval.amsv_synced is True
        assert res.editorial_eval.amsv_synced is True
        assert 0.0 <= res.overall_linguistic_score <= 1.0
