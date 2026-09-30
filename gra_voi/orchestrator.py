"""
Master Orchestrator: UniversalGrammarAI.

Coordinates all 12 core linguistic intelligence components and 4 proactive architectural
enhancements under a unified, high-level, production-grade programmatic API.
"""

from typing import Dict, List, Optional, Any, Union
from .common.models import (
    SentenceType,
    WordOrder,
    Tense,
    Aspect,
    Voice,
    WritingFormat,
    Register,
    GrammarConcept,
    SentenceAnalysis,
    CorrectionResult,
    PhoneticAnalysis,
    ContrastiveInsight,
    AssessmentQuestion,
    LearnerProfile,
)
from .reasoning.engine import DeepThinkingEngine, DeepReasoningTrace
from .universal_grammar.knowledge_base import UniversalGrammarKnowledgeBase
from .syntax.syntax_engine import SentenceSyntaxEngine
from .writing.writing_engine import WritingSkillEngine, WritingCritique
from .error_engine.error_detector import ErrorDetectionEngine
from .phonology.phonology_engine import PhonologyEngine
from .reading.reading_engine import ReadingComprehensionEngine, GrammaticalReadingAnalysis
from .spoken_language.spoken_engine import SpokenLanguageEngine, SpokenDiscourseAnalysis
from .multilingual.multilingual_engine import MultilingualEngine, LanguageProfile
from .creativity.creativity_engine import CreativityEngine, CreativeGenerationResult, StyleTransferResult
from .assessment.assessment_engine import AssessmentEngine, AssessmentQuiz, DiagnosticReport
from .compendium.compendium_engine import EducationalGrammarCompendium
from .pragmatics.pragmatics_engine import PragmaticsEngine, PragmaticAnalysisResult
from .discourse.discourse_engine import DiscourseEngine, DiscourseAnalysisResult
from .diachronic.diachronic_engine import DiachronicEngine, DiachronicShiftAnalysis
from .sla.sla_engine import SLAEngine, SLADiagnosisResult
from .typology.typology_engine import UniversalTypologyAI
from .common.models import LanguageFamilyEnum, TypologicalReport
from amsv.python.amsv_embedded import AMSVEmbeddedView


