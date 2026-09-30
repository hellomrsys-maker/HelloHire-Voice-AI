"""
test_multilingual_bubble4.py - Complete Test Suite for Multilingual Bubble 4 (8 Languages).

Verifies:
1. Dataset & Curriculum Manifest Integrity across all 8 Global Expansion Engines:
   - Gujarati, Kannada, Malayalam, Greek, Czech, Swedish, Romanian, Hungarian.
2. Bubble 4 verified checkpoints existence, weights loading, and SHA-256 integrity.
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

TARGET_ENGINES_4 = [
    ("Gujarati", "Gujarati_engine"),
    ("Kannada", "Kannada_engine"),
    ("Malayalam", "Malayalam_engine"),
    ("Greek", "Greek_engine"),
    ("Czech", "Czech_engine"),
    ("Swedish", "Swedish_engine"),
    ("Romanian", "Romanian_engine"),
    ("Hungarian", "Hungarian_engine"),
]

MAIN_CKPT_PATH_4 = os.path.join("checkpoints", "multilingual_bubble4_main_model_verified.pt")
SUB_CKPT_PATH_4 = os.path.join("checkpoints", "multilingual_bubble4_sub_ais_verified.pt")


class TestMultilingualCorporaAndManifestsBubble4:
    """Verifies all 8 languages have complete, valid grammar corpora and curriculum manifests."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_4)
    def test_corpus_exists_and_populated_bubble4(self, lang_name, eng_dir):
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

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_4)
    def test_manifest_exists_and_valid_bubble4(self, lang_name, eng_dir):
        manifest_file = os.path.join(eng_dir, "6_DATA_REQUIREMENTS", f"{lang_name.lower()}_full_curriculum_manifest.json")
        assert os.path.exists(manifest_file), f"Missing manifest file for {lang_name} at {manifest_file}"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == lang_name
        assert "curriculum_stages" in data
        assert len(data["curriculum_stages"]) == 3
        assert data["ready_for_neural_training"] is True


