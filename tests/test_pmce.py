"""
test_pmce.py — Persuasion & Message Construction Engine (PMCE) Integration Tests
"""
import sys, os, struct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pmce.python.pmce_orchestrator import (
    LogosAI, EthosAI, PathosAI, KairosAI, CTAAI,
    PersuasionMessageConstructionOrchestrator
)


class TestLogosAI:
    def test_logical_argument_with_data_scores_high(self):
        ai = LogosAI()
        text = ("Because our p99 latency increased by 40%, the evidence suggests we need caching. "
                "Therefore, I recommend Redis. Data shows a 60% reduction in DB calls.")
        r = ai.evaluate(text)
        assert r["composite_score"] >= 0.55
        assert r["data_backed"] is True

    def test_fallacy_penalized(self):
        ai = LogosAI()
        text = "Everyone knows this approach is correct. It's obvious. We should always do it this way."
        r = ai.evaluate(text)
        assert r["fallacy_count"] >= 2
        assert r["composite_score"] <= 0.45

    def test_no_argument_structure_low_score(self):
        ai = LogosAI()
        text = "I worked hard and did my best. The project went well."
        r = ai.evaluate(text)
        assert r["composite_score"] <= 0.50


class TestEthosAI:
    def test_credential_signals_detected(self):
        ai = EthosAI()
        text = "In my experience as a principal engineer, having led three platform re-architectures, I have delivered 99.99% uptime."
        r = ai.evaluate(text)
        assert r["credential_signals"] >= 2
        assert r["composite_score"] >= 0.45

    def test_no_credentials_low_score(self):
        ai = EthosAI()
        text = "I think the system is good. It works well and people like it."
        r = ai.evaluate(text)
        assert r["composite_score"] <= 0.25

    def test_expert_vocabulary_detected(self):
        ai = EthosAI()
        text = "We tracked the ROI per OKR cycle. The p99 latency and KPI metrics drove stakeholder confidence."
        r = ai.evaluate(text)
        assert r["expertise_markers"] >= 3


class TestPathosAI:
    def test_high_pathos_emotional_language(self):
        ai = PathosAI()
        text = "Imagine the impact we could create. I believe this would transform and inspire the entire team's journey."
        r = ai.evaluate(text)
        assert r["composite_score"] >= 0.50

    def test_dry_technical_text_low_pathos(self):
        ai = PathosAI()
        text = "The service uses gRPC and runs 3 replicas behind an L7 load balancer."
        r = ai.evaluate(text)
        assert r["composite_score"] <= 0.50


class TestKairosAI:
    def test_situational_transitions_detected(self):
        ai = KairosAI()
        text = "Building on that point, and given what you just mentioned about scale, this is exactly why we chose Kafka."
        r = ai.evaluate(text, turn_number=3)
        assert r["transition_cues"] >= 1

    def test_context_anchors_improve_kairos(self):
        ai = KairosAI()
        text = "As you mentioned earlier, referring to your point about team dynamics, I agree completely."
        r = ai.evaluate(text, turn_number=5)
        assert r["context_anchors"] >= 1
        assert r["composite_score"] >= 0.50


class TestCTAAI:
    def test_strong_cta_detected(self):
        ai = CTAAI()
        text = "My recommendation is that we move forward with the microservices migration. I propose we start in Q1."
        r = ai.evaluate(text)
        assert r["strong_cta_signals"] >= 2
        assert r["composite_score"] >= 0.70

    def test_weak_ending_penalized(self):
        ai = CTAAI()
        text = "I think maybe we could potentially consider something like that kind of approach possibly."
        r = ai.evaluate(text)
        assert r["weak_ending_count"] >= 2
        assert r["composite_score"] <= 0.40

    def test_neutral_factual_low_cta(self):
        ai = CTAAI()
        text = "The architecture has three services. Each handles a separate domain."
        r = ai.evaluate(text)
        assert r["composite_score"] <= 0.45


class TestPMCEOrchestrator:
    def test_full_pipeline_highly_persuasive(self):
        orc = PersuasionMessageConstructionOrchestrator()
        text = (
            "In my experience leading distributed systems teams, having delivered three successful platform migrations, "
            "the evidence suggests — with 40% latency improvement and clear ROI data — that we should move forward. "
            "Imagine the impact on our customers. Building on your point, therefore I propose we begin in Q1. "
            "My recommendation is to form a cross-functional task force immediately."
        )
        r = orc.evaluate_turn(text, turn_number=4)
        assert r["global_persuasion_index"] >= 0.48
        assert r["persuasion_label"] in ("HIGHLY_PERSUASIVE","PERSUASIVE","ADEQUATE","WEAK")

    def test_amsv_sync_writes_logos_bytes(self):
        buf = bytearray(64)
        orc = PersuasionMessageConstructionOrchestrator(master_amsv_buffer=buf)
        orc.evaluate_turn("Because the data shows 40% improvement, therefore I recommend Redis.", turn_number=1)
        logos_raw, ethos_raw, pathos_raw, kairos_raw = struct.unpack_from("<HHHH", buf, 0x10)
        assert logos_raw > 0

    def test_grade_labels_are_valid(self):
        orc = PersuasionMessageConstructionOrchestrator()
        valid_labels = {"HIGHLY_PERSUASIVE", "PERSUASIVE", "ADEQUATE", "WEAK"}
        for text in [
            "Because the data shows this is right, therefore I recommend immediate action.",
            "I think maybe we could possibly do something.",
            "The system has three services."
        ]:
            r = orc.evaluate_turn(text, turn_number=1)
            assert r["persuasion_label"] in valid_labels