class UniversalGrammarAI:
    """
    Unified Master Controller for the Lingua Sapiens AI System.
    Provides complete access to all reasoning, knowledge, syntax, writing,
    correction, phonology, reading, speech, multilingual, creative,
    assessment, and compendium capabilities.
    Embedded directly with the 64-byte Atomic Memory State Vector (AMSV)
    under the Zero-Bridge Synchronous Memory Rule.
    """

    def __init__(self, amsv: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv if amsv is not None else AMSVEmbeddedView()

        # Component 1: Deep Thinking & Reasoning Engine
        self.reasoning = DeepThinkingEngine()
        # Component 2: Universal Grammar Knowledge Base
        self.knowledge_base = UniversalGrammarKnowledgeBase()
        # Component 3: Sentence Construction and Analysis Module
        self.syntax = SentenceSyntaxEngine()
        # Component 4: Writing Skill Module
        self.writing = WritingSkillEngine()
        # Component 5: Error Detection and Correction Engine
        self.error_engine = ErrorDetectionEngine()
        # Component 6: Pronunciation and Phonological Intelligence Module
        self.phonology = PhonologyEngine()
        # Component 7: Reading Comprehension Intelligence Module
        self.reading = ReadingComprehensionEngine()
        # Component 8: Listening and Spoken Language Module
        self.spoken = SpokenLanguageEngine()
        # Component 9: Multilingual and Cross-Linguistic Module
        self.multilingual = MultilingualEngine()
        # Component 10: Creativity and Language Generation Module
        self.creativity = CreativityEngine()
        # Component 11: Self-Assessment and Learner Progress Module
        self.assessment = AssessmentEngine()
        # Component 12: Comprehensive Educational Grammar Document Engine
        self.compendium = EducationalGrammarCompendium()

        # Proactive Architectural Enhancements:
        # Enhancement 1: Pragmatic Competence & Speech Acts
        self.pragmatics = PragmaticsEngine()
        # Enhancement 2: Discourse Analysis & Rhetorical Structure Theory
        self.discourse = DiscourseEngine()
        # Enhancement 3: Diachronic Evolution & Historical Linguistics
        self.diachronic = DiachronicEngine()
        # Enhancement 4: Second Language Acquisition & Cognitive Load
        self.sla = SLAEngine()
        # Dedicated Universal Typology & Comparative Grammar AI Sub-Engine
        self.typology = UniversalTypologyAI(amsv=self.amsv)

    # --- COMPONENT 1: DEEP THINKING ---
    def think(self, text: str, context: Optional[str] = None) -> DeepReasoningTrace:
        """Execute multi-tier linguistic reasoning across structural, semantic, pragmatic, and cognitive levels."""
        res = self.reasoning.think(text, context)
        score = min(1.0, 0.70 + 0.05 * len(res.step_by_step_thought_chain))
        self.amsv.set_cognitive_score(0, score)
        self.amsv.set_cognitive_score(2, 0.85)
        return res

    # --- COMPONENT 2: UNIVERSAL GRAMMAR KNOWLEDGE BASE ---
    def query_grammar(self, concept_name: str) -> Optional[GrammarConcept]:
        """Look up a concept definition, functional role, universal principle, and cross-linguistic examples."""
        return self.knowledge_base.get_concept(concept_name)

    def list_grammar_concepts(self) -> List[str]:
        """List all indexed grammar concepts."""
        return self.knowledge_base.list_all_concepts()

    def get_universal_principles(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve core principles of Universal Grammar."""
        return self.knowledge_base.get_universal_principles()

    # --- COMPONENT 3: SENTENCE SYNTAX & GENERATION ---
    def analyze_sentence(self, text: str) -> SentenceAnalysis:
        """Parse sentence type, constituents, grammatical roles, clauses, and build ASCII parse tree."""
        res = self.syntax.analyze(text)
        self.amsv.set_cognitive_score(5, 0.88)
        self.amsv.set_cognitive_score(6, min(1.0, 0.60 + 0.04 * len(res.constituents)))
        return res

    def construct_sentence(
        self,
        subject: str,
        verb: str,
        direct_object: Optional[str] = None,
        indirect_object: Optional[str] = None,
        sentence_type: SentenceType = SentenceType.SIMPLE,
        word_order: WordOrder = WordOrder.SVO,
        tense: Tense = Tense.PRESENT,
        aspect: Aspect = Aspect.SIMPLE,
        voice: Voice = Voice.ACTIVE,
        modifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesize a valid sentence from scratch across any of the 6 word order typologies."""
        return self.syntax.synthesize(
            subject=subject,
            verb=verb,
            direct_object=direct_object,
            indirect_object=indirect_object,
            sentence_type=sentence_type,
            word_order=word_order,
            tense=tense,
            aspect=aspect,
            voice=voice,
            modifier=modifier
        )

    def transform_sentence(self, sentence: str, transformation: str) -> Dict[str, Any]:
        """Transform a sentence across structural dimensions (active/passive, affirmative/negative, cleft, etc.)."""
        return self.syntax.transform(sentence, transformation)

    # --- COMPONENT 4: WRITING SKILL ---
    def generate_writing_model(self, writing_format: Union[WritingFormat, str], topic: str = "Linguistic Intelligence") -> str:
        """Generate a complete model document adhering to the structural blueprint of the genre."""
        if isinstance(writing_format, str):
            writing_format = WritingFormat(writing_format.lower())
        return self.writing.generate_model_document(writing_format, topic)

    def critique_writing(self, text: str, target_format: WritingFormat = WritingFormat.ESSAY_ARGUMENTATIVE) -> WritingCritique:
        """Evaluate submitted writing for syntactic maturity, cohesion, register, and generate actionable feedback."""
        res = self.writing.critique_writing(text, target_format)
        self.amsv.set_cognitive_score(6, res.overall_score / 100.0)
        return res

    # --- COMPONENT 5: ERROR DETECTION & CORRECTION ---
    def detect_errors(self, text: str):
        """Scan input text against 16+ grammatical error categories and return detailed diagnostic objects."""
        return self.error_engine.detect_errors(text)

    def correct_text(self, text: str) -> CorrectionResult:
        """Scan, annotate, explain, and output a fully corrected version of the submitted text."""
        res = self.error_engine.correct_text(text)
        self.amsv.set_cognitive_score(5, max(0.2, 1.0 - 0.1 * len(res.errors)))
        return res

    # --- COMPONENT 6: PRONUNCIATION & PHONOLOGY ---
    def analyze_pronunciation(self, word_or_sentence: str, grammatical_role: str = "noun", language: str = "English") -> PhoneticAnalysis:
        """Produce IPA transcription, syllable breakdown, stress pattern, and connected speech analysis."""
        res = self.phonology.analyze_phonology(word_or_sentence, grammatical_role, language)
        phoneme_hash = hash(res.ipa) & 0xFFFF
        self.amsv.set_phoneme_state(phoneme_hash | (0x7FFF << 16))
        self.amsv.set_prosody_state(0x008000000000 | (130 << 16) | 180)
        return res

    # --- COMPONENT 7: READING COMPREHENSION ---
    def analyze_reading_passage(self, passage: str) -> GrammaticalReadingAnalysis:
        """Deconstruct reading passage into matrix spine vs modifiers, track anaphora, and generate guided exercises."""
        return self.reading.analyze_passage(passage)

    # --- COMPONENT 8: SPOKEN LANGUAGE & LISTENING ---
    def analyze_spoken_discourse(self, transcript: str) -> SpokenDiscourseAnalysis:
        """Analyze oral speech features: disfluencies, heads/tails, ellipsis, discourse markers, and real-time parsing."""
        return self.spoken.analyze_spoken_discourse(transcript)

    # --- COMPONENT 9: MULTILINGUAL & CROSS-LINGUISTIC ---
    def compare_languages(self, source_lang: str, target_lang: str) -> ContrastiveInsight:
        """Perform pairwise contrastive analysis between L1 and L2, predicting interference and transfer errors."""
        return self.multilingual.compare_languages(source_lang, target_lang)

    def get_language_profile(self, language_name: str) -> Optional[LanguageProfile]:
        """Retrieve deep typological profile for a specific language."""
        return self.multilingual.get_language_profile(language_name)

    # --- COMPONENT 10: CREATIVITY & STYLE TRANSFER ---
    def generate_creative(self, genre: str, prompt: str, target_devices: Optional[List[str]] = None) -> CreativeGenerationResult:
        """Synthesize expressive creative writing (sonnet, haiku, fiction, dialogue, oration) with rhetorical explanations."""
        res = self.creativity.generate_creative_piece(genre, prompt, target_devices)
        self.amsv.set_cognitive_score(3, 0.94)
        self.amsv.set_cognitive_score(4, 0.92)
        return res

    def transfer_style(self, text: str, target_style: str) -> StyleTransferResult:
        """Transfer text across registers (Academic, Corporate, Victorian, Casual, Poetic) while preserving meaning."""
        return self.creativity.transfer_style(text, target_style)

    # --- COMPONENT 11: ASSESSMENT & LEARNER PROGRESS ---
    def create_quiz(self, cefr_level: str = "B1", topic: str = "General Grammar", count: int = 4) -> AssessmentQuiz:
        """Generate a customized diagnostic quiz at a specific CEFR proficiency level."""
        return self.assessment.create_quiz(cefr_level, topic, count)

    def evaluate_quiz(self, learner_id: str, quiz: AssessmentQuiz, learner_answers: Dict[str, str]) -> DiagnosticReport:
        """Score quiz answers, explain distractors, update learner profile, and generate a dynamic study roadmap."""
        res = self.assessment.evaluate_quiz(learner_id, quiz, learner_answers)
        theta = (res.score_percentage / 50.0) - 1.0
        self.amsv.set_examination_theta(theta)
        return res

    # --- COMPONENT 12: COMPREHENSIVE EDUCATIONAL COMPENDIUM ---
    def generate_educational_compendium(self) -> str:
        """Generate the complete, publication-grade 10-chapter educational grammar compendium."""
        return self.compendium.generate_full_document()

    def export_compendium(self, filepath: str) -> str:
        """Export the comprehensive educational grammar document to disk."""
        return self.compendium.export_to_file(filepath)

    # --- PROACTIVE ENHANCEMENTS ---
    def analyze_pragmatics(self, utterance: str, context: Optional[str] = None) -> PragmaticAnalysisResult:
        """Analyze speech act classification, Gricean maxims, implicatures, and politeness face strategies."""
        return self.pragmatics.analyze_pragmatics(utterance, context)

    def analyze_discourse(self, text: str) -> DiscourseAnalysisResult:
        """Analyze suprasentential cohesion ties, Rhetorical Structure Theory relations, and thematic progression."""
        return self.discourse.analyze_discourse(text)

    def analyze_diachronic_evolution(self, query: str) -> DiachronicShiftAnalysis:
        """Trace historical sound laws (Grimm's Law, GVS), grammaticalization cycles, and grammatical irregularities."""
        return self.diachronic.analyze_historical_evolution(query)

    def diagnose_sla(self, errors_detected: List[str], l1: str = "Spanish", l2: str = "English", exposure_years: float = 2.0) -> SLADiagnosisResult:
        """Diagnose interlanguage development stage, fossilization risk, Krashen i+1 zone, and cognitive load."""
        return self.sla.diagnose_learner(errors_detected, l1, l2, exposure_years)

    # --- DEDICATED TYPOLOGY & COMPARATIVE GRAMMAR SUB-ENGINE ---
    def diagnose_typology(self, text: str, family: Optional[LanguageFamilyEnum] = None) -> TypologicalReport:
        """Execute the 8-Pillar Universal Typological Diagnostic over text, evaluating synthesis, alignment, and harmony."""
        return self.typology.diagnose_text(text, family)

    def predict_typology_friction(self, l1: LanguageFamilyEnum, l2: LanguageFamilyEnum) -> List[str]:
        """Predict L1 -> L2 negative transfer friction points and pedagogical traps."""
        return self.typology.predict_transfer_friction(l1, l2)

