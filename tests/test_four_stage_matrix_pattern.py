"""
test_four_stage_matrix_pattern.py - Unit and Integration Tests for Reusable Four-Stage 6-Language Matrix Pattern.

Verifies:
1. Matrix Cell (M): All 6 technical lanes active (Rust, Python, C++, CUDA/Triton, Java, Julia).
2. Stage 1: Reserved Entry Boundary (contracts, quality rules, rejection boundaries).
3. Stage 2: Base Matrix <--> AI Model + Training (bidirectional state & feedback).
4. Stage 3: Connected Internal Groups (Group 3.1 2x2 -> Group 3.2 Central Hub -> Group 3.3 2x2 with cyclic refinement).
5. Stage 4: Verify, Learn, Analyze, Result (4.1 -> 4.2 -> 4.3 -> 4.4 -> out, with recursive feedback loop).
6. End-to-End Concrete Recruitment Verbal Engine with AMSV Offset 0x20 synchronization.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amsv.python.amsv_embedded import AMSVEmbeddedView
from four_stage_matrix.matrix_cell import SixLanguageMatrixCell
from four_stage_matrix.stage1_entry import ReservedEntryBoundary, RequirementContract
from four_stage_matrix.stage2_base_ai import BaseMatrixAIPair
from four_stage_matrix.stage3_connected_groups import TwoByTwoMatrixNetwork, ConnectedInternalGroups
from four_stage_matrix.stage4_execution_pipeline import VerifyLearnAnalyzePipeline
from four_stage_matrix.four_stage_engine import FourStageMatrixEngine, RecruitmentVerbalFourStageEngine


def test_matrix_cell_six_lanes():
    print("\n[1/6] Testing Six-Language Matrix Cell (M) across all 6 technical lanes...")
    amsv = AMSVEmbeddedView()
    cell = SixLanguageMatrixCell("TestMatrixCell", amsv)

    payload = "In my previous role, I architected a high-throughput lock-free ring buffer."
    result = cell.process_step(
        payload=payload,
        context={"requirement": "VerbalEvaluation", "session_id": "sess_101"},
        amsv_slot=0,
        amsv_val=0.88
    )

    assert result["matrix_cell"] == "TestMatrixCell"
    assert "lanes" in result

    # Check all 6 lanes exist and executed
    lanes = result["lanes"]
    assert "rust" in lanes
    assert "python" in lanes
    assert "cpp" in lanes
    assert "cuda_triton" in lanes
    assert "java" in lanes
    assert "julia" in lanes

    assert lanes["rust"]["lane"] == "Rust" and lanes["rust"]["is_memory_safe"] is True
    assert lanes["python"]["lane"] == "Python" and lanes["python"]["status"] == "ORCHESTRATED"
    assert lanes["cpp"]["lane"] == "C++" and lanes["cpp"]["lock_free_sync"] is True
    assert lanes["cuda_triton"]["lane"] == "CUDA/Triton"
    assert lanes["java"]["lane"] == "Java" and lanes["java"]["service_active"] is True
    assert lanes["julia"]["lane"] == "Julia" and lanes["julia"]["acoustic_entropy"] > 0.0

    assert result["composite_score"] > 0.60
    assert result["passed"] is True
    print(f"  [OK] Matrix Cell (M) verified across all 6 technical lanes (Composite: {result['composite_score']:.4f})")


def test_stage1_reserved_entry_boundary():
    print("\n[2/6] Testing Stage 1: Reserved Entry Boundary...")
    contract = RequirementContract(
        requirement_name="STAR_Evaluation",
        target_format_code=2,
        min_word_count=5,
        max_word_count=100
    )
    entry_gate = ReservedEntryBoundary(contract)

    # Valid input
    valid_res = entry_gate.validate_and_bind("During a major outage, I migrated the database seamlessly.")
    assert valid_res.is_valid is True
    assert len(valid_res.rejection_reasons) == 0

    # Invalid input (too short)
    short_res = entry_gate.validate_and_bind("Too short")
    assert short_res.is_valid is False
    assert any("violates bounds" in r for r in short_res.rejection_reasons)

    # Invalid input (null byte injection)
    bad_res = entry_gate.validate_and_bind("Malicious payload\x00corrupt")
    assert bad_res.is_valid is False
    assert any("null byte" in r for r in bad_res.rejection_reasons)
    print("  [OK] Stage 1 Reserved Entry Boundary enforces quality rules and contracts.")


def test_stage2_base_ai_pair():
    print("\n[3/6] Testing Stage 2: Base Matrix <--> AI Model + Training...")
    amsv = AMSVEmbeddedView()
    stage2 = BaseMatrixAIPair(amsv)

    payload = "When the system crashed, I coordinated incident triage and restored availability."
    res = stage2.execute_stage2(payload, {"domain": "Recruitment"})

    assert res["stage"] == 2
    assert "base_matrix_result" in res
    assert "ai_matrix_result" in res
    assert "shared_state" in res
    assert "feedback_gradient" in res
    assert res["stage2_composite"] > 0.60
    print(f"  [OK] Stage 2 Base <--> AI bidirectional state established (Composite: {res['stage2_composite']:.4f}, Gradient: {res['feedback_gradient']:.4f})")


def test_stage3_connected_internal_groups():
    print("\n[4/6] Testing Stage 3: Connected Internal Groups (3.1 [2x2] -> 3.2 [Hub] -> 3.3 [2x2])...")
    amsv = AMSVEmbeddedView()
    stage3 = ConnectedInternalGroups(amsv)

    payload = "We refactored the streaming bus to guarantee sequential ordering across distributed nodes."
    res = stage3.execute_stage3(payload, iterations=2)

    assert res["stage"] == 3
    assert "group_3_1" in res
    assert "central_hub_3_2" in res
    assert "group_3_3" in res
    assert len(res["cyclic_feedback_loop_history"]) == 2
    assert res["stage3_composite"] > 0.60
    assert res["cyclic_stability"] is True
    print(f"  [OK] Stage 3 2x2 Network -> Hub -> 2x2 Network verified with active cyclic feedback (Composite: {res['stage3_composite']:.4f})")


def test_stage4_verify_learn_analyze():
    print("\n[5/6] Testing Stage 4: Verify, Learn, Analyze, Result (4.1 -> 4.2 -> 4.3 -> 4.4 -> out)...")
    amsv = AMSVEmbeddedView()
    stage4 = VerifyLearnAnalyzePipeline(amsv)

    payload = "The candidate demonstrated deep architectural understanding and concise communication."
    stage3_dummy = {"stage3_composite": 0.82}
    res = stage4.execute_stage4(payload, stage3_dummy, max_feedback_passes=2)

    assert res["stage"] == 4
    assert res["box_4_1"]["passed"] is True
    assert res["box_4_2"]["passed"] is True
    assert res["box_4_3"]["passed"] is True
    assert res["box_4_4"]["passed"] is True
    assert len(res["recursive_feedback_history"]) == 2

    out_result = res["out_result"]
    assert out_result["status"] == "SUCCESS"
    assert out_result["quality_certified"] is True
    assert out_result["final_composite_score"] >= 0.70
    print(f"  [OK] Stage 4 Horizontal Pipeline synthesized final Result (Score: {out_result['final_composite_score']:.4f}, Status: {out_result['status']})")


def test_end_to_end_recruitment_verbal_four_stage_engine():
    print("\n[6/6] Testing End-to-End Recruitment Verbal Four-Stage Engine with AMSV Sync...")
    amsv = AMSVEmbeddedView()
    rvce_engine = RecruitmentVerbalFourStageEngine(amsv_view=amsv)

    star_transcript = (
        "During a critical payment gateway outage on Black Friday, I was tasked with incident command. "
        "I rapidly deployed a lock-free fallback settlement queue in C++20, which preserved $4.2M in "
        "transaction volume and restored normal operations within 90 seconds."
    )

    result = rvce_engine.evaluate_interview_turn(
        transcript=star_transcript,
        format_code=2, # Behavioral STAR
        turn_number=3,
        speech_wpm=142.0
    )

    assert result["status"] == "COMPLETED"
    assert result["global_four_stage_score"] >= 0.70

    # Verify physical write into AMSV Offset 0x20
    raw_state = amsv.get_scenario_state()
    format_code = raw_state & 0xFFFF
    turn_num = (raw_state >> 16) & 0xFFFF
    comp_q16 = (raw_state >> 32) & 0xFFFF
    phase = (raw_state >> 48) & 0xFFFF
    reg_comp = comp_q16 / 65535.0

    assert format_code == 2, f"Expected format 2, got {format_code}"
    assert turn_num == 3, f"Expected turn 3, got {turn_num}"
    assert phase == 2, f"Expected active phase 2, got {phase}"
    assert reg_comp >= 0.65, f"AMSV register compliance low: {reg_comp}"

    print(f"  [OK] End-to-End Four-Stage Engine verified (Score: {result['global_four_stage_score']:.4f}) | AMSV Offset 0x20 Synced (Format: {format_code}, Turn: {turn_num}, Q16: {reg_comp:.3f})")


if __name__ == "__main__":
    test_matrix_cell_six_lanes()
    test_stage1_reserved_entry_boundary()
    test_stage2_base_ai_pair()
    test_stage3_connected_internal_groups()
    test_stage4_verify_learn_analyze()
    test_end_to_end_recruitment_verbal_four_stage_engine()
    print("\n" + "=" * 80)
    print("  ALL 6 FOUR-STAGE 6-LANGUAGE MATRIX PATTERN TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)
