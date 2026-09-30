"""
test_multilingual_bubble3.py - Complete Test Suite for Multilingual Bubble 3 (6 Languages).

Verifies:
1. Dataset & Curriculum Manifest Integrity across all 6 Population Cohort Engines:
   - Punjabi, Telugu, Marathi, Tagalog, Hausa, Ukrainian (~560M+ speakers).
2. Bubble 3 verified checkpoints existence, weights loading, and SHA-256 integrity.
3. Universal Sub-AIs neural inference across all 6 target languages.
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

TARGET_ENGINES_3 = [
    ("Punjabi", "Punjabi_engine"),
    ("Telugu", "Telugu_engine"),
    ("Marathi", "Marathi_engine"),
    ("Tagalog", "Tagalog_engine"),
    ("Hausa", "Hausa_engine"),
    ("Ukrainian", "Ukrainian_engine"),
]

MAIN_CKPT_PATH_3 = os.path.join("checkpoints", "multilingual_bubble3_main_model_verified.pt")
SUB_CKPT_PATH_3 = os.path.join("checkpoints", "multilingual_bubble3_sub_ais_verified.pt")


class TestMultilingualCorporaAndManifestsBubble3:
    """Verifies all 6 languages have complete, valid grammar corpora and curriculum manifests."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_3)
    def test_corpus_exists_and_populated_bubble3(self, lang_name, eng_dir):
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

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_3)
    def test_manifest_exists_and_valid_bubble3(self, lang_name, eng_dir):
        manifest_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", f"{lang_name.lower()}_full_curriculum_manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest file for {lang_name} at {manifest_file}"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == lang_name
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) == 3
        assert data["ready_for_neural_training"] is True


