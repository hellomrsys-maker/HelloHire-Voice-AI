"""
Comprehensive Test Suite for Lingua Sapiens (gra_voi).
Exercises all 12 core components and 4 proactive architectural enhancements.
"""

import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gra_voi.orchestrator import UniversalGrammarAI
from gra_voi.common.models import (
    WordOrder,
    SentenceType,
    WritingFormat,
    ErrorCategory,
)


class TestLinguaSapiens(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ai = UniversalGrammarAI()

    def test_component_1_deep_thinking(self):
        trace = self.ai.think("I saw the astronomer with binoculars.", context="Looking at the night sky")
        self.assertIsNotNone(trace)
        self.assertTrue(len(trace.step_by_step_thought_chain) >= 5)
        self.assertTrue(len(trace.ambiguities_detected) >= 1)
        self.assertIsNotNone(trace.selected_interpretation)
        self.assertIn("PP_HIGH_ATTACHMENT_INSTRUMENT", [a.interpretation_id for a in trace.ambiguities_detected])

    def test_component_2_universal_grammar_kb(self):
        noun_concept = self.ai.query_grammar("Noun")
        self.assertIsNotNone(noun_concept)
        self.assertEqual(noun_concept.name, "Noun")
        self.assertTrue(len(noun_concept.annotated_examples) >= 2)

        principles = self.ai.get_universal_principles()
        self.assertIn("Structure Dependency", principles)
        self.assertIn("Binding Theory", principles)

    def test_component_3_sentence_syntax(self):
        # 1. Parse
        analysis = self.ai.analyze_sentence("The diligent student solved the equation in the laboratory.")
        self.assertEqual(analysis.sentence_type, SentenceType.SIMPLE)
        self.assertEqual(analysis.word_order_typology, WordOrder.SVO)
        self.assertTrue(len(analysis.constituents) >= 3)

        # 2. Synthesis across typologies
        syn_sov = self.ai.construct_sentence(
            subject="The cat",
            verb="caught",
            direct_object="the mouse",
            word_order=WordOrder.SOV
        )
        self.assertEqual(syn_sov["word_order"], "SOV")
        self.assertEqual(syn_sov["sentence"], "The cat the mouse caught.")

        # 3. Transformation
        trans = self.ai.transform_sentence("The cat caught the mouse", "active_to_passive")
        self.assertIn("was caught by", trans["transformed_sentence"].lower())

    def test_component_4_writing_skill(self):
        model_doc = self.ai.generate_writing_model(WritingFormat.ESSAY_ARGUMENTATIVE, "Artificial Intelligence Ethics")
        self.assertIn("ARGUMENTATIVE ESSAY", model_doc)
        self.assertIn("PEEL", model_doc)

        critique = self.ai.critique_writing(
            "Language is an essential instrument of human thought. Furthermore, complex syntax enables nuanced reasoning. Consequently, linguistic mastery is vital."
        )
        self.assertTrue(critique.overall_score > 70.0)
        self.assertTrue(len(critique.strengths) >= 1)

    def test_component_5_error_detection_and_correction(self):
        bad_text = "The list of participants were published, and he don't care because their going to arrive on monday."
        result = self.ai.correct_text(bad_text)
        self.assertTrue(len(result.errors) >= 3)
        self.assertIn("was", result.corrected_text)
        self.assertIn("doesn't", result.corrected_text)
        self.assertIn("they're", result.corrected_text)
        self.assertTrue(len(result.step_by_step_reasoning) >= 3)

    def test_component_6_phonology_and_pronunciation(self):
        # Stress shift check
        noun_res = self.ai.analyze_pronunciation("record", grammatical_role="noun")
        verb_res = self.ai.analyze_pronunciation("record", grammatical_role="verb")
        self.assertIn("ˈrɛk", noun_res.ipa)
        self.assertIn("rɪˈkɔːrd", verb_res.ipa)
        self.assertTrue(len(noun_res.grammatical_stress_shift_note) > 0)

        # Connected speech
        conn_res = self.ai.analyze_pronunciation("did you drink water")
        self.assertTrue(len(conn_res.connected_speech_effects) >= 1)

    def test_component_7_reading_comprehension(self):
        passage = (
            "Although early linguists hypothesized that grammar was learned purely through associative conditioning, "
            "Noam Chomsky demonstrated that human language acquisition requires an innate universal grammar. "
            "He showed that children acquire intricate syntactic rules despite poverty of the stimulus."
        )
        analysis = self.ai.analyze_reading_passage(passage)
        self.assertTrue(len(analysis.sentence_breakdowns) == 2)
        self.assertTrue(len(analysis.guided_comprehension_exercises) >= 2)
        self.assertTrue(len(analysis.anaphora_reference_chains) >= 1)

    def test_component_8_spoken_language(self):
        transcript = "Well, um, that book, I loved it, you know, but my friend, he said it was too dense."
        analysis = self.ai.analyze_spoken_discourse(transcript)
        self.assertTrue(len(analysis.detected_disfluencies) >= 2)
        self.assertTrue(len(analysis.discourse_markers) >= 1)
        self.assertTrue(len(analysis.spoken_grammatical_structures) >= 1)
        self.assertNotIn("um", analysis.cleaned_canonical_syntax)

    def test_component_9_multilingual_and_contrastive(self):
        contrast = self.ai.compare_languages("Spanish", "English")
        self.assertIn("Null-Subject Transfer Risk", "".join(contrast.negative_interference_risks))
        self.assertTrue(len(contrast.positive_transfer_factors) >= 1)

        prof = self.ai.get_language_profile("Mandarin")
        self.assertIsNotNone(prof)
        self.assertTrue(prof.is_tonal)
        self.assertEqual(prof.family, "Sino-Tibetan")

    def test_component_10_creativity_and_style_transfer(self):
        sonnet = self.ai.generate_creative("sonnet", "The architecture of universal grammar")
        self.assertEqual(sonnet.genre, "sonnet")
        self.assertTrue(len(sonnet.devices_applied) >= 3)
        self.assertIn("Iambic Pentameter", sonnet.metrical_and_rhythmic_notes)

        transfer = self.ai.transfer_style("We found out that the test worked really well.", "academic")
        self.assertIn("Empirical investigation", transfer.transferred_text)
        self.assertTrue(len(transfer.semantic_invariants_preserved) >= 1)

    def test_component_11_assessment_and_learner_progress(self):
        quiz = self.ai.create_quiz(cefr_level="B1", topic="General Grammar")
        self.assertEqual(quiz.target_cefr_level, "B1")
        self.assertTrue(len(quiz.questions) >= 1)

        # Submit answers
        q1 = quiz.questions[0]
        report = self.ai.evaluate_quiz("learner_001", quiz, {q1.question_id: q1.correct_answer})
        self.assertGreaterEqual(report.score_percentage, 0.0)
        self.assertTrue(len(report.personalized_roadmap) >= 1)

    def test_component_12_educational_compendium(self):
        full_doc = self.ai.generate_educational_compendium()
        self.assertIn("LINGUA SAPIENS", full_doc)
        self.assertIn("Chapter 1:", full_doc)
        self.assertIn("Chapter 10:", full_doc)
        self.assertGreater(len(full_doc.split()), 2500)

    def test_enhancement_1_pragmatics(self):
        prag = self.ai.analyze_pragmatics("Could you please pass the salt?")
        self.assertIn("Directive", prag.illocutionary_force)
        self.assertIn("Negative Politeness", prag.politeness_strategy)
        self.assertIn("Indirect Directive", prag.conversational_implicature)

    def test_enhancement_2_discourse(self):
        disc = self.ai.analyze_discourse(
            "The experiment validated the initial thesis. Consequently, the team expanded funding for Phase 2."
        )
        self.assertTrue(len(disc.cohesion_ties) >= 1)
        self.assertTrue(len(disc.rst_relations) >= 1)

    def test_enhancement_3_diachronic(self):
        dia = self.ai.analyze_diachronic_evolution("strong verbs")
        self.assertIn("Ablaut", dia.target_item_or_pattern)
        self.assertTrue(len(dia.phonological_sound_laws) >= 1)

    def test_enhancement_4_sla(self):
        sla = self.ai.diagnose_sla(["Subject-Verb Agreement violation", "Article omission"], l1="Spanish", l2="English")
        self.assertIn("Mesolect", sla.interlanguage_stage)
        self.assertTrue(len(sla.neurolinguistic_remediation_regimen) >= 3)

    def test_zero_bridge_amsv_synchronization(self):
        # Verify 64-byte direct memory representation
        self.assertEqual(len(self.ai.amsv.raw_bytes()), 64)

        # Trigger operations that write to AMSV
        self.ai.think("The quantum computer executed the Shor factorization algorithm.")
        cog_scores = self.ai.amsv.get_all_cognitive_scores()
        self.assertGreater(cog_scores[0], 0.0) # Thinking score updated
        self.assertGreater(cog_scores[2], 0.0) # Memory score updated

        self.ai.analyze_pronunciation("record", grammatical_role="noun")
        self.assertNotEqual(self.ai.amsv.get_phoneme_state(), 0)
        self.assertNotEqual(self.ai.amsv.get_prosody_state(), 0)


if __name__ == "__main__":
    unittest.main()
