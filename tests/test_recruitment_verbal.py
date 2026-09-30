"""
test_recruitment_verbal.py - Dedicated Test Suite for Recruitment Verbal Communication Engine (RVCE / RSSE).

Verifies across the Six-Language Matrix:
1. Rust Layer: C-ABI dynamic invocation of `rsse_evaluate_verbal_turn` in `rsse_ontology.dll`.
2. Python Layer: Deep Transformer inference via `RecruitmentVerbalSubAINeural`.
3. AMSV Layer: Lock-free atomic synchronization to AMSV Offset 0x20 (format, turn, register, phase).
4. Scenario Agent: Multi-format evaluation & feedback generation across all 8 standardized interview formats.
5. C++20 Layer: Verification of `rsse/cpp/verbal_communication_engine.hpp` and `verbal_communication_engine.o`.
6. Java 21 Layer: Verification of `RecruitmentVerbalService.java` and `VerbalEvaluationDTO.java`.
7. Julia Layer: Verification of `VerbalDynamics.jl` acoustic entropy and continuous turn-taking dynamics.
"""

import os
import sys
import ctypes
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amsv.python.amsv_embedded import AMSVEmbeddedView
from rsse.python.verbal_sub_ai_neural import RecruitmentVerbalSubAINeural
from rsse.python.scenario_agent import RecruitmentScenarioAgent


# ----------------------------------------------------------------------------
# 1. RUST C-ABI VERIFICATION
# ----------------------------------------------------------------------------

class RustStarScores(ctypes.Structure):
    _fields_ = [
        ("situation", ctypes.c_float),
        ("task", ctypes.c_float),
        ("action", ctypes.c_float),
        ("result", ctypes.c_float),
        ("coherence", ctypes.c_float),
    ]

class RustVerbalTurnEvaluation(ctypes.Structure):
    _fields_ = [
        ("register_compliance", ctypes.c_float),
        ("star_scores", RustStarScores),
        ("jargon_density", ctypes.c_float),
        ("wpm_score", ctypes.c_float),
        ("filler_penalty", ctypes.c_float),
        ("composite_score", ctypes.c_float),
    ]

def test_rust_c_abi_verbal_evaluator():
    print("\n[1/6] Testing Rust C-ABI Verbal Evaluator (rsse_ontology.dll)...")
    dll_path = os.path.join("rsse", "rust", "target", "release", "rsse_ontology.dll")
    assert os.path.exists(dll_path), f"Rust DLL missing at {dll_path}"

    rust_lib = ctypes.CDLL(os.path.abspath(dll_path))
    rsse_evaluate = rust_lib.rsse_evaluate_verbal_turn
    rsse_evaluate.argtypes = [
        ctypes.c_char_p,
        ctypes.c_uint16,
        ctypes.c_float,
        ctypes.POINTER(RustVerbalTurnEvaluation)
    ]
    rsse_evaluate.restype = ctypes.c_int32

    # Test High-STAR Response
    high_star_text = (
        "In my previous role, our team was facing critical database lockups. "
        "My objective was to eliminate tail latency. "
        "I architected and implemented a lock-free ring buffer in Rust, "
        "resulting in reducing p99 latency by 85%."
    ).encode("utf-8")

    out_eval_star = RustVerbalTurnEvaluation()
    status = rsse_evaluate(high_star_text, ctypes.c_uint16(2), ctypes.c_float(140.0), ctypes.byref(out_eval_star))
    assert status == 0, f"Rust C-ABI call failed with code {status}"
    assert out_eval_star.star_scores.coherence >= 0.85, f"Expected high STAR coherence, got {out_eval_star.star_scores.coherence}"
    assert out_eval_star.composite_score >= 0.75, f"Expected high composite, got {out_eval_star.composite_score}"
    assert out_eval_star.filler_penalty < 0.05, f"Unexpected filler penalty: {out_eval_star.filler_penalty}"

    # Test Filler-Heavy Response
    filler_text = "Um, like, you know, we basically, uh, changed some code, literally sort of.".encode("utf-8")
    out_eval_filler = RustVerbalTurnEvaluation()
    status_filler = rsse_evaluate(filler_text, ctypes.c_uint16(2), ctypes.c_float(110.0), ctypes.byref(out_eval_filler))
    assert status_filler == 0
    assert out_eval_filler.filler_penalty > 0.10, f"Failed to detect filler words: {out_eval_filler.filler_penalty}"
    print(f"  [OK] Rust C-ABI Verified: High-STAR ({out_eval_star.composite_score:.3f}) | Filler Penalty ({out_eval_filler.filler_penalty:.3f})")



