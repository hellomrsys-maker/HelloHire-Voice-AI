"""Russian Language Engine Master Orchestrator.

Unifies all 9 layers, computational skills, cognitive analyzers, 4 dedicated Sub-AIs,
and the Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.skills.tokenization import RussianTokenizer
from .brain.skills.pos_tagging import RussianPOSTagger
from .brain.skills.verb_aspect_conjugator import RussianVerbAspectConjugator
from .brain.skills.case_engine import RussianCaseEngine
from .brain.skills.motion_verb_engine import RussianMotionVerbEngine
from .brain.skills.numeral_concord_engine import RussianNumeralConcordEngine
from .brain.skills.pragmatics_engine import RussianPragmaticsEngine
from .brain.skills.parsing import RussianDependencyParser
from .brain.skills.generation import RussianSentenceGenerator

from .brain.analysis.case_government_analyzer import RussianCaseGovernmentAnalyzer
from .brain.analysis.aspect_choice_analyzer import RussianAspectChoiceAnalyzer
from .brain.analysis.numeral_concord_analyzer import RussianNumeralConcordAnalyzer

from .brain.task.grammar_check import RussianGrammarChecker
from .brain.task.email_pipeline import RussianEmailPipeline
from .brain.task.composition_pipeline import RussianCompositionPipeline

from .brain.sub_ais.syntax_sub_ai import RussianSyntaxSubAI, RussianSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import RussianPhonologySubAI, RussianPhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import RussianPragmaticSubAI, RussianPragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import RussianEditorialSubAI, RussianEditorialEvaluationResult

from .six_language_matrix.python.russian_matrix_bridge import RussianMatrixBridge


@dataclass
class RussianEngineAnalysisResult:
    input_text: str
    tokens: List[str]
    pos_tags: List[Dict[str, str]]
    parsed_structure: Dict[str, Any]
    case_analysis: Dict[str, Any]
    aspect_analysis: Dict[str, Any]
    numeral_analysis: Dict[str, Any]
    syntax_eval: RussianSyntaxEvaluationResult
    phonology_eval: RussianPhonologyEvaluationResult
    pragmatic_eval: RussianPragmaticEvaluationResult
    editorial_eval: RussianEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class RussianEngineOrchestrator:
    """Master Orchestrator for Russian Language Processing & Cognitive Assessment."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

        # Brain Skills
        self.tokenizer = RussianTokenizer()
        self.tagger = RussianPOSTagger()
        self.verb_conjugator = RussianVerbAspectConjugator()
        self.case_engine = RussianCaseEngine()
        self.motion_engine = RussianMotionVerbEngine()
        self.numeral_engine = RussianNumeralConcordEngine(self.case_engine)
        self.pragmatics = RussianPragmaticsEngine()
        self.parser = RussianDependencyParser(self.tokenizer, self.tagger)
        self.generator = RussianSentenceGenerator(
            self.case_engine, self.verb_conjugator, self.numeral_engine
        )

        # Cognitive Analyzers
        self.case_analyzer = RussianCaseGovernmentAnalyzer(
            self.tokenizer, self.tagger, self.case_engine
        )
        self.aspect_analyzer = RussianAspectChoiceAnalyzer(
            self.tokenizer, self.tagger, self.verb_conjugator, self.motion_engine
        )
        self.numeral_analyzer = RussianNumeralConcordAnalyzer(
            self.tokenizer, self.tagger, self.numeral_engine
        )

        # Task Pipelines
        self.grammar_task = RussianGrammarChecker()
        self.email_task = RussianEmailPipeline(self.pragmatics)
        self.composition_task = RussianCompositionPipeline()

        # Dedicated Sub-AIs
        self.syntax_sub_ai = RussianSyntaxSubAI(amsv_view=self.amsv)
        self.phonology_sub_ai = RussianPhonologySubAI(amsv_view=self.amsv)
        self.pragmatic_sub_ai = RussianPragmaticSubAI(amsv_view=self.amsv)
        self.editorial_sub_ai = RussianEditorialSubAI(amsv_view=self.amsv)

        # Six-Language Matrix Bridge
        self.matrix_bridge = RussianMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> RussianEngineAnalysisResult:
        """Executes complete multi-layer linguistic analysis and zero-bridge AMSV synchronization."""
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed = self.parser.parse(text)

        case_res = self.case_analyzer.analyze(text)
        aspect_res = self.aspect_analyzer.analyze(text)
        numeral_res = self.numeral_analyzer.analyze(text)

        # Execute Sub-AIs
        syntax_res = self.syntax_sub_ai.evaluate(text)
        phono_res = self.phonology_sub_ai.evaluate(text)
        prag_res = self.pragmatic_sub_ai.evaluate(text)
        edit_res = self.editorial_sub_ai.evaluate(text)

        # Matrix integration
        matrix_res = self.matrix_bridge.execute_matrix_pipeline(
            text=text,
            syntax_score=syntax_res.syntax_score,
            phonology_score=phono_res.phonology_score,
            register_score=prag_res.politeness_score
        )

        overall_score = round(
            (syntax_res.syntax_score * 0.35) +
            (phono_res.phonological_density_score * 0.15) +
            (prag_res.politeness_score * 0.25) +
            (edit_res.editorial_score * 0.25),
            3
        )

        return RussianEngineAnalysisResult(
            input_text=text,
            tokens=tokens,
            pos_tags=tagged,
            parsed_structure=parsed,
            case_analysis=case_res,
            aspect_analysis=aspect_res,
            numeral_analysis=numeral_res,
            syntax_eval=syntax_res,
            phonology_eval=phono_res,
            pragmatic_eval=prag_res,
            editorial_eval=edit_res,
            matrix_status=matrix_res,
            overall_linguistic_score=overall_score,
            amsv_synced=True
        )

    def proofread(self, text: str) -> Dict[str, Any]:
        """Runs the grammar and proofreading audit task."""
        return self.grammar_task.check(text)

    def compose_email(
        self,
        recipient_first_name: str,
        recipient_father_name: Optional[str] = None,
        recipient_gender: str = "masc",
        sender_name: str = "Александр",
        subject: str = "Рабочий вопрос",
        body_paragraphs: Optional[list] = None,
        register: str = "formal_business"
    ) -> Dict[str, Any]:
        """Generates a complete Russian email/correspondence."""
        return self.email_task.compose_email(
            recipient_first_name=recipient_first_name,
            recipient_father_name=recipient_father_name,
            recipient_gender=recipient_gender,
            sender_name=sender_name,
            subject=subject,
            body_paragraphs=body_paragraphs,
            register=register
        )

    def compose_report(
        self,
        engineer_name: str,
        task_count: int,
        component_lemma: str = "модуль",
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Generates a structured technical report with paucal concord."""
        return self.composition_task.compose_report(
            engineer_name=engineer_name,
            task_count=task_count,
            component_lemma=component_lemma,
            status=status
        )

    def compose_prose(
        self,
        author_name: str = "Иван",
        task_count: int = 3
    ) -> Dict[str, Any]:
        """Generates structured narrative prose."""
        return self.compose_report(engineer_name=author_name, task_count=task_count)

    def generate_sentence(
        self,
        subj_lemma: str,
        subj_gender: str,
        verb_lemma: str,
        obj_lemma: str,
        obj_gender: str,
        obj_declension: str = "2nd",
        obj_animacy: bool = False,
        tense: str = "past"
    ) -> str:
        """Generates an affirmative SVO clause."""
        return self.generator.generate_transitive_svo(
            subj_lemma=subj_lemma,
            subj_gender=subj_gender,
            verb_lemma=verb_lemma,
            obj_lemma=obj_lemma,
            obj_gender=obj_gender,
            obj_declension=obj_declension,
            obj_animacy=obj_animacy,
            tense=tense
        )

