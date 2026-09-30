"""
test_candidate_grading_flow.py — End-to-end tests for the Master Candidate Grading Flow.
"""

import pytest
from grading.master_candidate_grader import MasterCandidateGrader
from grading.run_candidate_grading import BENCHMARK_INTERVIEWS, grade_interview_scenario


def test_principal_architect_benchmark_grading():
    amsv = bytearray(64)
    grader = MasterCandidateGrader(master_amsv_buffer=amsv)
    scenario = BENCHMARK_INTERVIEWS["principal"]

    scorecards = grade_interview_scenario(grader, "principal_test", scenario)
    assert len(scorecards) == 3

    # Turn 1 should show high domain competence and strong structure
    t1 = scorecards[0]
    assert t1["engine_grades"]["DCVE"]["grade"] in (1, 2)
    assert t1["engine_grades"]["LSCE"]["grade"] == 1
    assert t1["engine_grades"]["PACE"]["grade"] == 1
    assert not t1["has_red_flags"]

    # Verify AMSV buffer has been mutated in-place
    assert any(b != 0 for b in amsv)


def test_bluffing_candidate_triggers_red_flag_no_hire():
    amsv = bytearray(64)
    grader = MasterCandidateGrader(master_amsv_buffer=amsv)
    scenario = BENCHMARK_INTERVIEWS["bluffing"]

    scorecards = grade_interview_scenario(grader, "bluffing_test", scenario)
    assert len(scorecards) == 2

    # Turn 2 has a direct contradiction about Redis reliability
    t2 = scorecards[1]
    assert t2["has_red_flags"] is True
    assert t2["verdict"] == "NO HIRE"
    assert t2["verdict_grade"] == 4


def test_borderline_candidate_grading():
    amsv = bytearray(64)
    grader = MasterCandidateGrader(master_amsv_buffer=amsv)
    scenario = BENCHMARK_INTERVIEWS["borderline"]

    scorecards = grade_interview_scenario(grader, "borderline_test", scenario)
    assert len(scorecards) == 2

    # Borderline junior has shallow technical substance
    avg_mcr = sum(s["master_candidate_rating"] for s in scorecards) / 2
    assert avg_mcr < 65.0
