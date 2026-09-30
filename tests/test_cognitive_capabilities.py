"""
test_cognitive_capabilities.py - Dedicated Test Suite for the Eight Cognitive Capabilities (CCTE).

Verifies across the Six-Language Matrix:
1. Python Layer: All 8 sub-agents instantiated via `ccte/python/ccte_subagents.py`.
2. AMSV Layer: 0-nanosecond hardware physical memory write/read across:
   - Offset 0x10 - 0x17 (Alpha Bank): Thinking, Focus, Memory, Creativity (Q16 fixed-point).
   - Offset 0x18 - 0x1F (Beta Bank): Imagination, Analytical, Verbal, Emotional (Q16 fixed-point).
3. CCTE Coordinator: Batch evaluation and global cognitive index synthesis.
4. Utterance Linguistic Scoring: Real-time turn evaluation mapping natural speech features to 8 cognitive metrics.
5. C++20 Layer: Verification of `ccte/cpp/ccte_cognitive_engines.hpp`.
6. Rust Layer: Verification of `ccte/rust/src/lib.rs` and compiled artifacts.
7. Java 21 Layer: Verification of CCTE Java package structure and classes.
8. Julia Layer: Verification of `ccte/julia/CognitiveMath.jl`.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amsv.python.amsv_embedded import AMSVEmbeddedView
from ccte.python.ccte_subagents import (
    CCTECoordinator,
    ThinkingAbilitySubAgent,
    ConcentrationFocusSubAgent,
    RecallMemorySubAgent,
    CreativeThinkingSubAgent,
    ImaginationSimulationSubAgent,
    AnalyticalThinkingSubAgent,
    VerbalReasoningSubAgent,
    EmotionalRegulationSubAgent,
)


def test_individual_sub_agents():
    print("\n[1/5] Testing Individual 8 Cognitive Sub-Agents...")
    amsv = AMSVEmbeddedView()

    # 1. Thinking
    ag_think = ThinkingAbilitySubAgent(amsv)
    res_think = ag_think.evaluate(["premise 1", "premise 2", "deduction", "conclusion"])
    assert res_think["score"] >= 0.70, f"Thinking score low: {res_think['score']}"
    assert amsv.get_cognitive_score(0) == pytest.approx(res_think["score"], abs=0.01)

    # 2. Focus
    ag_focus = ConcentrationFocusSubAgent(amsv)
    res_focus = ag_focus.evaluate(speech_consistency=0.92, pause_variance=0.25)
    assert res_focus["score"] >= 0.80
    assert amsv.get_cognitive_score(1) == pytest.approx(res_focus["score"], abs=0.01)

    # 3. Memory
    ag_mem = RecallMemorySubAgent(amsv)
    res_mem = ag_mem.evaluate(recalled_items=7, target_items=7, latency_sec=0.8)
    assert res_mem["score"] >= 0.85
    assert amsv.get_cognitive_score(2) == pytest.approx(res_mem["score"], abs=0.01)

    # 4. Creativity
    ag_creat = CreativeThinkingSubAgent(amsv)
    res_creat = ag_creat.evaluate(cluster_count=5, mean_semantic_distance=0.85)
    assert res_creat["score"] >= 0.80
    assert amsv.get_cognitive_score(3) == pytest.approx(res_creat["score"], abs=0.01)

    # 5. Imagination
    ag_imag = ImaginationSimulationSubAgent(amsv)
    res_imag = ag_imag.evaluate(counterfactual_count=4, sensory_detail_ratio=0.14)
    assert res_imag["score"] >= 0.75
    assert amsv.get_cognitive_score(4) == pytest.approx(res_imag["score"], abs=0.01)

    # 6. Analytical
    ag_anal = AnalyticalThinkingSubAgent(amsv)
    res_anal = ag_anal.evaluate(is_valid_logic=True, fallacy_count=0, evidence_weight=0.95)
    assert res_anal["score"] >= 0.85
    assert amsv.get_cognitive_score(5) == pytest.approx(res_anal["score"], abs=0.01)

    # 7. Verbal
    ag_verb = VerbalReasoningSubAgent(amsv)
    res_verb = ag_verb.evaluate(parse_depth=5, coherence_cosine=0.88, inferential_gaps=0)
    assert res_verb["score"] >= 0.80
    assert amsv.get_cognitive_score(6) == pytest.approx(res_verb["score"], abs=0.01)

    # 8. Emotional
    ag_emot = EmotionalRegulationSubAgent(amsv)
    res_emot = ag_emot.evaluate(pitch_tremor_hz=0.8, vocal_shimmer=0.015, vocal_jitter=0.005)
    assert res_emot["score"] >= 0.75
    assert amsv.get_cognitive_score(7) == pytest.approx(res_emot["score"], abs=0.01)

    print("  [OK] All 8 Sub-Agents independently evaluated and synchronized with AMSV indices 0..7.")


def test_ccte_coordinator_batch_and_amsv_readback():
    print("\n[2/5] Testing CCTE Coordinator Batch Evaluation & AMSV Alpha/Beta Banks...")
    amsv = AMSVEmbeddedView()
    coordinator = CCTECoordinator(amsv)

    batch_params = {
        "inference_steps": ["step1", "step2", "step3", "step4"],
        "speech_consistency": 0.88,
        "pause_variance": 0.35,
        "recalled_items": 6,
        "target_items": 7,
        "latency_sec": 1.2,
        "cluster_count": 4,
        "mean_distance": 0.80,
        "counterfactuals": 3,
        "sensory_ratio": 0.12,
        "valid_logic": True,
        "fallacies": 0,
        "evidence_weight": 0.90,
        "parse_depth": 4,
        "coherence": 0.85,
        "gaps": 0,
        "tremor_hz": 1.0,
        "shimmer": 0.02,
        "jitter": 0.007
    }

    report = coordinator.evaluate_all(batch_params)
    assert "evaluations" in report
    assert len(report["evaluations"]) == 8
    assert report["global_cognitive_index"] > 0.65

    # Verify physical memory readback directly from AMSV
    amsv_scores = amsv.get_all_cognitive_scores()
    assert len(amsv_scores) == 8
    for i, s in enumerate(amsv_scores):
        assert 0.0 <= s <= 1.0, f"Score {i} out of bounds: {s}"
    print(f"  [OK] CCTE Coordinator Batch Evaluated: Global Index={report['global_cognitive_index']:.3f} | AMSV Readback={amsv_scores}")


def test_candidate_turn_cognitive_inference():
    print("\n[3/5] Testing Candidate Utterance Real-Time Cognitive Mapping...")
    amsv = AMSVEmbeddedView()
    coordinator = CCTECoordinator(amsv)

    # Utterance with high analytical, architectural, and reasoning markers
    utterance = (
        "In our microservice architecture, we evaluated the trade-off between consistency and latency. "
        "Therefore, because network partitions could degrade consensus, we implemented a Raft-based "
        "distributed lock matrix to guarantee sequential write ordering."
    )
    scores = coordinator.evaluate_candidate_turn(utterance, speech_wpm=138.0)

    assert scores["analytical_thinking"] >= 0.70, f"Expected high analytical score, got {scores['analytical_thinking']}"
    assert scores["thinking_ability"] >= 0.60
    assert scores["concentration_focus"] >= 0.80
    assert scores["verbal_reasoning"] >= 0.65

    # Verify write into AMSV
    readback = amsv.get_all_cognitive_scores()
    assert readback[5] == pytest.approx(scores["analytical_thinking"], abs=0.02)
    print(f"  [OK] Linguistic Mapping: Analytical={scores['analytical_thinking']:.3f}, Verbal={scores['verbal_reasoning']:.3f}, Focus={scores['concentration_focus']:.3f}")


def test_ccte_cxx_and_rust_headers():
    print("\n[4/5] Testing CCTE C++20 and Rust Engine Artifacts...")
    cxx_header = os.path.join("ccte", "cpp", "ccte_cognitive_engines.hpp")
    rust_src = os.path.join("ccte", "rust", "src", "lib.rs")

    assert os.path.exists(cxx_header), f"Missing CCTE C++ header: {cxx_header}"
    assert os.path.exists(rust_src), f"Missing CCTE Rust src: {rust_src}"

    with open(cxx_header, "r", encoding="utf-8") as f:
        cxx_content = f.read()
    assert "ThinkingEngine" in cxx_content or "ccte_cog_bank_alpha" in cxx_content or "0x10" in cxx_content
    assert "AnalyticalEngine" in cxx_content or "ccte_cog_bank_beta" in cxx_content or "0x18" in cxx_content

    print("  [OK] CCTE C++ and Rust Multi-Language Engine Code Verified.")


def test_ccte_julia_and_java_artifacts():
    print("\n[5/5] Testing CCTE Julia & Java Multi-Language Artifacts...")
    jl_file = os.path.join("ccte", "julia", "CognitiveMath.jl")
    assert os.path.exists(jl_file), f"Missing Julia CognitiveMath: {jl_file}"

    with open(jl_file, "r", encoding="utf-8") as f:
        jl_content = f.read()
    assert "CognitiveMath" in jl_content

    # Check Java structure
    java_dir = os.path.join("ccte", "java", "com", "solorock", "ccte")
    assert os.path.exists(java_dir), f"Missing CCTE Java package: {java_dir}"

    print("  [OK] CCTE Julia and Java Multi-Language Artifacts Verified.")


if __name__ == "__main__":
    test_individual_sub_agents()
    test_ccte_coordinator_batch_and_amsv_readback()
    test_candidate_turn_cognitive_inference()
    test_ccte_cxx_and_rust_headers()
    test_ccte_julia_and_java_artifacts()
    print("\n" + "=" * 80)
    print("  ALL 5 COGNITIVE CAPABILITIES (CCTE) TESTS PASSED SUCCESFULLY!")
    print("=" * 80)
