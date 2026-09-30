"""
test_ecse.py — Emotional Communication & Social Calibration Engine (ECSE) Integration Tests
"""
import sys, os, ctypes, struct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ecse.python.ecse_orchestrator import (
    AffectValenceAI, RapportBuildingAI, MirrorMatchingAI,
    MicroDisagreementAI, PolitenessRegisterAI,
    EmotionalCommunicationSocialOrchestrator
)


class TestAffectValenceAI:
    def test_positive_affect_detected(self):
        ai = AffectValenceAI()
        text = "I'm genuinely excited and passionate about this opportunity. I'm confident we'd achieve fantastic results."
        r = ai.evaluate(text)
        assert r["positive_affect"] >= 0.20
        assert r["valence_score"] > 0.0

    def test_negative_affect_detected(self):
        ai = AffectValenceAI()
        text = "Unfortunately this is a very difficult and challenging situation. I'm quite anxious about the outcome."
        r = ai.evaluate(text)
        assert r["negative_affect"] >= 0.20
        assert r["valence_score"] < 0.0

    def test_neutral_text_balanced(self):
        ai = AffectValenceAI()
        text = "I led a team. We shipped three features. The metrics showed 15% improvement."
        r = ai.evaluate(text)
        assert abs(r["valence_score"]) <= 0.20


class TestRapportBuildingAI:
    def test_high_rapport_detected(self):
        ai = RapportBuildingAI()
        text = "I appreciate your perspective. That resonates with my experience. Together as a team we can achieve this."
        r = ai.evaluate(text)
        assert r["composite_score"] >= 0.60

    def test_no_rapport_low_score(self):
        ai = RapportBuildingAI()
        text = "The technical stack includes Kubernetes, gRPC, and Kafka with eventual consistency guarantees."
        r = ai.evaluate(text)
        assert r["warmth_density"] <= 0.10


class TestMirrorMatchingAI:
    def test_vocabulary_mirror_detected(self):
        ai = MirrorMatchingAI()
        q = "Tell me about your experience with microservices architecture and service mesh design."
        a = "I designed a microservices architecture using Istio as the service mesh. The architecture handled 100k RPS."
        r = ai.evaluate(a, q, candidate_wpm=145.0, interviewer_wpm=140.0)
        assert r["vocabulary_mirror"] >= 0.20

    def test_rhythm_sync_close_wpm(self):
        ai = MirrorMatchingAI()
        r = ai.evaluate("Answer text.", "Question text.", candidate_wpm=130.0, interviewer_wpm=135.0)
        assert r["rhythm_synchrony"] >= 0.90

    def test_rhythm_sync_divergent_wpm(self):
        ai = MirrorMatchingAI()
        r = ai.evaluate("Answer.", "Question.", candidate_wpm=200.0, interviewer_wpm=120.0)
        assert r["rhythm_synchrony"] <= 0.70


class TestMicroDisagreementAI:
    def test_hedging_detected(self):
        ai = MicroDisagreementAI()
        text = "Somewhat, in a way. To some extent I agree, but it kind of depends on the context."
        r = ai.evaluate(text)
        assert r["hedge_count"] >= 3
        assert r["disagreement_signal"] >= 0.30

    def test_confident_agreement_no_hedging(self):
        ai = MicroDisagreementAI()
        text = "Absolutely. I fully agree with that approach and have implemented it successfully."
        r = ai.evaluate(text)
        assert r["hedge_count"] == 0
        assert r["composite_score"] >= 0.90


class TestPolitenessRegisterAI:
    def test_high_courtesy_detected(self):
        ai = PolitenessRegisterAI()
        text = "Thank you for this opportunity. I appreciate your question. Of course, I'd be happy to elaborate."
        r = ai.evaluate(text)
        assert r["courtesy_markers"] >= 2
        assert r["composite_score"] >= 0.60

    def test_crude_language_penalized(self):
        ai = PolitenessRegisterAI()
        text = "Whatever. To be honest I don't care about the process. Just bluntly speaking here."
        r = ai.evaluate(text)
        assert r["formal_compliance"] <= 0.50


class TestECSEOrchestrator:
    def test_full_pipeline_calibrated(self):
        orc = EmotionalCommunicationSocialOrchestrator()
        q = "What motivates you most in your work?"
        a = ("I appreciate that question. I'm genuinely passionate about building systems that empower people. "
             "Thank you for giving me the opportunity to share. Together we can absolutely achieve this vision.")
        r = orc.evaluate_turn(a, q, turn_number=1, candidate_wpm=145.0, interviewer_wpm=140.0)
        assert "global_social_intelligence" in r
        assert r["global_social_intelligence"] >= 0.55
        assert r["social_label"] in ("HIGHLY_ATTUNED","CALIBRATED","ADEQUATE","MISALIGNED")

    def test_amsv_sync_writes_affect_bytes(self):
        buf = bytearray(64)
        orc = EmotionalCommunicationSocialOrchestrator(master_amsv_buffer=buf)
        orc.evaluate_turn("I'm genuinely excited and passionate about this role.", "", turn_number=1)
        aff_raw, rapp_raw, mir_raw, dis_raw = struct.unpack_from("<HHHH", buf, 0x10)
        assert aff_raw > 0

    def test_cpp_dll_evaluate(self):
        dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ecse', 'cpp', 'libecse_core.dll'))
        if not os.path.exists(dll_path):
            pytest.skip("libecse_core.dll not compiled")
        lib = ctypes.CDLL(dll_path, winmode=0)
        lib.ecse_cpp_evaluate.restype = ctypes.c_int32
        a = ctypes.c_char_p(b"I appreciate your perspective. Absolutely, I'm excited about this opportunity.")
        q = ctypes.c_char_p(b"What drives your motivation at work?")
        buf = ctypes.create_string_buffer(256)
        ret = lib.ecse_cpp_evaluate(a, q, ctypes.c_float(145.0), ctypes.c_float(140.0), ctypes.c_uint16(1), buf)
        assert ret == 0
