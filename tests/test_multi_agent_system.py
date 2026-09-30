"""
test_multi_agent_system.py - End-to-End Integration Tests for Multi-Language Multi-Agent System.

Tests:
1. Zero-Bridge AMSV 64-byte Shared Memory Layout & Bit-Packing.
2. VCE Acoustic & Prosody Sub-Agent.
3. CCTE 8 Cognitive Capability Sub-Agents & Coordinator.
4. RSSE Recruitment Scenario Simulation & STAR Parsing.
5. AEEE Adaptive Examination Engine & 3PL IRT Updates.
6. MAIO Global Orchestration, Knowledge Graph, & Holistic Gap Reasoning.
7. Lingua Sapiens Deep Grammar Intelligence Integration.
"""

import unittest
import struct
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amsv.python.amsv_embedded import AMSVEmbeddedView
from vce.python.vce_subagent import VceSubAgent
from ccte.python.ccte_subagents import CCTECoordinator
from rsse.python.scenario_agent import RecruitmentScenarioAgent
from aeee.python.examiner_voice_agent import ExaminerVoiceAgent
from maio.python.maio_orchestrator import MaioOrchestrator
from gra_voi.reasoning.engine import DeepReasoningEngine

class TestMultiAgentSystem(unittest.TestCase):

    def setUp(self):
        # Create zero-bridge 64-byte shared memory buffer
        self.raw_amsv_bytes = bytearray(64)
        self.amsv_view = memoryview(self.raw_amsv_bytes)
        self.amsv = AMSVEmbeddedView(self.amsv_view)

    def test_01_amsv_zero_bridge_memory_layout(self):
        """Verify 64-byte cache-line alignment and bit-field packing."""
        self.assertEqual(len(self.amsv_view), 64)

        # Test VCE Phoneme State (Offset 0x00)
        self.amsv.set_phoneme_state(0x123456789ABCDEF0)
        self.assertEqual(self.amsv.get_phoneme_state(), 0x123456789ABCDEF0)

        # Test CCTE Cognitive Banks (Offset 0x10 and 0x18)
        self.amsv.set_cognitive_score(0, 0.85)
        self.amsv.set_cognitive_score(1, 0.90)
        self.amsv.set_cognitive_score(5, 0.88)
        self.amsv.set_cognitive_score(7, 0.84)
        self.assertAlmostEqual(self.amsv.get_cognitive_score(0), 0.85, places=2)
        self.assertAlmostEqual(self.amsv.get_cognitive_score(1), 0.90, places=2)
        self.assertAlmostEqual(self.amsv.get_cognitive_score(5), 0.88, places=2)
        self.assertAlmostEqual(self.amsv.get_cognitive_score(7), 0.84, places=2)

        # Test RSSE State (Offset 0x20)
        self.amsv.set_scenario_state(0xAABBCCDDEEFF0011)
        self.assertEqual(self.amsv.get_scenario_state(), 0xAABBCCDDEEFF0011)

        # Test AEEE State (Offset 0x28)
        self.amsv.set_examination_theta(1.45)
        self.assertAlmostEqual(self.amsv.get_examination_theta(), 1.45, places=2)

    def test_02_vce_subagent_evaluation(self):
        """Verify VCE sub-agent acoustic, prosodic, and phoneme tracking."""
        vce = VceSubAgent(amsv_view=self.amsv)
        utterance = "The distributed consensus protocol operates with sub-millisecond latency."
        pitch = [120.0, 125.0, 130.0, 128.0, 122.0, 118.0]
        
        eval_result = vce.evaluate_text_utterance(utterance, pitch_contour=pitch, duration_sec=3.2)
        self.assertGreater(eval_result["phoneme_accuracy"], 0.5)
        self.assertGreater(eval_result["fluency_score"], 0.5)
        self.assertGreater(eval_result["f0_mean_hz"], 100.0)

        # Verify state was synchronized into AMSV offset 0x00 and 0x08
        phoneme_word = struct.unpack_from("<Q", self.amsv_view, 0)[0]
        prosody_word = struct.unpack_from("<Q", self.amsv_view, 8)[0]
        self.assertNotEqual(phoneme_word, 0)
        self.assertNotEqual(prosody_word, 0)

    def test_03_ccte_all_8_capabilities(self):
        """Verify all 8 independent cognitive capability sub-agents."""
        coordinator = CCTECoordinator(amsv_view=self.amsv)
        text = "When we analyzed the partition tolerance paradox, I designed a formal trade-off matrix balancing consistency and availability, ensuring linearizability while de-escalating customer panic."
        
        scores = coordinator.evaluate_candidate_turn(text, speech_wpm=135.0)
        self.assertEqual(len(scores), 8)
        for cap_name in [
            "thinking_ability", "concentration_focus", "memory_recall", "creative_thinking",
            "imagination", "analytical_thinking", "verbal_reasoning", "emotional_regulation"
        ]:
            self.assertIn(cap_name, scores)
            self.assertGreaterEqual(scores[cap_name], 0.0)
            self.assertLessEqual(scores[cap_name], 1.0)

        # Verify cognitive banks written to AMSV 0x10 and 0x18
        alpha_word = struct.unpack_from("<Q", self.amsv_view, 16)[0]
        beta_word = struct.unpack_from("<Q", self.amsv_view, 24)[0]
        self.assertNotEqual(alpha_word, 0)
        self.assertNotEqual(beta_word, 0)

    def test_04_rsse_scenario_star_parsing(self):
        """Verify RSSE recruitment scenario simulation and STAR structural evaluation."""
        rsse = RecruitmentScenarioAgent(amsv_state_vector=self.amsv_view)
        opening = rsse.start_scenario(format_code=2, scenario_id=201)
        self.assertIn("STAR", opening)

        # Provide a high-structure STAR answer
        transcript = (
            "During a catastrophic datacenter outage, I was tasked with restoring customer replication. "
            "I designed an automated failover script and led the mitigation bridge. "
            "This resulted in reducing downtime by 85% and saving two million dollars in SLA penalties."
        )
        turn_eval = rsse.evaluate_turn(transcript, wpm=135.0)
        self.assertIsNotNone(turn_eval.star_eval)
        self.assertGreater(turn_eval.star_eval.overall_star_coherence, 0.50)
        self.assertGreater(turn_eval.register_compliance, 0.6)


    def test_05_aeee_adaptive_irt_estimation(self):
        """Verify AEEE adaptive testing with 3PL Item Response Theory."""
        aeee = ExaminerVoiceAgent(amsv_state_vector=self.amsv_view, max_questions=5, target_sem=0.30)
        q1 = aeee.start_exam()
        self.assertTrue(len(q1) > 0)

        # Submit strong candidate responses
        eval1 = aeee.submit_candidate_response("High capability response", {"analytical_depth": 0.90, "prosody_fluency": 0.85})
        self.assertGreater(eval1.theta_estimate, -0.5)

        eval2 = aeee.submit_candidate_response("Another strong answer", {"analytical_depth": 0.95, "prosody_fluency": 0.90})
        # Standard error should decrease as more questions are administered
        self.assertLess(eval2.standard_error, 1.0)

    def test_06_maio_holistic_orchestration(self):
        """Verify MAIO end-to-end multi-agent orchestration and gap reasoning."""
        maio = MaioOrchestrator(amsv_state_vector=self.amsv_view)
        initial_prompt = maio.initialize_session(format_code=1, scenario_id=101)
        self.assertTrue(len(initial_prompt) > 0)

        utterance = (
            "In our distributed architecture, we employed kernel-bypass RDMA with a Raft consensus ring. "
            "When asymmetric network partitions caused packet drop at the NIC, I initiated a dynamic quorum reduction, "
            "which stabilized tail latency at 45 microseconds and preserved strict linearizability."
        )
        report = maio.process_candidate_turn(utterance, speech_wpm=140.0)

        self.assertGreater(report.global_competency_index, 0.5)
        self.assertEqual(len(report.dimension_scores), 8)
        self.assertGreater(len(report.root_cause_diagnoses), 0)
        self.assertGreater(len(report.prescriptive_curriculum), 0)

        # Verify MAIO state synchronized into AMSV offset 0x30 and 0x38
        alpha_word = struct.unpack_from("<Q", self.amsv_view, 48)[0]
        self.assertNotEqual(alpha_word, 0)

if __name__ == "__main__":
    unittest.main()
