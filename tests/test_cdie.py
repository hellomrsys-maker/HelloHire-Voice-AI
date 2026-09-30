"""
test_cdie.py — Test Suite for Cross-Domain Idea Transfer Engine (CDIE).
"""

import pytest
from cdie.python.cdie_orchestrator import CrossDomainIdeaTransferOrchestrator
from cdie.python.sub_ais.cross_domain_analogies_ai import CrossDomainAnalogiesAI
from cdie.python.sub_ais.interdisciplinary_bridge_ai import InterdisciplinaryBridgeAI
from cdie.python.sub_ais.lateral_concept_mapper_ai import LateralConceptMapperAI
from cdie.python.sub_ais.conceptual_distance_ai import ConceptualDistanceAI


def test_cross_domain_analogy_detected():
    ai = CrossDomainAnalogiesAI()
    text = (
        "Much like how biological DNA uses redundant cellular proofreading to prevent genetic mutation, "
        "our distributed database architecture employs cryptographic checksums across nodes to ensure latency-free integrity."
    )
    r = ai.evaluate(text)
    assert r["has_cross_domain_bridge"] is True
    assert "biology" in r["domains_detected"]
    assert "software" in r["domains_detected"]
    assert r["composite_score"] >= 0.70


def test_interdisciplinary_synthesis():
    ai = InterdisciplinaryBridgeAI()
    text = (
        "We executed a first-principles translation by borrowing the paradigm from thermodynamics, "
        "because the underlying event stream shares the exact same dynamic of entropy dissipation."
    )
    r = ai.evaluate(text)
    assert r["bridge_cues_found"] >= 1
    assert r["causal_grounding_hits"] >= 1
    assert r["synthesis_depth"] >= 0.60


def test_lateral_concept_mapper():
    ai = LateralConceptMapperAI()
    text = (
        "Instead of brute-forcing or throwing more hardware at it, we used an orthogonal approach: "
        "we inverted the problem and reframed the constraint using a lock-free ring buffer."
    )
    r = ai.evaluate(text)
    assert r["lateral_cues"] >= 2
    assert r["lateral_inventiveness"] >= 0.70


def test_conceptual_distance():
    ai = ConceptualDistanceAI()
    r = ai.evaluate(["biology", "software"], has_causal_link=True)
    assert r["manifold_distance"] == 0.85
    assert r["composite_score"] == 0.85


def test_cdie_orchestrator_visionary_grade():
    buf = bytearray(64)
    orc = CrossDomainIdeaTransferOrchestrator(master_amsv_buffer=buf, amsv_offset=0x38)
    text = (
        "Much like how immune T-cells identify foreign antigens, our intrusion detection engine "
        "maps anomalous payload vectors using an orthogonal approach to bypass traditional firewall bottlenecks. "
        "We borrowed the paradigm from evolutionary biology because the underlying threat vectors share the same adaptation dynamic."
    )
    res = orc.evaluate(text)
    assert res["cross_domain_transfer_index"] >= 0.70
    assert res["transfer_grade"] in (1, 2)
    assert res["has_cross_domain_bridge"] is True

    # Check AMSV buffer mutation
    assert any(b != 0 for b in buf)
