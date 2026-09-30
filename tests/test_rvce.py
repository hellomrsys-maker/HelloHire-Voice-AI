"""
test_rvce.py - Unit and Integration Tests for Recruitment Verbal Cognitive Engine (RVCE)

Tests:
1. ThinkingSubAI (MECE, First-Principles, STAR, Deduction)
2. ConcentrationSubAI (Pacing, Cognitive Endurance, SNR)
3. RecallSubAI (Working Memory, Consistency, Resume Fidelity)
4. CreativitySubAI (Divergence, Conceptual Novelty, Lateral Transfer)
5. ImaginationSubAI (Counterfactual, Prospective, Theory of Mind)
6. VerbalSubAI (WPM cadence, Register, Filler Mitigation)
7. RecruitmentVerbalCognitiveOrchestrator (Turn execution & Scorecard)
8. Zero-Bridge AMSV Memory Synchronization (Offsets 0x10, 0x18, 0x20)
9. C++ RVCE Core C-ABI (librvce_core.dll)
10. Rust Stream Processor and Fast Cognitive Metrics
11. GPU / Triton Cognitive Tensor Scoring
12. PyTorch Multi-Task Cognitive Training Step
"""

import os
import sys
import ctypes
import struct
import pytest
import torch

from rvce.python.sub_ais.thinking_sub_ai import ThinkingSubAI
from rvce.python.sub_ais.concentration_sub_ai import ConcentrationSubAI
from rvce.python.sub_ais.recall_sub_ai import RecallSubAI
from rvce.python.sub_ais.creativity_sub_ai import CreativitySubAI
from rvce.python.sub_ais.imagination_sub_ai import ImaginationSubAI
from rvce.python.sub_ais.verbal_sub_ai import VerbalSubAI
from rvce.python.rvce_orchestrator import RecruitmentVerbalCognitiveOrchestrator
from rvce.gpu.rvce_triton import run_rvce_gpu_scoring
from training.train_rvce_cognitive_ai import (
    RVCECognitiveNetwork,
    RVCETrainer,
    generate_synthetic_recruitment_batch
)

