"""
test_dcve.py — Comprehensive Unit & Integration Tests for DCVE (Domain Competence Verbal Engine).
"""

import struct
import pytest
from dcve.python.sub_ais.jargon_vs_depth_ai import JargonVsDepthAI
from dcve.python.sub_ais.conceptual_precision_ai import ConceptualPrecisionAI
from dcve.python.sub_ais.domain_track_classifier_ai import DomainTrackClassifierAI
from dcve.python.sub_ais.ontology_grounding_ai import OntologyGroundingAI
from dcve.python.dcve_orchestrator import DomainCompetenceVerbalOrchestrator


def test_jargon_vs_depth_empty_and_buzzwords():
    ai = JargonVsDepthAI()
    res_empty = ai.evaluate("")
    assert res_empty["depth_score"] <= 0.40
    assert not res_empty["is_substantive"]

    res_buzz = ai.evaluate("We leverage synergistic next-gen paradigm shifts to create seamless AI-driven disruption.")
    assert res_buzz["buzzword_count"] >= 3
    assert res_buzz["substance_count"] == 0
    assert res_buzz["depth_score"] < 0.45


def test_jargon_vs_depth_high_substance():
    ai = JargonVsDepthAI()
    text = (
        "We achieved linearizability by deploying a Raft consensus cluster with bounded queues "
        "and zero-copy memory-mapped write-ahead logs to minimize p99 tail latency."
    )
    res = ai.evaluate(text)
    assert res["substance_count"] >= 4
    assert res["depth_score"] >= 0.70
    assert res["is_substantive"]


def test_conceptual_precision():
    ai = ConceptualPrecisionAI()

    vague_text = "It was basically a lot of users and it got somewhat faster."
    res_vague = ai.evaluate(vague_text)
    assert res_vague["vague_qualifier_count"] >= 2
    assert res_vague["precision_score"] < 0.35

    precise_text = (
        "We reduced p99 latency from 450ms to 32ms by replacing the relational query with an in-memory B-tree index, "
        "consequently handling 50,000 req/s at 15% CPU."
    )
    res_precise = ai.evaluate(precise_text)
    assert res_precise["quantifier_count"] >= 2
    assert res_precise["causal_link_count"] >= 1
    assert res_precise["precision_score"] >= 0.70
    assert res_precise["is_quantitatively_grounded"]


def test_domain_track_classifier():
    ai = DomainTrackClassifierAI()

    eng_text = "Our microservices architecture utilizes distributed caching, asynchronous pipelines, and low latency queues."
    res_eng = ai.evaluate(eng_text)
    assert res_eng["primary_track"] == "ENGINEERING"
    assert res_eng["track_id"] == 1
    assert res_eng["confidence"] >= 0.50

    fin_text = "The DCF valuation models were calibrated based on EBITDA margins, WACC estimates, and liquidity reserves."
    res_fin = ai.evaluate(fin_text)
    assert res_fin["primary_track"] == "FINANCE"
    assert res_fin["track_id"] == 2


def test_ontology_grounding():
    ai = OntologyGroundingAI()

    valid_text = "We configured Kafka topic partitions to ensure strict ordering while Redis cache provides in-memory retrieval."
    res_valid = ai.evaluate(valid_text)
    assert res_valid["valid_relations_count"] >= 2
    assert res_valid["mismatch_count"] == 0
    assert res_valid["is_grounded"]
    assert res_valid["ontology_grounding_score"] >= 0.60

    mismatch_text = "We wrote our Kafka CSS styles to run inside a stethoscope."
    res_mismatch = ai.evaluate(mismatch_text)
    assert res_mismatch["mismatch_count"] >= 1
    assert not res_mismatch["is_grounded"]


def test_dcve_orchestrator_and_zero_bridge_amsv():
    amsv_buf = bytearray(64)
    orch = DomainCompetenceVerbalOrchestrator(master_amsv_buffer=amsv_buf)

    high_comp_text = (
        "In our distributed system, we implemented Raft consensus across 5 nodes to maintain "
        "linearizability. We reduced p99 latency by 35ms through zero-copy ring buffers, "
        "consequently sustaining 100,000 req/s. We ensured Kafka topic partitions maintain strict event ordering."
    )
    report = orch.evaluate(high_comp_text)

    assert report["competence_tier"] in ("EXPERT", "PROFICIENT")
    assert report["primary_track"] == "ENGINEERING"
    assert report["domain_competence_index"] >= 0.65

    # Check Zero-Bridge AMSV sync at offset 0x30 (<HH: depth, precision)
    depth_q16, prec_q16 = struct.unpack_from("<HH", amsv_buf, 0x30)
    assert depth_q16 > 0
    assert prec_q16 > 0
    assert abs(depth_q16 / 65535.0 - report["depth_score"]) < 0.01
