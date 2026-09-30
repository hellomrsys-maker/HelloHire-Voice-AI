"""
test_lsce.py — Comprehensive Unit & Integration Tests for LSCE (Long-Short Cognitive Endurance Engine).
"""

import struct
import pytest
from lsce.python.sub_ais.fatigue_trajectory_ai import FatigueTrajectoryAI
from lsce.python.sub_ais.lexical_diversity_drift_ai import LexicalDiversityDriftAI
from lsce.python.sub_ais.concentration_resilience_ai import ConcentrationResilienceAI
from lsce.python.sub_ais.endurance_recovery_ai import EnduranceRecoveryAI
from lsce.python.lsce_orchestrator import CognitiveEnduranceOrchestrator


def test_fatigue_trajectory_steady_vs_decay():
    ai = FatigueTrajectoryAI()

    # Turn 1: 50 words
    r1 = ai.evaluate("Word " * 50)
    assert not r1["is_fatiguing"]
    assert r1["stamina_score"] == 1.0

    # Turn 2: 45 words
    ai.evaluate("Word " * 45)
    # Turn 3: 10 words (severe collapse)
    r3 = ai.evaluate("Word " * 10)
    assert r3["trajectory_slope"] < 0


def test_lexical_diversity_drift():
    ai = LexicalDiversityDriftAI()

    rich_text = "The Byzantine consensus protocol guarantees fault tolerance under asynchronous network partitions."
    r_rich = ai.evaluate(rich_text)
    assert r_rich["is_lexically_rich"]
    assert r_rich["lexical_richness"] >= 0.70

    flat_text = "it was good and it was very good and good"
    r_flat = ai.evaluate(flat_text)
    assert r_flat["current_ttr"] < 0.70


def test_concentration_resilience():
    ai = ConcentrationResilienceAI()

    q = "Can you explain how you designed the sharding architecture, and how you handled cross-shard transactions?"
    a_detailed = (
        "First, regarding the sharding architecture, we partitioned by user hash into 64 virtual buckets. "
        "Second, to answer your question about cross-shard transactions, we utilized a two-phase commit protocol "
        "with bounded timeout recovery to avoid distributed deadlocks."
    )
    res = ai.evaluate(q, a_detailed)
    assert res["sub_prompts_detected"] >= 2
    assert res["structured_marker_count"] >= 2
    assert res["has_high_resilience"]


def test_endurance_recovery():
    ai = EnduranceRecoveryAI()

    r1 = ai.evaluate(0.40)  # low turn
    r2 = ai.evaluate(0.85)  # sharp recovery
    assert r2["has_recovered"]
    assert r2["recovery_score"] >= 0.80


def test_lsce_orchestrator_and_zero_bridge_amsv():
    amsv_buf = bytearray(64)
    orch = CognitiveEnduranceOrchestrator(master_amsv_buffer=amsv_buf)

    q = "What was the most challenging bug you resolved, and what steps did you take?"
    a = (
        "First, we faced a memory leak under high concurrency. "
        "Second, I isolated the issue using flame graphs and memory dumps, "
        "identifying an unbounded queue in our logger. We replaced it with a ring buffer."
    )

    report = orch.evaluate_turn(q, a, turn_quality_hint=0.85)
    assert report["stamina_tier"] in ("IRONCLAD", "RESILIENT")
    assert report["endurance_index"] >= 0.60

    # Check Zero-Bridge AMSV sync at offset 0x3C (<H: stamina)
    stamina_q16 = struct.unpack_from("<H", amsv_buf, 0x3C)[0]
    assert stamina_q16 > 0
    assert abs(stamina_q16 / 65535.0 - report["stamina_score"]) < 0.01
