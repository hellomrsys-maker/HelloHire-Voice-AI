"""
test_grammar_parallel_cores.py - Comprehensive Verification for Grammar Engines x 6 Languages Matrix.

Tests:
1. Engine A (Written Grammar): 6 language sub-cores + Engine A Synthesis + AMSV Offset 0x30.
2. Engine B (Verbal Communication): 6 language sub-cores + Engine B Synthesis + AMSV Offset 0x20.
3. Engine C (Phonology Voice): 6 language sub-cores + Engine C Synthesis + AMSV Offset 0x00-0x0F.
4. Engine D (Cognitive Examination): 6 language sub-cores + Engine D Synthesis + AMSV Offset 0x10-0x1F & 0x28-0x2F.
5. Linguistic Drive Core: Attention routing & AMSV Offset 0x38-0x3F.
6. Master Grammar Synthesis Core: Global Competency Index & multi-engine fusion.
7. End-to-End Orchestrator: 24 sub-cores + 4 synthesizers + Drive + Master + 4-Stage Matrix.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amsv.python.amsv_embedded import AMSVEmbeddedView
from grammar_parallel_cores.engine_a_written_grammar.synthesis.engine_a_synthesis import EngineAWrittenGrammarSynthesis
from grammar_parallel_cores.engine_b_verbal_communication.synthesis.engine_b_synthesis import EngineBVerbalCommunicationSynthesis
from grammar_parallel_cores.engine_c_phonology_voice.synthesis.engine_c_synthesis import EngineCPhonologyVoiceSynthesis
from grammar_parallel_cores.engine_d_cognitive_examination.synthesis.engine_d_synthesis import EngineDCognitiveExaminationSynthesis
from grammar_parallel_cores.drive_core.linguistic_drive_core import LinguisticDriveCore
from grammar_parallel_cores.master_synthesis.master_grammar_synthesis import MasterGrammarSynthesisCore
from grammar_parallel_cores.grammar_cores_orchestrator import GrammarParallelCoresOrchestrator


class TestGrammarParallelCores(unittest.TestCase):

    def setUp(self):
        self.amsv = AMSVEmbeddedView()

    def test_engine_a_written_grammar_six_subcores(self):
        """Verify Engine A executes all 6 sub-cores and synchronizes to AMSV Offset 0x30."""
        engine_a = EngineAWrittenGrammarSynthesis(self.amsv)
        sample_text = (
            "Because the syntactic structure was deeply hierarchical, "
            "the comparative grammar typology established universal invariants across branches."
        )
        res = engine_a.execute_all_subcores(sample_text)

        self.assertEqual(res["engine"], "Engine_A_Written_Grammar")
        self.assertGreater(res["engine_composite_score"], 0.0)
        self.assertLessEqual(res["engine_composite_score"], 1.0)

        # Verify all 6 sub-cores are present and executed
        subcores = res["subcores"]
        self.assertIn("A1_Rust", subcores)
        self.assertIn("A2_Python", subcores)
        self.assertIn("A3_CPP", subcores)
        self.assertIn("A4_CUDA", subcores)
        self.assertIn("A5_Java", subcores)
        self.assertIn("A6_Julia", subcores)

        self.assertTrue(subcores["A1_Rust"]["is_memory_safe"])
        self.assertGreater(subcores["A2_Python"]["written_rule_composite"], 0.0)
        self.assertEqual(subcores["A3_CPP"]["sub_core"], "A3_CPP")

        # Zero-bridge AMSV readback check
        struct_score = self.amsv.get_global_structural_score()
        reg_score = self.amsv.get_global_register_score()
        self.assertGreater(struct_score, 0.0)
        self.assertGreater(reg_score, 0.0)

    def test_engine_b_verbal_communication_six_subcores(self):
        """Verify Engine B executes all 6 sub-cores and synchronizes to AMSV Offset 0x20."""
        engine_b = EngineBVerbalCommunicationSynthesis(self.amsv)
        transcript = (
            "In my previous leadership role, our team faced a severe throughput bottleneck. "
            "I restructured the communication pipeline using synchronous protocols, resulting in a 40% performance gain."
        )
        res = engine_b.execute_all_subcores(transcript=transcript, turn_number=2, scenario_id=3)

        self.assertEqual(res["engine"], "Engine_B_Verbal_Communication")
        self.assertGreater(res["engine_composite_score"], 0.0)
        self.assertLessEqual(res["engine_composite_score"], 1.0)

        subcores = res["subcores"]
        self.assertIn("B1_Rust", subcores)
        self.assertIn("B2_Python", subcores)
        self.assertIn("B3_CPP", subcores)
        self.assertIn("B4_CUDA", subcores)
        self.assertIn("B5_Java", subcores)
        self.assertIn("B6_Julia", subcores)

        self.assertTrue(subcores["B1_Rust"]["is_memory_safe"])
        self.assertGreater(subcores["B2_Python"]["verbal_neural_composite"], 0.0)

        # Zero-bridge AMSV readback check (verbal reasoning score at 0x1C)
        verbal_score = self.amsv.get_cognitive_score(6)
        self.assertGreater(verbal_score, 0.0)

    def test_engine_c_phonology_voice_six_subcores(self):
        """Verify Engine C executes all 6 sub-cores and synchronizes to AMSV Offset 0x00-0x0F."""
        engine_c = EngineCPhonologyVoiceSynthesis(self.amsv)
        phonemes = "k ax m p j uw t ey sh ax n ax l l ih ng g w ih s t ih k s"
        res = engine_c.execute_all_subcores(phonemes)

        self.assertEqual(res["engine"], "Engine_C_Phonology_Voice")
        self.assertGreater(res["engine_composite_score"], 0.0)
        self.assertLessEqual(res["engine_composite_score"], 1.0)

        subcores = res["subcores"]
        self.assertIn("C1_Rust", subcores)
        self.assertIn("C2_Python", subcores)
        self.assertIn("C3_CPP", subcores)
        self.assertIn("C4_CUDA", subcores)
        self.assertIn("C5_Java", subcores)
        self.assertIn("C6_Julia", subcores)

        # Zero-bridge AMSV readback check
        art_acc = self.amsv.get_phoneme_accuracy()
        fluency = self.amsv.get_prosody_fluency()
        self.assertGreater(art_acc, 0.0)
        self.assertGreater(fluency, 0.0)

    def test_engine_d_cognitive_examination_six_subcores(self):
        """Verify Engine D executes all 6 sub-cores and synchronizes to AMSV Offsets 0x10-0x1F & 0x28-0x2F."""
        engine_d = EngineDCognitiveExaminationSynthesis(self.amsv)
        candidate_input = (
            "If we hypothesize that ergative-absolutive alignment emerged as an economical marking strategy "
            "in intransitive clauses, we can deduce cross-linguistic morphosyntactic retention."
        )
        res = engine_d.execute_all_subcores(candidate_input, question_idx=3)

        self.assertEqual(res["engine"], "Engine_D_Cognitive_Examination")
        self.assertGreater(res["engine_composite_score"], 0.0)
        self.assertLessEqual(res["engine_composite_score"], 1.0)

        subcores = res["subcores"]
        self.assertIn("D1_Rust", subcores)
        self.assertIn("D2_Python", subcores)
        self.assertIn("D3_CPP", subcores)
        self.assertIn("D4_CUDA", subcores)
        self.assertIn("D5_Java", subcores)
        self.assertIn("D6_Julia", subcores)

        # Zero-bridge AMSV readback check
        thinking = self.amsv.get_cognitive_score(0)
        theta = self.amsv.get_examination_theta()
        sem = self.amsv.get_examination_sem()
        self.assertGreater(thinking, 0.0)
        self.assertGreaterEqual(theta, -4.0)
        self.assertLessEqual(theta, 4.0)
        self.assertGreater(sem, 0.0)

    def test_linguistic_drive_core(self):
        """Verify Linguistic Drive Core calculates motive force and attention weights."""
        drive = LinguisticDriveCore(self.amsv)
        res = drive.evaluate_drive_state(user_intent="VERBAL_INTERVIEW")

        self.assertEqual(res["core"], "Linguistic_Drive_Core")
        weights = res["engine_weights"]
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=2)
        self.assertGreater(weights["engine_b"], weights["engine_a"])

    def test_master_grammar_synthesis(self):
        """Verify Master AI Synthesis Core aggregates all engines and generates GCI."""
        master = MasterGrammarSynthesisCore(self.amsv)
        dummy_a = {"engine_composite_score": 0.85}
        dummy_b = {"engine_composite_score": 0.80}
        dummy_c = {"engine_composite_score": 0.90}
        dummy_d = {"engine_composite_score": 0.75}
        dummy_drive = {"engine_weights": {"engine_a": 0.25, "engine_b": 0.25, "engine_c": 0.25, "engine_d": 0.25}}

        res = master.synthesize(dummy_a, dummy_b, dummy_c, dummy_d, dummy_drive)
        self.assertEqual(res["core"], "Master_Grammar_Synthesis_Core")
        self.assertGreaterEqual(res["global_competency_index"], 0.80)
        self.assertIsInstance(res["pedagogical_recommendations"], list)

    def test_end_to_end_orchestrator(self):
        """Verify the full 24-core parallel execution through the Four-Stage Matrix."""
        orchestrator = GrammarParallelCoresOrchestrator(self.amsv)
        text = (
            "We systematically evaluated the morphological case systems across Indo-European and Afro-Asiatic. "
            "Our empirical findings demonstrate significant structural retention."
        )
        res = orchestrator.execute_parallel_workflow(
            text_payload=text,
            turn_number=1,
            user_intent="BALANCED_MASTERY"
        )

        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["total_engines"], 4)
        self.assertEqual(res["total_subcores_executed"], 24)
        self.assertIn("linguistic_drive_core", res)
        self.assertIn("engines", res)
        self.assertIn("master_grammar_synthesis", res)
        self.assertIn("four_stage_matrix_pipeline", res)
        self.assertEqual(res["four_stage_matrix_pipeline"]["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
