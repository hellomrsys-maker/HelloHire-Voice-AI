"""
test_hindustani_dialogue_dynamics.py - Test Suite for Hindustani Conversational Dynamics & Turn-Taking.

Verifies:
1. Observational Conversational Dataset integrity and zero-voice-cloning compliance.
2. DialogueDynamicsAnalyzer turn-taking latency (wait time in ms), floor holding, and register alignment.
3. Neural checkpoint loading and multi-task predictions (latency, speech act, tempo, floor).
4. Master Orchestrator integration and zero-bridge AMSV synchronization.
"""

from __future__ import annotations
import os
import json
import pytest
import torch

from amsv.python.amsv_embedded import AMSVEmbeddedView
from Hindustani_engine.hindustani_engine_orchestrator import HindustaniEngineOrchestrator
from Hindustani_engine.brain.analysis.dialogue_dynamics_analyzer import DialogueDynamicsAnalyzer, TurnDynamicsResult
from training.train_hindustani_dialogue_dynamics import HindustaniDialogueDynamicsNeural

CKPT_PATH = os.path.join("checkpoints", "hindustani_dialogue_dynamics_verified.pt")
CORPUS_PATH = os.path.join("Hindustani_engine", "6_DATA_REQUIREMENTS", "conversational_dialogue_dynamics_corpus.json")


class TestDialogueCorpusAndManifest:
    """Verifies the observational conversational corpus structure."""

    def test_corpus_exists_and_valid(self):
        assert os.path.exists(CORPUS_PATH), f"Corpus missing at {CORPUS_PATH}"
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["zero_voice_cloning_certified"] is True
        scenes = data.get("dialogue_scenes", [])
        assert len(scenes) >= 5

        for sc in scenes:
            assert "scene_id" in sc
            assert "register" in sc
            assert len(sc["turns"]) >= 2
            for t in sc["turns"]:
                assert "text" in t
                assert "post_utterance_pause_ms" in t
                assert "expected_response_latency_range_ms" in t
                assert t["post_utterance_pause_ms"] > 0


class TestDialogueDynamicsAnalyzer:
    """Verifies conversational timing, turn wait latency, and pragmatic registers."""

    def setup_method(self):
        self.amsv = AMSVEmbeddedView()
        self.analyzer = DialogueDynamicsAnalyzer(amsv_view=self.amsv)

    def test_urgent_conversational_turn_timing(self):
        # Urgent query requires brisk response (< 400ms)
        text = "यार, यह थ्रेड तो बार-बार क्रैश हो रहा है, तुरंत कुछ करो!"
        res = self.analyzer.analyze_dialogue_turn(text)

        assert res.delivery_tempo == "ALLEGRO_FAST"
        assert res.recommended_wait_time_ms <= 400
        assert res.detected_register in ["TUM", "TU"]
        assert res.amsv_synced is True

    def test_respectful_mentorship_conversational_turn(self):
        # Respectful inquiry with Aap register
        text = "सर, क्या आप इस नए आर्किटेक्चर की समीक्षा करना चाहेंगे?"
        res = self.analyzer.analyze_dialogue_turn(text)

        assert res.detected_register == "AAP"
        assert res.recommended_reply_register == "AAP"
        assert 350 <= res.recommended_wait_time_ms <= 650
        assert res.is_question is True
        assert res.amsv_synced is True

    def test_reflective_philosophical_turn_timing(self):
        # Deep philosophical statement requires longer contemplative pause (> 700ms)
        text = "क्या आपको लगता है कि मशीनें वास्तव में मानव चेतना और संवेदनशीलता की गहरी अनुभूति को समझ पाएंगी?"
        res = self.analyzer.analyze_dialogue_turn(text)

        assert res.delivery_tempo == "LENTO_DELIBERATE"
        assert res.recommended_wait_time_ms >= 750
        assert res.speech_act_detected == "REFLECTIVE_INQUIRY"
        assert res.amsv_synced is True

    def test_floor_holding_filler_detection(self):
        # When speaker uses floor-holding fillers and ellipsis, floor is held (not yielded)
        text = "देखिए... असल में बात यह है..."
        res = self.analyzer.analyze_dialogue_turn(text)

        assert res.floor_yielding is False


class TestNeuralDialogueDynamicsModel:
    """Verifies neural model checkpoint inference without voice cloning."""

    def test_checkpoint_exists_and_verified(self):
        assert os.path.exists(CKPT_PATH), f"Checkpoint missing at {CKPT_PATH}"
        assert os.path.exists(CKPT_PATH + ".json"), "Checkpoint metadata sidecar missing"
        with open(CKPT_PATH + ".json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["zero_voice_cloning_certified"] is True
        assert "sha256" in meta

    def test_neural_inference_predictions(self):
        ckpt = torch.load(CKPT_PATH, map_location="cpu")
        model = HindustaniDialogueDynamicsNeural(d_model=128)
        model.load_state_dict(ckpt)
        model.eval()

        sentences = [
            "सर, क्या आपको लगता है कि यह नया सिस्टम काम करेगा?",
            "रुक, मुझे लॉग्स देखने दे तुरंत!",
            "मानव चेतना की अनुभूति अत्यंत गहरी है।",
        ]

        ids, mask = model.tokenizer.encode(sentences, max_length=64)
        with torch.no_grad():
            preds = model(ids, mask)

        lat_ms = preds["predicted_latency_ms"].squeeze()
        reg_logits = preds["register_logits"]
        act_logits = preds["speech_act_logits"]
        tempo_logits = preds["tempo_logits"]
        floor_prob = preds["floor_yielding_prob"].squeeze()

        assert lat_ms.shape[0] == 3
        for lat in lat_ms:
            assert 100.0 <= float(lat.item()) <= 1500.0

        assert reg_logits.shape == (3, 3)
        assert act_logits.shape == (3, 6)
        assert tempo_logits.shape == (3, 3)
        for flr in floor_prob:
            assert 0.0 <= float(flr.item()) <= 1.0


class TestOrchestratorDialogueIntegration:
    """Verifies HindustaniEngineOrchestrator dialogue analysis and AMSV integration."""

    def test_orchestrator_dialogue_turn_analysis(self):
        amsv = AMSVEmbeddedView()
        orch = HindustaniEngineOrchestrator(amsv_view=amsv)

        turn_res = orch.analyze_dialogue_turn("सर, क्या आप हमें मार्गदर्शन दे सकते हैं?")
        assert isinstance(turn_res, TurnDynamicsResult)
        assert turn_res.detected_register == "AAP"
        assert turn_res.recommended_wait_time_ms > 0
        assert turn_res.amsv_synced is True

        # Complete linguistic pipeline analysis
        full_res = orch.analyze("हम मिलकर एक बहुत ही मजबूत और सुरक्षित प्रणाली विकसित करेंगे।")
        assert full_res.amsv_synced is True
        assert full_res.turn_dynamics is not None
        assert full_res.turn_dynamics.recommended_wait_time_ms > 0
        assert amsv._view.nbytes == 64