class TestMultilingualCheckpointsAndSubAIsBubble3:
    """Verifies checkpoint persistence, SHA-256 fingerprinting, and universal sub-AI inference for Bubble 3."""

    def test_checkpoint_files_and_sidecars_bubble3(self):
        assert os.path.exists(MAIN_CKPT_PATH_3), f"Main checkpoint missing: {MAIN_CKPT_PATH_3}"
        assert os.path.exists(SUB_CKPT_PATH_3), f"Sub-AIs checkpoint missing: {SUB_CKPT_PATH_3}"
        assert os.path.exists(MAIN_CKPT_PATH_3 + ".json"), "Main metadata sidecar missing"
        assert os.path.exists(SUB_CKPT_PATH_3 + ".json"), "Sub-AIs metadata sidecar missing"

        with open(SUB_CKPT_PATH_3, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SUB_CKPT_PATH_3 + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["sha256"] == computed_hash

    def test_universal_writing_sub_ai_cross_lingual_bubble3(self):
        ckpt = torch.load(SUB_CKPT_PATH_3, map_location="cpu")
        writing_ai = WritingSubAINeural()
        writing_ai.load_state_dict(ckpt["writing_sub_ai"])
        writing_ai.eval()

        test_sentences = [
            "ਇੰਜੀਨੀਅਰ ਨੇ ਇੱਕ ਬਹੁਤ ਹੀ ਕੁਸ਼ਲ ਵੰਡਿਆ ਹੋਇਆ ਸਿਸਟਮ ਤਿਆਰ ਕੀਤਾ ਹੈ।",
            "ఇంజనీరు అత్యంత సమర్థవంతమైన పంపిణీ వ్యవస్థను రూపొందించారు.",
            "अभियंत्याने अत्यंत कार्यक्षम वितरित प्रणाली विकसित केली आहे.",
            "Bumuo ang inhinyero ng isang napakahusay na sistemang ipinamamahagi.",
            "Injiniyan ya gina ingantaccen tsarin rarraba bayanai mai matuƙar inganci.",
            "Інженер розробив надзвичайно ефективну розподілену систему.",
        ]

        ids, mask = writing_ai.tokenizer.encode(test_sentences, max_length=56)
        with torch.no_grad():
            preds = writing_ai(ids, mask)

        comp = preds["sentence_completeness"].squeeze()
        assert comp.shape[0] == 6
        for score in comp:
            assert float(score.item()) > 0.50

    def test_universal_email_sub_ai_cross_lingual_bubble3(self):
        ckpt = torch.load(SUB_CKPT_PATH_3, map_location="cpu")
        email_ai = EmailSubAINeural()
        email_ai.load_state_dict(ckpt["email_sub_ai"])
        email_ai.eval()

        formal_sentences = [
            "ਕੀ ਤੁਸੀਂ ਕਿਰਪਾ ਕਰਕੇ ਇਸ ਤਕਨੀਕੀ ਦਸਤਾਵੇਜ਼ ਦੀ ਸਮੀਖਿਆ ਕਰੋਗੇ?",
            "మీరు దయచేసి ఈ సాంకేతిక పత్రాన్ని సమీక్షిస్తారా?",
            "कृपया आपण या तांत्रिक दस्तऐवजाचे पुनरावलोकन कराल का?",
            "Maaari po ba ninyong suriin ang teknikal na dokumentong ito?",
            "Shin za ku iya duba wannan takarda ta fasaha don Allah?",
            "Чи не могли б Ви, будь ласка, ознайомитися з цим технічним документом?",
        ]

        ids, mask = email_ai.tokenizer.encode(formal_sentences, max_length=56)
        with torch.no_grad():
            preds = email_ai(ids, mask)

        pol = preds["politeness_score"].squeeze()
        assert pol.shape[0] == 6
        assert float(pol.mean().item()) > 0.65
        for p in pol:
            assert float(p.item()) > 0.40

    def test_universal_phonology_and_listening_sub_ai_bubble3(self):
        ckpt = torch.load(SUB_CKPT_PATH_3, map_location="cpu")
        pron_ai = PronunciationSubAINeural()
        pron_ai.load_state_dict(ckpt["pronunciation_sub_ai"])
        pron_ai.eval()

        list_ai = ListeningSubAINeural()
        list_ai.load_state_dict(ckpt["listening_sub_ai"])
        list_ai.eval()

        samples = [
            "ਕੋੜਾ ਘੋੜਾ ਦੌੜਿਆ ਪਹਾੜ ਵੱਲ।",
            "గాజుల గలగలలు పిల్లల కిలకిలలు.",
            "चांदण्या रात्री तांदूळ सडला.",
            "Kakakaba-kaba ba ang pakiramdam mo?",
            "Ɗan ƙaramin ɓawo ya faɗi a ƙasa.",
            "У затишному гаю щебече дзвінкий соловейко.",
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

    def test_universal_reviewing_sub_ai_bubble3(self):
        ckpt = torch.load(SUB_CKPT_PATH_3, map_location="cpu")
        rev_ai = ReviewingSubAINeural()
        rev_ai.load_state_dict(ckpt["reviewing_sub_ai"])
        rev_ai.eval()

        sentences = [
            "ਸਿਸਟਮ ਬਹੁਤ ਹੀ ਸਥਿਰ ਅਤੇ ਤੇਜ਼ ਚੱਲ ਰਿਹਾ ਹੈ।",
            "వ్యవస్థ చాలా స్థిరంగా పనిచేస్తోంది.",
            "प्रणाली अत्यंत स्थिर आणि सुरळीत चालत आहे.",
            "Tumatakbo nang napakatatag at maayos ang buong sistema.",
            "Tsarin yana aiki lafiya kalau kuma cikin kwanciyar hankali.",
            "Система працює абсолютно стабільно, швидко та безвідмовно.",
        ]

        ids, mask = rev_ai.tokenizer.encode(sentences, max_length=48)
        with torch.no_grad():
            preds = rev_ai(ids, mask)

        error_logits = preds["error_taxonomy_logits"]
        assert error_logits.shape[0] == 6
        assert "hedging_score" in preds


class TestMasterOrchestratorsBubble3:
    """Verifies that all 6 Bubble 3 master orchestrators initialize and synchronize cleanly with AMSV."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_3)
    def test_engine_orchestrator_initialization_bubble3(self, lang_name, eng_dir):
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
