"""Turkish Language Engine Master Orchestrator.

Unifies all 9 layers, computational skills, cognitive analyzers, 4 dedicated Sub-AIs,
and the Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.skills.tokenization import TurkishTokenizer
from .brain.skills.vowel_harmony_engine import TurkishVowelHarmonyEngine
from .brain.skills.consonant_mutation_engine import TurkishConsonantMutationEngine
from .brain.skills.pos_tagging import TurkishPOSTagger
from .brain.skills.case_engine import TurkishCaseEngine
from .brain.skills.verb_conjugator import TurkishVerbConjugator
from .brain.skills.pragmatics_engine import TurkishPragmaticsEngine
from .brain.skills.parsing import TurkishDependencyParser
from .brain.skills.generation import TurkishSentenceGenerator

from .brain.analysis.vowel_harmony_analyzer import TurkishVowelHarmonyAnalyzer
from .brain.analysis.case_postposition_analyzer import TurkishCasePostpositionAnalyzer
from .brain.analysis.evidentiality_analyzer import TurkishEvidentialityAnalyzer

from .brain.task.grammar_check import TurkishGrammarChecker
from .brain.task.email_pipeline import TurkishEmailPipeline
from .brain.task.composition_pipeline import TurkishCompositionPipeline

from .brain.sub_ais.syntax_sub_ai import TurkishSyntaxSubAI, TurkishSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import TurkishPhonologySubAI, TurkishPhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import TurkishPragmaticSubAI, TurkishPragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import TurkishEditorialSubAI, TurkishEditorialEvaluationResult

from .six_language_matrix.python.turkish_matrix_bridge import TurkishMatrixBridge


@dataclass
class TurkishEngineAnalysisResult:
    input_text: str
    tokens: List[str]
    pos_tags: List[Dict[str, str]]
    parsed_structure: Dict[str, Any]
    vowel_harmony_analysis: Dict[str, Any]
    case_analysis: Dict[str, Any]
    evidentiality_analysis: Dict[str, Any]
    syntax_eval: TurkishSyntaxEvaluationResult
    phonology_eval: TurkishPhonologyEvaluationResult
    pragmatic_eval: TurkishPragmaticEvaluationResult
    editorial_eval: TurkishEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class TurkishEngineOrchestrator:
    """Master Orchestrator for Turkish Language Processing & Cognitive Assessment."""

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

        # Brain Skills
        self.tokenizer = TurkishTokenizer()
        self.harmony = TurkishVowelHarmonyEngine()
        self.mutation = TurkishConsonantMutationEngine()
        self.tagger = TurkishPOSTagger()
        self.case_engine = TurkishCaseEngine(self.harmony, self.mutation)
        self.verb_conjugator = TurkishVerbConjugator(self.harmony, self.mutation)
        self.pragmatics = TurkishPragmaticsEngine()
        self.parser = TurkishDependencyParser(self.tokenizer, self.tagger)
        self.generator = TurkishSentenceGenerator(
            self.case_engine, self.verb_conjugator, self.harmony
        )

        # Cognitive Analyzers
        self.harmony_analyzer = TurkishVowelHarmonyAnalyzer(self.tokenizer, self.harmony)
        self.case_analyzer = TurkishCasePostpositionAnalyzer(self.tokenizer, self.tagger, self.harmony)
        self.evidential_analyzer = TurkishEvidentialityAnalyzer(self.tokenizer, self.tagger)

        # Task Pipelines
        self.grammar_task = TurkishGrammarChecker()
        self.email_task = TurkishEmailPipeline(self.pragmatics)
        self.composition_task = TurkishCompositionPipeline()

        # Dedicated Sub-AIs
        self.syntax_sub_ai = TurkishSyntaxSubAI(amsv_view=self.amsv)
        self.phonology_sub_ai = TurkishPhonologySubAI(amsv_view=self.amsv)
        self.pragmatic_sub_ai = TurkishPragmaticSubAI(amsv_view=self.amsv)
        self.editorial_sub_ai = TurkishEditorialSubAI(amsv_view=self.amsv)

        # Six-Language Matrix Bridge
        self.matrix_bridge = TurkishMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> TurkishEngineAnalysisResult:
        """Executes complete multi-layer linguistic analysis and zero-bridge AMSV synchronization."""
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag(tokens)
        parsed = self.parser.parse(text)

        harm_res = self.harmony_analyzer.analyze(text)
        case_res = self.case_analyzer.analyze(text)
        evid_res = self.evidential_analyzer.analyze(text)

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
            (phono_res.phonological_density_score * 0.20) +
            (prag_res.politeness_score * 0.20) +
            (edit_res.editorial_score * 0.25),
            3
        )

        return TurkishEngineAnalysisResult(
            input_text=text,
            tokens=tokens,
            pos_tags=tagged,
            parsed_structure=parsed,
            vowel_harmony_analysis=harm_res,
            case_analysis=case_res,
            evidentiality_analysis=evid_res,
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
        recipient_name: str,
        sender_name: str = "Ahmet",
        subject: str = "Proje Güncellemesi",
        recipient_gender: str = "masc",
        register: str = "formal_business",
        body_paragraphs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generates a complete Turkish email."""
        return self.email_task.compose_email(
            recipient_name=recipient_name,
            sender_name=sender_name,
            subject=subject,
            recipient_gender=recipient_gender,
            register=register,
            body_paragraphs=body_paragraphs
        )

    def compose_report(
        self,
        engineer_name: str,
        task_count: int = 3,
        system_name: str = "modül",
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Generates a structured technical report."""
        return self.composition_task.compose_report(
            engineer_name=engineer_name,
            task_count=task_count,
            system_name=system_name,
            status=status
        )

    def compose_prose(
        self,
        author_name: str = "Ahmet",
        task_count: int = 3
    ) -> Dict[str, Any]:
        """Generates structured narrative prose."""
        return self.compose_report(engineer_name=author_name, task_count=task_count)

    def generate_sentence(
        self,
        subject: str,
        verb_lemma: str,
        object_noun: str,
        is_definite_object: bool = True,
        tense: str = "past",
        person: str = "3sg"
    ) -> str:
        """Generates an affirmative SOV clause."""
        return self.generator.generate_transitive_sov(
            subject=subject,
            verb_lemma=verb_lemma,
            object_noun=object_noun,
            is_definite_object=is_definite_object,
            tense=tense,
            person=person
        )