class TestRVCECognitiveFaculties:

    def test_thinking_sub_ai(self):
        ai = ThinkingSubAI()
        transcript = (
            "Firstly, the root cause was memory contention because the lock-free queue had high cache invalidation. "
            "In my previous role, our team was facing 10x traffic. The goal was to eliminate tail latency. "
            "I implemented a partitioned atomic buffer, resulting in a 45% reduction in p99 latency."
        )
        res = ai.evaluate(transcript)
        assert res["reasoning_depth"] >= 3
        assert res["first_principles_score"] > 0.4
        assert res["mece_score"] > 0.5
        assert res["star_coherence"] >= 0.8
        assert res["composite_score"] > 0.6

    def test_concentration_sub_ai(self):
        ai = ConcentrationSubAI()
        res = ai.evaluate(measured_wpm=145.0, elapsed_minutes=15.0, turn_number=5, filler_penalty=0.04)
        assert res["pace_stability"] >= 0.95
        assert res["endurance_factor"] > 0.8
        assert res["distraction_resistance"] > 0.7
        assert res["cognitive_snr_db"] > 20.0
        assert res["composite_score"] > 0.7

    def test_recall_sub_ai(self):
        ai = RecallSubAI()
        history = [
            "We initially selected PostgreSQL for ACID transaction integrity.",
            "Our latency budget was strictly 20 milliseconds."
        ]
        curr = "As mentioned regarding PostgreSQL, we maintained the ACID guarantees within the 20 milliseconds budget."
        res = ai.evaluate(curr, history, claimed_resume_entities=["PostgreSQL", "ACID"])
        assert res["working_memory_retention"] > 0.5
        assert res["cross_turn_consistency"] >= 0.9
        assert res["resume_fidelity"] >= 0.9
        assert res["composite_score"] > 0.7

    def test_creativity_sub_ai(self):
        ai = CreativitySubAI()
        transcript = (
            "Instead of standard scaling, we took a novel orthogonal approach. We used an unconventional "
            "analogous mechanism akin to biological immune systems to synthesize a self-healing re-architected cluster."
        )
        res = ai.evaluate(transcript)
        assert res["divergent_thinking_score"] > 0.7
        assert res["conceptual_novelty_score"] > 0.7
        assert res["lateral_synthesis_score"] > 0.7
        assert res["metaphoric_richness"] >= 0.85
        assert res["composite_score"] > 0.7

    def test_imagination_sub_ai(self):
        ai = ImaginationSubAI()
        transcript = (
            "What if we face 100M queries next year? Projecting forward, from the customer's perspective, "
            "sub-millisecond responsiveness will determine retention. Had we chosen a naive cache, we would fail to scale."
        )
        res = ai.evaluate(transcript)
        assert res["counterfactual_score"] >= 0.9
        assert res["prospective_forecasting_score"] >= 0.9
        assert res["theory_of_mind_score"] >= 0.9
        assert res["vision_clarity"] >= 0.9
        assert res["composite_score"] > 0.8

    def test_verbal_sub_ai(self):
        ai = VerbalSubAI()
        transcript = (
            "We optimized the distributed consensus protocol by pipelining raft log entries and applying "
            "asynchronous batching to minimize network roundtrips."
        )
        res = ai.evaluate(transcript, measured_wpm=148.0)
        assert res["wpm_score"] == 1.0
        assert res["register_compliance"] == 1.0
        assert res["filler_penalty"] == 0.0
        assert res["type_token_ratio"] > 0.7
        assert res["composite_score"] > 0.7

    def test_rvce_orchestrator_pipeline(self):
        master_buffer = bytearray(64)
        orch = RecruitmentVerbalCognitiveOrchestrator(master_amsv_buffer=master_buffer)
        t1 = (
            "Firstly, in my previous role our objective was to scale data streaming. "
            "I designed an out of the box orthogonal pipeline, anticipating future growth. "
            "Resulting in 3x throughput improvement without lock contention."
        )
        report = orch.evaluate_turn(t1, turn_number=1, measured_wpm=145.0, elapsed_minutes=5.0)

        assert report["composite_hireability"] > 0.65
        assert report["recommendation_code"] in [1, 2] # Strong Hire or Hire
        assert len(orch.conversation_history) == 1

        # Verify Zero-Bridge AMSV writes directly to buffer
        # ccte_cog_bank_alpha at 0x10: [Thinking, Focus, Recall, Creativity]
        q_think, q_focus, q_recal, q_creat = struct.unpack_from("<HHHH", master_buffer, 0x10)
        assert q_think > 0
        assert q_focus > 0
        assert q_recal > 0
        assert q_creat > 0

        # ccte_cog_bank_beta at 0x18: [Imagination, Analytical, Verbal, Composure]
        q_imagi, q_analy, q_verba, q_emoti = struct.unpack_from("<HHHH", master_buffer, 0x18)
        assert q_imagi > 0
        assert q_verba > 0

        # rsse_scenario_state at 0x20: [ScenarioID, Turn, Score, RecCode]
        sc_id, turn, q_comp, rec_code = struct.unpack_from("<HHHH", master_buffer, 0x20)
        assert sc_id == 202
        assert turn == 1
        assert q_comp > 0
        assert rec_code in [1, 2]

    def test_rvce_cpp_core_c_abi(self):
        dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rvce", "cpp", "librvce_core.dll"))
        if not os.path.exists(dll_path):
            pytest.skip("librvce_core.dll not compiled on this platform")

        lib = ctypes.CDLL(dll_path, winmode=0) if sys.platform == "win32" else ctypes.CDLL(dll_path)

        class ThinkingStruct(ctypes.Structure):
            _fields_ = [
                ("reasoning_depth", ctypes.c_int),
                ("first_principles_score", ctypes.c_float),
                ("mece_structuring_score", ctypes.c_float),
                ("star_coherence", ctypes.c_float),
                ("deductive_validity", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class ConcentrationStruct(ctypes.Structure):
            _fields_ = [
                ("sustained_attention_sec", ctypes.c_float),
                ("distraction_resistance", ctypes.c_float),
                ("cognitive_endurance_factor", ctypes.c_float),
                ("noise_suppression_snr_db", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class RecallStruct(ctypes.Structure):
            _fields_ = [
                ("working_memory_retention", ctypes.c_float),
                ("cross_turn_consistency", ctypes.c_float),
                ("resume_fact_fidelity", ctypes.c_float),
                ("retrieval_latency_ms", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class CreativityStruct(ctypes.Structure):
            _fields_ = [
                ("divergent_thinking_score", ctypes.c_float),
                ("conceptual_distance_novelty", ctypes.c_float),
                ("lateral_solution_synthesis", ctypes.c_float),
                ("metaphoric_richness", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class ImaginationStruct(ctypes.Structure):
            _fields_ = [
                ("counterfactual_simulation", ctypes.c_float),
                ("prospective_forecasting", ctypes.c_float),
                ("theory_of_mind_empathy", ctypes.c_float),
                ("vision_articulation_clarity", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class VerbalStruct(ctypes.Structure):
            _fields_ = [
                ("fluency_wpm_score", ctypes.c_float),
                ("register_compliance", ctypes.c_float),
                ("vocabulary_density", ctypes.c_float),
                ("filler_penalty", ctypes.c_float),
                ("composite_score", ctypes.c_float),
            ]

        class ScorecardStruct(ctypes.Structure):
            _fields_ = [
                ("thinking", ThinkingStruct),
                ("concentration", ConcentrationStruct),
                ("recall", RecallStruct),
                ("creativity", CreativityStruct),
                ("imagination", ImaginationStruct),
                ("verbal", VerbalStruct),
                ("global_hireability_index", ctypes.c_float),
                ("recommendation_code", ctypes.c_uint16),
            ]

        lib.rvce_cpp_evaluate_turn.argtypes = [
            ctypes.c_char_p, ctypes.c_float, ctypes.c_float, ctypes.c_uint16, ctypes.POINTER(ScorecardStruct)
        ]
        lib.rvce_cpp_evaluate_turn.restype = ctypes.c_int32

        scorecard = ScorecardStruct()
        transcript = b"Because of the fundamental bottleneck, I took action to re-architect our data pipeline, resulting in 50% speedup."
        status = lib.rvce_cpp_evaluate_turn(transcript, ctypes.c_float(145.0), ctypes.c_float(10.0), ctypes.c_uint16(1), ctypes.byref(scorecard))

        assert status == 0
        assert scorecard.global_hireability_index > 0.5
        assert scorecard.recommendation_code in [1, 2, 3]

    def test_rvce_rust_shared_library(self):
        dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rvce", "rust", "target", "release", "rvce_stream_processor.dll"))
        if not os.path.exists(dll_path):
            pytest.skip("rvce_stream_processor.dll not compiled on this platform")

        lib = ctypes.CDLL(dll_path)

        class RustSummary(ctypes.Structure):
            _fields_ = [
                ("total_words", ctypes.c_uint32),
                ("unique_words", ctypes.c_uint32),
                ("ttr", ctypes.c_float),
                ("filler_ratio", ctypes.c_float),
                ("pace_wpm", ctypes.c_float),
                ("star_score", ctypes.c_float),
                ("composite_hireability", ctypes.c_float),
            ]

        lib.rvce_rust_analyze_transcript.argtypes = [
            ctypes.c_char_p, ctypes.c_float, ctypes.c_uint16, ctypes.POINTER(RustSummary)
        ]
        lib.rvce_rust_analyze_transcript.restype = ctypes.c_int32

        summary = RustSummary()
        text = b"In my previous role the task was to scale our cluster. I implemented a novel caching layer resulting in reduced latency."
        ret = lib.rvce_rust_analyze_transcript(text, ctypes.c_float(30.0), ctypes.c_uint16(1), ctypes.byref(summary))

        assert ret == 0
        assert summary.total_words > 10
        assert summary.unique_words > 8
        assert summary.ttr > 0.6
        assert summary.composite_hireability > 0.4

    def test_gpu_scoring(self):
        batch_size = 4
        d_model = 64
        cands = torch.randn(batch_size, d_model)
        rubrics = torch.randn(6, d_model)

        scores = run_rvce_gpu_scoring(cands, rubrics)
        assert scores.shape == (batch_size, 6)
        assert torch.all(scores >= 0.0)
        assert torch.all(scores <= 1.0)

    def test_neural_training_step(self):
        amsv_buf = bytearray(64)
        trainer = RVCETrainer(amsv_buffer=amsv_buf)
        tokens, targets = generate_synthetic_recruitment_batch(batch_size=4, seq_len=16)

        initial_loss = None
        for step in range(3):
            metrics = trainer.train_step(tokens, targets)
            if initial_loss is None:
                initial_loss = metrics["total_loss"]

        assert "total_loss" in metrics
        # Verify AMSV was updated during training
        q_think, q_focus, q_recal, q_creat = struct.unpack_from("<HHHH", amsv_buf, 0x10)
        assert q_think > 0
        assert q_focus > 0
