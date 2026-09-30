"""
test_nace.py — Comprehensive Unit & Integration Tests for NACE (Narrative Arc & Coherence Engine).
"""

import struct
import pytest
from nace.python.sub_ais.contradiction_detector_ai import ContradictionDetectorAI
from nace.python.sub_ais.theme_consistency_ai import ThemeConsistencyAI
from nace.python.sub_ais.narrative_climax_ai import NarrativeClimaxAI
from nace.python.sub_ais.arc_momentum_ai import ArcMomentumAI
from nace.python.nace_orchestrator import NarrativeArcCoherenceOrchestrator


def test_contradiction_detector():
    ai = ContradictionDetectorAI()

    t1 = ai.evaluate(1, "I managed a team of 5 engineers building our backend.")
    assert not t1["has_contradictions"]
    assert t1["coherence_score"] == 1.0

    t2 = ai.evaluate(2, "We delivered the project in 3 years with zero downtime.")
    assert not t2["has_contradictions"]

    # Blatant contradiction in team size: 5 -> 35
    t3 = ai.evaluate(3, "As the manager leading a team of 35 people, we worked hard.")
    assert t3["has_contradictions"]
    assert t3["contradiction_penalty"] > 0
    assert t3["coherence_score"] < 1.0


def test_theme_consistency():
    ai = ThemeConsistencyAI()

    ai.evaluate("We redesigned our distributed database architecture to optimize query latency.")
    ai.evaluate("Our backend infrastructure handles high throughput and scalability challenges.")
    res = ai.evaluate("Our distributed storage clusters ensure reliability and concurrency control.")

    assert res["dominant_theme"] == "systems_infrastructure"
    assert res["theme_stability_score"] >= 0.80
    assert res["is_stable"]


def test_narrative_climax_star():
    ai = NarrativeClimaxAI()

    star_text = (
        "We were facing a major outage occurred because of legacy database locks. "
        "My role was to lead the emergency remediation. "
        "I implemented an asynchronous lock-free queue and migrated the hot tables. "
        "As a result, we achieved zero downtime and improved throughput by 45%."
    )
    res = ai.evaluate(star_text)
    assert res["has_star_structure"]
    assert res["has_quantifiable_outcome"]
    assert res["climax_score"] >= 0.80


def test_arc_momentum():
    ai = ArcMomentumAI()

    rambling = "Um, you know, like I said, going back to what I mentioned before, and stuff like that."
    res_rambling = ai.evaluate(rambling)
    assert res_rambling["stagnation_markers_count"] >= 3
    assert res_rambling["momentum_score"] < 0.40

    driven = "First, we analyzed the root cause. Next, we prototyped the solution. Finally, to summarize, we deployed."
    res_driven = ai.evaluate(driven)
    assert res_driven["forward_transitions_count"] >= 3
    assert res_driven["has_forward_drive"]


def test_nace_orchestrator_and_zero_bridge_amsv():
    amsv_buf = bytearray(64)
    orch = NarrativeArcCoherenceOrchestrator(master_amsv_buffer=amsv_buf)

    t1_text = (
        "We were facing critical latency spikes. My goal was to stabilize the backend. "
        "I implemented a distributed cache. As a result, we reduced p99 latency by 50%."
    )
    r1 = orch.evaluate_turn(1, t1_text)
    assert r1["narrative_coherence_index"] >= 0.65
    assert not r1["has_contradictions"]

    # Check Zero-Bridge AMSV sync at offset 0x34
    coherence_q16, climax_q16 = struct.unpack_from("<HH", amsv_buf, 0x34)
    assert coherence_q16 > 0
    assert climax_q16 > 0
    assert abs(coherence_q16 / 65535.0 - r1["coherence_score"]) < 0.01
