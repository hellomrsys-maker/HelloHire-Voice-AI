"""
test_pace.py — Comprehensive Unit & Integration Tests for PACE (Pacing & Adaptation Calibration Engine).
"""

import struct
import pytest
from pace.python.sub_ais.vocabulary_adaptation_ai import VocabularyAdaptationAI
from pace.python.sub_ais.response_length_calibrator_ai import ResponseLengthCalibratorAI
from pace.python.sub_ais.register_shift_ai import RegisterShiftAI
from pace.python.sub_ais.interruption_recovery_ai import InterruptionRecoveryAI
from pace.python.pace_orchestrator import PacingAdaptationOrchestrator


def test_vocabulary_adaptation():
    ai = VocabularyAdaptationAI()

    # Prompt asks for simple terms
    p_simple = "Can you explain that in simple terms for a non-technical manager?"
    a_simple = "We keep a backup copy of our records so if one machine breaks, another machine takes over instantly."
    r_simple = ai.evaluate(p_simple, a_simple)
    assert r_simple["target_complexity"] == "SIMPLE"
    assert r_simple["is_adapted"]
    assert r_simple["compliance_score"] >= 0.85

    # Prompt asks for deep dive
    p_deep = "Give me a deep dive into the technical specifics of your replication protocol."
    a_deep = "We implemented Raft consensus with linearizability guarantees and backpressure on the network channels."
    r_deep = ai.evaluate(p_deep, a_deep)
    assert r_deep["target_complexity"] == "DEEP"
    assert r_deep["is_adapted"]
    assert r_deep["compliance_score"] >= 0.85


def test_response_length_calibration():
    ai = ResponseLengthCalibratorAI()

    p_brief = "In one sentence, what is the primary bottleneck?"
    a_brief = "The primary bottleneck was disk I/O serialization on the database leader node."
    r_brief = ai.evaluate(p_brief, a_brief)
    assert r_brief["length_target"] == "CONCISE"
    assert r_brief["is_calibrated"]
    assert r_brief["compliance_score"] >= 0.85


def test_register_shift():
    ai = RegisterShiftAI()

    p_formal = "Good morning. Furthermore, let us formally review the statutory compliance report."
    a_formal = "Good morning. In accordance with the governance guidelines, we have prepared the documentation."
    r_formal = ai.evaluate(p_formal, a_formal)
    assert r_formal["prompt_register"] == "FORMAL"
    assert r_formal["is_matched"]


def test_interruption_recovery():
    ai = InterruptionRecoveryAI()

    p_interrupt = "Hold on, let me interrupt you right there — let's pivot to your experience with Redis."
    a_composed = "Certainly, happy to pivot. With Redis, we configured sentinel replication clusters for sub-millisecond cache hits."
    r_comp = ai.evaluate(p_interrupt, a_composed)
    assert r_comp["was_interrupted"]
    assert r_comp["graceful_acknowledgement"]
    assert r_comp["is_composed"]
    assert not r_comp["is_defensive"]


def test_pace_orchestrator_and_zero_bridge_amsv():
    amsv_buf = bytearray(64)
    orch = PacingAdaptationOrchestrator(master_amsv_buffer=amsv_buf)

    p = "Briefly, in one sentence, what was your role?"
    a = "I was the lead backend engineer responsible for redesigning the consensus module."

    report = orch.evaluate_turn(p, a)
    assert report["adaptation_tier"] in ("SEAMLESS", "ADAPTIVE")
    assert report["adaptation_calibration_index"] >= 0.70

    # Check Zero-Bridge AMSV sync at offset 0x3E (<H: adaptation)
    adaptation_q16 = struct.unpack_from("<H", amsv_buf, 0x3E)[0]
    assert adaptation_q16 > 0
    assert abs(adaptation_q16 / 65535.0 - report["adaptation_calibration_index"]) < 0.01