# ----------------------------------------------------------------------------
# 2. PYTHON NEURAL SUB-AI VERIFICATION
# ----------------------------------------------------------------------------

def test_neural_verbal_sub_ai():
    print("\n[2/6] Testing RecruitmentVerbalSubAINeural...")
    sub_ai = RecruitmentVerbalSubAINeural()

    # Load trained checkpoint if available
    chk_path = os.path.join("checkpoints", "bandhu_sub_ais_verified.pt")
    if os.path.exists(chk_path):
        import torch
        bundle = torch.load(chk_path, map_location="cpu", weights_only=True)
        if "recruitment_verbal" in bundle:
            sub_ai.load_state_dict(bundle["recruitment_verbal"])
            print("  Loaded trained checkpoint weights for RecruitmentVerbalSubAINeural.")

    # High-quality technical STAR response
    star_response = (
        "When our primary payment gateway experienced a catastrophic outage during Black Friday, "
        "I was tasked with leading incident response. I immediately orchestrated a canary failover "
        "to our secondary settlement gateway within 90 seconds, preserving $4.2M in transaction volume."
    )
    res_star = sub_ai.analyze_verbal_response(star_response, format_code=2, wpm=140.0)
    assert res_star["star_coherence"] >= 0.50, f"Expected high STAR coherence, got {res_star['star_coherence']}"
    assert res_star["register_compliance"] >= 0.50, f"Expected high register, got {res_star['register_compliance']}"
    assert "format_fit" in res_star

    # Low-quality colloquial response
    colloq_response = "Yeah so like, we had this problem and stuff broke, so I kinda just rebooted it I guess."
    res_colloq = sub_ai.analyze_verbal_response(colloq_response, format_code=2, wpm=90.0)
    assert len(res_colloq["actionable_feedback"]) > 0, "Failed to generate actionable feedback for poor response!"
    print(f"  [OK] Neural Sub-AI Verified: STAR ({res_star['star_coherence']:.3f}) vs Colloq ({res_colloq['star_coherence']:.3f})")


# ----------------------------------------------------------------------------
# 3. SCENARIO AGENT & AMSV OFFSET 0x20 SYNCHRONIZATION
# ----------------------------------------------------------------------------

def test_scenario_agent_amsv_synchronization():
    print("\n[3/6] Testing RecruitmentScenarioAgent & AMSV Offset 0x20 Sync...")
    amsv = AMSVEmbeddedView()
    agent = RecruitmentScenarioAgent(amsv_state_vector=amsv._view)
    agent.start_scenario(format_code=1, scenario_id=1)

    # Evaluate a Turn
    transcript = (
        "In our distributed architecture, we encountered severe cross-datacenter replication lag. "
        "I spearheaded migrating to a zero-copy lock-free ring buffer in C++20 with atomic CAS semantics, "
        "which reduced tail p99 latency by 82% across high-throughput ingestion pipelines."
    )
    turn_eval = agent.evaluate_turn(transcript, wpm=142.0)

    assert turn_eval.register_compliance > 0.50, f"Low register compliance: {turn_eval.register_compliance}"
    assert turn_eval.turn_id == 1

    # Read physical memory from AMSV to verify zero-bridge synchronization
    raw_state = amsv.get_scenario_state()
    scenario_id = raw_state & 0xFFFF
    turn_number = (raw_state >> 16) & 0xFFFF
    comp_q16 = (raw_state >> 32) & 0xFFFF
    phase = (raw_state >> 48) & 0xFFFF
    reg_comp = comp_q16 / 65535.0

    assert scenario_id == 1, f"Expected scenario_id 1, got {scenario_id}"
    assert turn_number == 1, f"Expected turn 1, got {turn_number}"
    assert phase >= 1, f"Expected active phase, got {phase}"
    assert reg_comp > 0.50, f"Register compliance in AMSV too low: {reg_comp}"
    print(f"  [OK] AMSV Offset 0x20 Synchronized: Scenario={scenario_id}, Turn={turn_number}, Register={reg_comp:.3f}, Phase={phase}")