class TestMultilingualCheckpointsAndSubAIsBubble4:
    """Verifies checkpoint persistence, SHA-256 fingerprinting, and universal sub-AI inference for Bubble 4."""

    def test_checkpoint_files_and_sidecars_bubble4(self):
        assert os.path.exists(MAIN_CKPT_PATH_4), f"Main checkpoint missing: {MAIN_CKPT_PATH_4}"
        assert os.path.exists(SUB_CKPT_PATH_4), f"Sub-AIs checkpoint missing: {SUB_CKPT_PATH_4}"
        assert os.path.exists(MAIN_CKPT_PATH_4 + ".json"), "Main metadata sidecar missing"
        assert os.path.exists(SUB_CKPT_PATH_4 + ".json"), "Sub-AIs metadata sidecar missing"

        with open(SUB_CKPT_PATH_4, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SUB_CKPT_PATH_4 + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["sha256"] == computed_hash

    def test_universal_writing_sub_ai_cross_lingual_bubble4(self):
        ckpt = torch.load(SUB_CKPT_PATH_4, map_location="cpu")
        writing_ai = WritingSubAINeural()
        writing_ai.load_state_dict(ckpt["writing_sub_ai"])
        writing_ai.eval()

        test_sentences = [
            "ઇજનેરે અત્યંત કાર્યક્ષમ વિતરિત સિસ્ટમ વિકસાવી છે.",
            "ಇಂಜಿನಿಯರ್ ಅತ್ಯಂತ ಪರಿಣಾಮಕಾರಿ ವಿತರಿಸಿದ ವ್ಯವಸ್ಥೆಯನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸಿದ್ದಾರೆ.",
            "എഞ്ചിനീയർ വളരെ കാര്യക്ഷമമായ വിതരണ സംവിധാനം നിർമ്മിച്ചു.",
            "Ο μηχανικός σχεδίασε ένα εξαιρετικά αποδοτικό κατανεμημένο σύστημα.",
            "Inženýr navrhl mimořádně efektivní distribuovaný systém.",
            "Ingenjören designade ett extremt effektivt distribuerat system.",
            "Inginerul a proiectat un sistem distribuit extrem de eficient.",
            "A mérnök egy rendkívül hatékony elosztott rendszert tervezett.",
        ]

        ids, mask = writing_ai.tokenizer.encode(test_sentences, max_length=56)
        with torch.no_grad():
            preds = writing_ai(ids, mask)

        comp = preds["sentence_completeness"].squeeze()
        assert comp.shape[0] == 8
        for score in comp:
            assert float(score.item()) > 0.50

    def test_universal_email_sub_ai_cross_lingual_bubble4(self):
        ckpt = torch.load(SUB_CKPT_PATH_4, map_location="cpu")
        email_ai = EmailSubAINeural()
        email_ai.load_state_dict(ckpt["email_sub_ai"])
        email_ai.eval()

        formal_sentences = [
            "શું તમે કૃપા કરીને આ તકનીકી દસ્તાવેજની સમીક્ષા કરશો?",
            "ತಾವು ದಯವಿಟ್ಟು ಈ ತಾಂತ್ರಿಕ ದಾಖಲೆಯನ್ನು ಪರಿಶೀಲಿಸುವಿರಾ?",
            "ദയവായി താങ്കൾ ഈ സാങ്കേതിക രേഖ പരിശോധിക്കാമോ?",
            "Θα είχατε την καλοσύνη να εξετάσετε αυτό το τεχνικό έγγραφο;",
            "Byl byste tak laskav a prohlédl si tento technický dokument?",
            "Skulle Ni vänligen ha möjlighet att granska detta tekniska dokument?",
            "Ați avea amabilitatea să examinați acest document tehnic?",
            "Lenne szíves áttekinteni ezt a műszaki dokumentációt?",
        ]

        ids, mask = email_ai.tokenizer.encode(formal_sentences, max_length=56)
        with torch.no_grad():
            preds = email_ai(ids, mask)

        pol = preds["politeness_score"].squeeze()
        assert pol.shape[0] == 8
        assert float(pol.mean().item()) > 0.65
        for p in pol:
            assert float(p.item()) > 0.40

    def test_universal_phonology_and_listening_sub_ai_bubble4(self):
        ckpt = torch.load(SUB_CKPT_PATH_4, map_location="cpu")
        pron_ai = PronunciationSubAINeural()
        pron_ai.load_state_dict(ckpt["pronunciation_sub_ai"])
        pron_ai.eval()

        list_ai = ListeningSubAINeural()
        list_ai.load_state_dict(ckpt["listening_sub_ai"])
        list_ai.eval()

        samples = [
            "ઝરમર ઝરમર વરસાદ વરસે છે.",
            "ತಂಪು ಗಾಳಿ ಬೀಸುತ್ತಿತ್ತು ಮರಗಳು ತೂಗುತ್ತಿದ್ದವು.",
            "മഴ പെയ്യുമ്പോൾ തവളകൾ പാടാൻ തുടങ്ങി.",
            "Καλημέρα σας κύριε καθηγητά.",
            "Tři sta třicet tři stříbrných stříkaček.",
            "Sju sjösjuka sjömän sköttes av sju sköna sjuksköterskor.",
            "Capra calcă piatra, piatra crapă-n patru.",
            "Mit sütsz, kis szűcs? Tán sós húst sütsz, kis szűcs?",
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

    def test_universal_reviewing_sub_ai_bubble4(self):
        ckpt = torch.load(SUB_CKPT_PATH_4, map_location="cpu")
        rev_ai = ReviewingSubAINeural()
        rev_ai.load_state_dict(ckpt["reviewing_sub_ai"])
        rev_ai.eval()

        sentences = [
            "સિસ્ટમ અત્યંત સ્થિર અને ઝડપી કામ કરે છે.",
            "ವ್ಯವಸ್ಥೆಯು ಅತ್ಯಂತ ಸ್ಥಿರವಾಗಿ ಮತ್ತು ವೇಗವಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿದೆ.",
            "സിസ്റ്റം വളരെ സുഗമമായി പ്രവർത്തിക്കുന്നുണ്ട്.",
            "Το σύστημα λειτουργεί απόλυτα σταθερά και γρήγορα.",
            "Systém funguje naprosto stabilně a bezchybně.",
            "Systemet fungerar fullständigt stabilt och snabbt.",
            "Sistemul funcționează perfect stabil și foarte rapid.",
            "A rendszer teljesen stabilan és megbízhatóan működik.",
        ]

        ids, mask = rev_ai.tokenizer.encode(sentences, max_length=48)
        with torch.no_grad():
            preds = rev_ai(ids, mask)

        error_logits = preds["error_taxonomy_logits"]
        assert error_logits.shape[0] == 8
        assert "hedging_score" in preds


class TestMasterOrchestratorsBubble4:
    """Verifies that all 8 Bubble 4 master orchestrators initialize and synchronize cleanly with AMSV."""

    @pytest.mark.parametrize("lang_name,eng_dir", TARGET_ENGINES_4)
    def test_engine_orchestrator_initialization_bubble4(self, lang_name, eng_dir):
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
