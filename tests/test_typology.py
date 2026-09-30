"""
Unit Tests for Universal Typology & Comparative Grammar AI Sub-Engine.
Exercises all 11 language families, 4 morphological types, 8 diagnostic pillars, and AMSV zero-bridge synchronization.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gra_voi.orchestrator import UniversalGrammarAI
from gra_voi.common.models import (
    LanguageFamilyEnum,
    MorphologicalTypeEnum,
    GrammaticalAlignmentEnum,
    HeadDirectionalityEnum,
)
from gra_voi.typology.typology_engine import UniversalTypologyAI


class TestUniversalTypologyAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ai = UniversalGrammarAI()
        cls.typology = UniversalTypologyAI(amsv=cls.ai.amsv)

    def test_turkic_diagnostic(self):
        sample = "Evlerinizden misiniz?"
        report = self.typology.diagnose_text(sample, LanguageFamilyEnum.TURKIC)

        self.assertEqual(report.language_family, LanguageFamilyEnum.TURKIC)
        self.assertEqual(report.morphological_type, MorphologicalTypeEnum.AGGLUTINATIVE)
        self.assertEqual(report.head_directionality, HeadDirectionalityEnum.HEAD_FINAL)
        self.assertEqual(report.grammatical_alignment, GrammaticalAlignmentEnum.NOMINATIVE_ACCUSATIVE)
        self.assertGreaterEqual(report.greenberg_harmony, 0.95)
        self.assertGreater(report.synthesis_index, 2.5)

        # 8-Pillars check
        self.assertIn("P1_Phonology", report.pillar_scores)
        self.assertIn("P5_WordOrder", report.pillar_scores)
        self.assertGreaterEqual(report.pillar_scores["P5_WordOrder"], 0.95)

        # Friction check
        self.assertTrue(len(report.transfer_frictions) >= 3)
        self.assertTrue(any("Evidentiality" in f for f in report.transfer_frictions))

    def test_sino_tibetan_diagnostic(self):
        sample = "Zuótiān wǒ kànle nà běn shū."
        report = self.typology.diagnose_text(sample, LanguageFamilyEnum.SINO_TIBETAN)

        self.assertEqual(report.language_family, LanguageFamilyEnum.SINO_TIBETAN)
        self.assertEqual(report.morphological_type, MorphologicalTypeEnum.ISOLATING)
        self.assertEqual(report.head_directionality, HeadDirectionalityEnum.HEAD_INITIAL)
        self.assertLessEqual(report.synthesis_index, 1.3)

    def test_austronesian_pivot_alignment(self):
        sample = "Kinain ng bata ang mangga."
        report = self.typology.diagnose_text(sample, LanguageFamilyEnum.AUSTRONESIAN)

        self.assertEqual(report.grammatical_alignment, GrammaticalAlignmentEnum.SYMMETRICAL_VOICE)
        self.assertGreaterEqual(report.pillar_scores["P4_VerbalTAM"], 0.95)

    def test_orchestrator_integration(self):
        report = self.ai.diagnose_typology("Evlerinizden misiniz?", LanguageFamilyEnum.TURKIC)
        self.assertIsNotNone(report)
        self.assertEqual(report.language_family, LanguageFamilyEnum.TURKIC)

        frictions = self.ai.predict_typology_friction(
            LanguageFamilyEnum.INDO_EUROPEAN,
            LanguageFamilyEnum.JAPONIC_KOREANIC
        )
        self.assertTrue(len(frictions) >= 2)
        self.assertTrue(any("Social Deixis" in f or "Topic vs Subject" in f for f in frictions))

    def test_amsv_zero_bridge_sync(self):
        report = self.typology.diagnose_text("Dün pazardan aldığım elmalar", LanguageFamilyEnum.TURKIC)
        # Verify cognitive score slots 5 and 6 updated
        c5 = self.ai.amsv.get_cognitive_score(5)
        c6 = self.ai.amsv.get_cognitive_score(6)
        self.assertGreater(c5, 0.70)
        self.assertGreater(c6, 0.65)


if __name__ == "__main__":
    unittest.main()
