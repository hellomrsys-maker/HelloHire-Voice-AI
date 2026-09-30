"""
Self-Assessment, Learner Progress, and Diagnostic Testing Engine.

Provides:
  - Multi-level CEFR-aligned assessment items (A1 to C2)
  - Diverse task modalities: Multiple choice with distractor rationale, Cloze/fill-in-the-blank,
    Sentence correction, Syntactic transformations, Open-ended prompts
  - Real-time diagnostic evaluation with grammar rule references
  - State-tracking Learner Profile and personalized dynamic study roadmaps.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from ..common.models import (
    AssessmentQuestion,
    LearnerProfile,
)


@dataclass
class AssessmentQuiz:
    quiz_id: str
    target_cefr_level: str
    topic: str
    questions: List[AssessmentQuestion]


@dataclass
class DiagnosticReport:
    total_questions: int
    correct_count: int
    score_percentage: float
    cefr_assessment: str
    domain_breakdown: Dict[str, float]
    specific_error_feedback: List[Dict[str, Any]]
    personalized_roadmap: List[str]


class AssessmentEngine:
    """
    Diagnostic assessment engine evaluating learner grammatical proficiency,
    scoring responses with distractor explanations, and generating remediation roadmaps.
    """

    def __init__(self):
        self._question_bank: List[AssessmentQuestion] = []
        self._profiles: Dict[str, LearnerProfile] = {}
        self._initialize_question_bank()

    def _initialize_question_bank(self):
        # A1 - BEGINNER: Subject-Verb Agreement / Basic Copula
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_A1_01",
            question_type="multiple_choice",
            prompt="Select the grammatically correct sentence:",
            target_concept="Subject-Verb Agreement (Present Simple)",
            cefr_level="A1",
            options=[
                "She live in London with her family.",
                "She lives in London with her family.",
                "She living in London with her family.",
                "She are living in London with her family."
            ],
            correct_answer="She lives in London with her family.",
            distractor_explanations={
                "She live in London with her family.": "Incorrect: 3rd person singular subject 'She' requires suffix -s on the present simple verb.",
                "She living in London with her family.": "Incorrect: Present participle 'living' cannot serve as finite predicate without an auxiliary copula.",
                "She are living in London with her family.": "Incorrect: Auxiliary 'are' clashes in number with singular subject 'She'."
            },
            full_explanation="In English, 3rd person singular subjects (he, she, it) require the inflectional morpheme -s/-es on the lexical verb in the present simple indicative.",
            grammar_rule_reference="Rule: Subject-Verb Agreement in Present Indicative (Third Person Singular -s)"
        ))

        # A2 - ELEMENTARY: Past Simple vs Present Perfect
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_A2_01",
            question_type="cloze_fill_blank",
            prompt="Yesterday, the professor ______ (give) a fascinating lecture on historical linguistics.",
            target_concept="Past Simple with Definite Past Temporal Anchor",
            cefr_level="A2",
            options=["gave", "has given", "was given", "gives"],
            correct_answer="gave",
            distractor_explanations={
                "has given": "Incorrect: Present perfect cannot co-occur with a specific past time anchor like 'Yesterday'.",
                "was given": "Incorrect: Passive construction makes the professor the recipient rather than the agent of lecturing.",
                "gives": "Incorrect: Present tense contradicts the past time adverb 'Yesterday'."
            },
            full_explanation="When a sentence contains a definite past temporal adverbial ('yesterday', 'in 1998', 'three days ago'), the Past Simple tense ('gave') is required rather than the Present Perfect.",
            grammar_rule_reference="Rule: Definite Past Time Anchor vs Present Perfect Constraint"
        ))

        # B1 - INTERMEDIATE: Correlative Conjunctions & Agreement
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_B1_01",
            question_type="sentence_correction",
            prompt="Identify the correct fix for: 'Neither the manager or the supervisors was present.'",
            target_concept="Correlative Conjunctions & Proximity Agreement",
            cefr_level="B1",
            options=[
                "Neither the manager nor the supervisors were present.",
                "Neither the manager or the supervisors were present.",
                "Either the manager nor the supervisors was present.",
                "Neither the manager and the supervisors were present."
            ],
            correct_answer="Neither the manager nor the supervisors were present.",
            distractor_explanations={
                "Neither the manager or the supervisors were present.": "Incorrect: 'Neither' must pair strictly with 'nor', not 'or'.",
                "Either the manager nor the supervisors was present.": "Incorrect: 'Either' pairs with 'or', not 'nor'.",
                "Neither the manager and the supervisors were present.": "Incorrect: 'Neither' cannot pair with coordinating 'and'."
            },
            full_explanation="Correlative conjunction 'Neither' strictly pairs with 'nor'. Furthermore, when subjects differ in number, the verb agrees with the closer subject ('supervisors' -> plural 'were').",
            grammar_rule_reference="Rule: Correlative Conjunction Pairing and Principle of Proximity"
        ))

        # B2 - UPPER INTERMEDIATE: Subjunctive & Mandative Clauses
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_B2_01",
            question_type="multiple_choice",
            prompt="Which sentence correctly utilizes the mandative subjunctive mood?",
            target_concept="Mandative Subjunctive",
            cefr_level="B2",
            options=[
                "The board insisted that the CEO resigns immediately.",
                "The board insisted that the CEO resign immediately.",
                "The board insisted that the CEO must resign immediately.",
                "The board insisted that the CEO will resign immediately."
            ],
            correct_answer="The board insisted that the CEO resign immediately.",
            distractor_explanations={
                "The board insisted that the CEO resigns immediately.": "Incorrect: Indicative 3rd-person -s violates the requirement for the bare subjunctive stem in mandative complements.",
                "The board insisted that the CEO must resign immediately.": "Incorrect: Modal insertion is redundant and alters the formal mandative subjunctive register.",
                "The board insisted that the CEO will resign immediately.": "Incorrect: Future auxiliary 'will' is ungrammatical in formal mandative clauses."
            },
            full_explanation="In formal English, verbs of demanding, recommending, or insisting (insist, demand, recommend, decree) govern a subordinate that-clause containing the bare infinitive subjunctive verb ('resign').",
            grammar_rule_reference="Rule: Mandative Subjunctive in Finite Clausal Complements"
        ))

        # C1 - ADVANCED: Inversion & Negative Adverbials
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_C1_01",
            question_type="transformation",
            prompt="Transform the sentence by preposing the negative adverbial: 'I have seldom witnessed such profound intellectual dishonesty.'",
            target_concept="Negative Adverbial Preposing & Subject-Auxiliary Inversion",
            cefr_level="C1",
            options=[
                "Seldom I have witnessed such profound intellectual dishonesty.",
                "Seldom have I witnessed such profound intellectual dishonesty.",
                "Seldom did I witnessed such profound intellectual dishonesty.",
                "Seldom having I witnessed such profound intellectual dishonesty."
            ],
            correct_answer="Seldom have I witnessed such profound intellectual dishonesty.",
            distractor_explanations={
                "Seldom I have witnessed such profound intellectual dishonesty.": "Incorrect: Preposing a negative adverbial triggers obligatory subject-auxiliary inversion; uninverted order is ungrammatical.",
                "Seldom did I witnessed such profound intellectual dishonesty.": "Incorrect: Auxiliary 'did' cannot take a past-tense inflected participle 'witnessed'.",
                "Seldom having I witnessed such profound intellectual dishonesty.": "Incorrect: Participle 'having' cannot license finite inversion."
            },
            full_explanation="When negative or restrictive adverbials (seldom, rarely, scarcely, hardly, never, under no circumstances) are fronted for rhetorical focus, Subject-Auxiliary Inversion is obligatory in the matrix clause.",
            grammar_rule_reference="Rule: Negative Preposing and Head Movement (T-to-C Inversion)"
        ))

        # C2 - MASTERY: Complex Island Extraction & Parasitic Gaps
        self._question_bank.append(AssessmentQuestion(
            question_id="Q_C2_01",
            question_type="multiple_choice",
            prompt="Which sentence demonstrates a syntactically licensed parasitic gap?",
            target_concept="Parasitic Gaps and Island Constraints",
            cefr_level="C2",
            options=[
                "Which document did you file without reading?",
                "Which document did you file the report without reading it?",
                "Which document did you file the book because you liked?",
                "Which document did you file without you read?"
            ],
            correct_answer="Which document did you file without reading?",
            distractor_explanations={
                "Which document did you file the report without reading it?": "Incorrect: Contains an overt resumptive pronoun 'it', failing to exhibit a parasitic gap.",
                "Which document did you file the book because you liked?": "Incorrect: Violates the Adjunct Island Constraint without a licensed parasitic gap configuration.",
                "Which document did you file without you read?": "Incorrect: Ungrammatical non-finite prepositional complement."
            },
            full_explanation="A parasitic gap is a gap (empty category) that is licensed only by the presence of another real gap created by wh-movement. In 'Which document_i did you file t_i without reading e_i?', the second gap e_i inside the adjunct island is parasitically licensed by the primary wh-trace t_i.",
            grammar_rule_reference="Rule: Universal Island Constraints and Parasitic Gap Licensing"
        ))

    def create_quiz(self, target_cefr_level: str = "B1", topic: str = "General Grammar", question_count: int = 4) -> AssessmentQuiz:
        """
        Generate a customized assessment quiz matching target CEFR level and criteria.
        """
        filtered = [q for q in self._question_bank if q.cefr_level == target_cefr_level]
        if not filtered:
            filtered = self._question_bank[:question_count]

        return AssessmentQuiz(
            quiz_id=f"QUIZ_{target_cefr_level}_{len(filtered)}",
            target_cefr_level=target_cefr_level,
            topic=topic,
            questions=filtered[:question_count]
        )

    def evaluate_quiz(
        self, learner_id: str, quiz: AssessmentQuiz, learner_answers: Dict[str, str]
    ) -> DiagnosticReport:
        """
        Evaluate submitted answers, update learner profile, and generate a diagnostic roadmap.
        """
        correct_count = 0
        feedback_items = []
        domain_scores: Dict[str, List[float]] = {
            "Syntax & Word Order": [],
            "Morphology & Tense": [],
            "Agreement & Concord": [],
            "Advanced Stylistics": []
        }

        for q in quiz.questions:
            ans = learner_answers.get(q.question_id, "").strip()
            is_correct = (ans == q.correct_answer or ans == q.correct_answer.strip("."))

            domain = "Syntax & Word Order"
            if "Agreement" in q.target_concept:
                domain = "Agreement & Concord"
            elif "Tense" in q.target_concept or "Aspect" in q.target_concept:
                domain = "Morphology & Tense"
            elif q.cefr_level in {"C1", "C2"}:
                domain = "Advanced Stylistics"

            if is_correct:
                correct_count += 1
                domain_scores[domain].append(1.0)
                feedback_items.append({
                    "question_id": q.question_id,
                    "status": "CORRECT",
                    "explanation": q.full_explanation
                })
            else:
                domain_scores[domain].append(0.0)
                distractor_reason = q.distractor_explanations.get(ans, "Incorrect choice violating the target grammatical constraint.")
                feedback_items.append({
                    "question_id": q.question_id,
                    "status": "INCORRECT",
                    "user_answer": ans,
                    "correct_answer": q.correct_answer,
                    "distractor_critique": distractor_reason,
                    "remedial_explanation": q.full_explanation,
                    "rule_reference": q.grammar_rule_reference
                })

        pct = (correct_count / max(len(quiz.questions), 1)) * 100.0

        # CEFR level assessment
        if pct >= 85:
            cefr_eval = f"Proficient in {quiz.target_cefr_level} (Ready to advance to higher tier)."
        elif pct >= 60:
            cefr_eval = f"Developing in {quiz.target_cefr_level} (Consolidating core concepts)."
        else:
            cefr_eval = f"Needs foundational reinforcement in {quiz.target_cefr_level}."

        # Domain breakdown
        domain_summary = {
            k: (sum(v) / max(len(v), 1)) * 100.0 if v else 100.0 for k, v in domain_scores.items()
        }

        # Dynamic roadmap
        roadmap = []
        for domain, score in domain_summary.items():
            if score < 70.0:
                roadmap.append(f"PRIORITY REVISION: {domain} (Mastery at {score:.1f}%). Focus on systematic rule drills and contrastive analysis.")
        if not roadmap:
            roadmap.append("All tested domains demonstrate superior competency (>85%). Proceed to advanced stylistic transformations and cross-linguistic typological analysis.")

        # Update or create learner profile
        profile = self._profiles.get(learner_id, LearnerProfile(
            learner_id=learner_id,
            target_language="English",
            native_language="Universal",
            proficiency_level=quiz.target_cefr_level,
            domain_mastery={},
            error_frequency={},
            recommended_roadmap=roadmap
        ))
        for d, s in domain_summary.items():
            profile.domain_mastery[d] = s / 100.0
        profile.recommended_roadmap = roadmap
        self._profiles[learner_id] = profile

        return DiagnosticReport(
            total_questions=len(quiz.questions),
            correct_count=correct_count,
            score_percentage=round(pct, 1),
            cefr_assessment=cefr_eval,
            domain_breakdown={k: round(v, 1) for k, v in domain_summary.items()},
            specific_error_feedback=feedback_items,
            personalized_roadmap=roadmap
        )

    def get_learner_profile(self, learner_id: str) -> Optional[LearnerProfile]:
        """Retrieve historical learner profile state."""
        return self._profiles.get(learner_id)