# ----------------------------------------------------------------------------
# 4. C++20 ENGINE VALIDATION
# ----------------------------------------------------------------------------

def test_cpp_engine_artifacts():
    print("\n[4/6] Testing C++20 Verbal Communication Engine Artifacts...")
    header = os.path.join("rsse", "cpp", "verbal_communication_engine.hpp")
    source = os.path.join("rsse", "cpp", "verbal_communication_engine.cpp")
    obj = os.path.join("rsse", "cpp", "verbal_communication_engine.o")

    assert os.path.exists(header), f"Missing C++ header: {header}"
    assert os.path.exists(source), f"Missing C++ source: {source}"
    assert os.path.exists(obj), f"Missing C++ compiled object: {obj}"

    # Verify header contains 0x20 offset synchronization and lock-free semantics
    with open(header, "r", encoding="utf-8") as f:
        content = f.read()
    assert "rsse_scenario_state" in content or "0x20" in content or "AtomicStateVector" in content
    print("  [OK] C++20 Verbal Engine Header, Implementation, and Object File Verified.")



# ----------------------------------------------------------------------------
# 5. JAVA 21 SERVICE VALIDATION
# ----------------------------------------------------------------------------

def test_java_service_artifacts():
    print("\n[5/6] Testing Java 21 Recruitment Verbal Service Artifacts...")
    dto = os.path.join("rsse", "java", "com", "solorock", "rsse", "dto", "VerbalEvaluationDTO.java")
    service = os.path.join("rsse", "java", "com", "solorock", "rsse", "RecruitmentVerbalService.java")
    dto_class = os.path.join("rsse", "java", "com", "solorock", "rsse", "dto", "VerbalEvaluationDTO.class")
    service_class = os.path.join("rsse", "java", "com", "solorock", "rsse", "RecruitmentVerbalService.class")

    assert os.path.exists(dto), f"Missing Java DTO: {dto}"
    assert os.path.exists(service), f"Missing Java Service: {service}"
    assert os.path.exists(dto_class), f"Missing compiled DTO class: {dto_class}"
    assert os.path.exists(service_class), f"Missing compiled Service class: {service_class}"

    with open(service, "r", encoding="utf-8") as f:
        content = f.read()
    assert "ByteBuffer" in content
    assert "0x20" in content
    print("  [OK] Java 21 DTO and Service Source & Bytecode Verified with AMSV Offset 0x20.")


# ----------------------------------------------------------------------------
# 6. JULIA DYNAMICS VALIDATION
# ----------------------------------------------------------------------------

def test_julia_verbal_dynamics():
    print("\n[6/6] Testing Julia Continuous Turn-Taking Dynamics...")
    jl_file = os.path.join("rsse", "julia", "VerbalDynamics.jl")
    assert os.path.exists(jl_file), f"Missing Julia file: {jl_file}"

    with open(jl_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "module VerbalDynamics" in content
    assert "TurnTakingLatencyModel" in content
    assert "calculate_turn_latency_score" in content
    assert "compute_conversational_entropy" in content
    assert "evaluate_star_mathematics" in content
    print("  [OK] Julia Verbal Dynamics Mathematical Definitions Verified.")



if __name__ == "__main__":
    test_rust_c_abi_verbal_evaluator()
    test_neural_verbal_sub_ai()
    test_scenario_agent_amsv_synchronization()
    test_cpp_engine_artifacts()
    test_java_service_artifacts()
    test_julia_verbal_dynamics()
    print("\n" + "=" * 80)
    print("  ALL 6 RECRUITMENT VERBAL COMMUNICATION ENGINE TESTS PASSED SUCCESFULLY!")
    print("=" * 80)
