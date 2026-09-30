"""
test_all_engines_grading.py — Comprehensive Unit & Integration Tests for All 8 Engines & Master Grading.
"""

import struct
import pytest
from grading.master_candidate_grader import MasterCandidateGrader


def test_master_grader_strong_hire_candidate():
    amsv_buf = bytearray(64)
    grader = MasterCandidateGrader(master_amsv_buffer=amsv_buf)

    interviewer_prompt = (
        "Can you walk me through an instance where your distributed system suffered a cascade outage, "
        "and how you diagnosed and resolved the root cause?"
    )

    candidate_response = (
        "Building on your question regarding cascade outages, we were facing a severe latency cascade "
        "where database locks caused thread pool exhaustion across our microservices. "
        "In my experience as lead infrastructure engineer, my task was to isolate the root cause. "
        "I implemented Raft consensus across 5 nodes to maintain linearizability, replaced the relational queue "
        "with an in-memory ring buffer, and deployed circuit breakers with exponential backoff. "
        "Consequently, we reduced p99 latency by 45ms and achieved zero downtime under 100,000 req/s. "
        "I propose we standardize this bounded queue pattern for our future service architectures."
    )

    sc = grader.evaluate_turn(
        interviewer_prompt=interviewer_prompt,
        candidate_response=candidate_response,
        turn_number=1,
        latency_ms=1100.0,
        candidate_wpm=140.0,
        interviewer_wpm=135.0
    )

    assert sc["turn_number"] == 1
    assert sc["master_candidate_rating"] >= 65.0
    assert sc["verdict"] in ("STRONG HIRE", "HIRE")
    assert not sc["has_red_flags"]

    eg = sc["engine_grades"]
    assert "ALIE" in eg
    assert "ECSE" in eg
    assert "PMCE" in eg
    assert "HCTE" in eg
    assert "DCVE" in eg
    assert "NACE" in eg
    assert "LSCE" in eg
    assert "PACE" in eg

    # Verify report generation
    report = grader.generate_report(sc)
    assert "MASTER CANDIDATE EVALUATION" in report
    assert "Zero-Bridge AMSV Memory Verification" in report

    # Verify AMSV buffer has non-zero values written in-place
    assert any(b != 0 for b in amsv_buf)


def test_master_grader_weak_candidate_no_hire():
    amsv_buf = bytearray(64)
    grader = MasterCandidateGrader(master_amsv_buffer=amsv_buf)

    interviewer_prompt = "What was your approach to optimizing database throughput?"
    candidate_response = (
        "Um, you know, we basically used AI-driven synergy and next-gen cutting-edge cloud paradigms "
        "to make it blazing fast. It was somewhat better, I think maybe, something like that."
    )

    sc = grader.evaluate_turn(
        interviewer_prompt=interviewer_prompt,
        candidate_response=candidate_response,
        turn_number=1,
        latency_ms=3500.0
    )

    assert sc["master_candidate_rating"] < 60.0
    assert sc["verdict"] in ("LEAN HIRE", "NO HIRE")
