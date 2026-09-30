"""
Bengali Language Engine Master Orchestrator.
Unifies all 9 layers, computational skills, cognitive analyzers, 4 dedicated Sub-AIs,
and the Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.skills.tokenization import BengaliTokenizer
from .brain.skills.pos_tagging import BengaliPOSTagger
from .brain.skills.verb_conjugator import BengaliVerbConjugator
from .brain.skills.classifier_engine import BengaliClassifierEngine
from .brain.skills.case_engine import BengaliCaseEngine
from .brain.skills.compound_verb_engine import BengaliCompoundVerbEngine
from .brain.skills.pragmatics_engine import BengaliPragmaticsEngine
from .brain.skills.parsing import BengaliParser
from .brain.skills.generation import BengaliGenerator

from .brain.analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer
from .brain.analysis.case_postposition_analyzer import CasePostpositionAnalyzer
from .brain.analysis.honorific_register_analyzer import HonorificRegisterAnalyzer

from .brain.task.grammar_check import BengaliGrammarCheckTask
from .brain.task.email_pipeline import BengaliEmailPipelineTask
from .brain.task.composition_pipeline import BengaliCompositionPipelineTask

from .brain.sub_ais.syntax_sub_ai import BengaliSyntaxSubAI, BengaliSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import BengaliPhonologySubAI, BengaliPhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import BengaliPragmaticSubAI, BengaliPragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import BengaliEditorialSubAI, BengaliEditorialEvaluationResult

from .six_language_matrix.python.bengali_matrix_bridge import BengaliMatrixBridge


@dataclass
class BengaliEngineAnalysisResult:
    input_text: str
    tokens: List[str]
    pos_tags: List[Dict[str, str]]
    parsed_structure: Dict[str, Any]
    classifier_analysis: Dict[str, Any]
    case_analysis: Dict[str, Any]
    honorific_analysis: Dict[str, Any]
    syntax_eval: BengaliSyntaxEvaluationResult
    phonology_eval: BengaliPhonologyEvaluationResult
    pragmatic_eval: BengaliPragmaticEvaluationResult
    editorial_eval: BengaliEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class BengaliEngineOrchestrator:
    """
    Master Orchestrator for Bengali Language Processing & Cognitive Assessment.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

        # Brain Skills
        self.tokenizer = BengaliTokenizer()
        self.tagger = BengaliPOSTagger()
        self.conjugator = BengaliVerbConjugator()
        self.classifier_engine = BengaliClassifierEngine()
        self.case_engine = BengaliCaseEngine()
        self.compound_engine = BengaliCompoundVerbEngine(self.conjugator)
        self.pragmatics = BengaliPragmaticsEngine()
        self.parser = BengaliParser()
        self.generator = BengaliGenerator()

        # Cognitive Analyzers
        self.clf_analyzer = ClassifierConcordAnalyzer()
        self.case_analyzer = CasePostpositionAnalyzer()
        self.honorific_analyzer = HonorificRegisterAnalyzer()

        # Task Pipelines
        self.grammar_task = BengaliGrammarCheckTask()
        self.email_task = BengaliEmailPipelineTask()
        self.composition_task = BengaliCompositionPipelineTask()

        # Dedicated Sub-AIs
        self.syntax_sub_ai = BengaliSyntaxSubAI(amsv_view=self.amsv)
        self.phonology_sub_ai = BengaliPhonologySubAI(amsv_view=self.amsv)
        self.pragmatic_sub_ai = BengaliPragmaticSubAI(amsv_view=self.amsv)
        self.editorial_sub_ai = BengaliEditorialSubAI(amsv_view=self.amsv)

        # Six-Language Matrix Bridge
        self.matrix_bridge = BengaliMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> BengaliEngineAnalysisResult:
        """
        Executes complete multi-layer linguistic analysis and zero-bridge AMSV synchronization.
        """
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag_tokens(tokens)
        parsed = self.parser.parse_sentence(text)

        clf_res = self.clf_analyzer.analyze_sentence(text)
        case_res = self.case_analyzer.analyze_sentence(text)
        hon_res = self.honorific_analyzer.analyze_sentence(text)

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

        return BengaliEngineAnalysisResult(
            input_text=text,
            tokens=tokens,
            pos_tags=tagged,
            parsed_structure=parsed,
            classifier_analysis=clf_res,
            case_analysis=case_res,
            honorific_analysis=hon_res,
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
        return self.grammar_task.run(text)

    def compose_email(
        self,
        recipient_name: str,
        sender_name: str,
        purpose: str = "general",
        tier: str = "superior",
        custom_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a complete Bengali email/letter."""
        return self.email_task.compose_email(
            recipient_name=recipient_name,
            sender_name=sender_name,
            purpose=purpose,
            tier=tier,
            custom_body=custom_body
        )

    def compose_prose(
        self,
        topic: str = "daily_routine",
        subject: str = "আমি",
        tier: str = "1st",
        include_compound: bool = True
    ) -> Dict[str, Any]:
        """Generates multi-clause Bengali prose."""
        return self.composition_task.compose_narrative(
            topic=topic,
            subject=subject,
            tier=tier,
            include_compound=include_compound
        )

    def generate_sentence(
        self,
        verb_lemma: str,
        subject: Optional[str] = None,
        direct_object: Optional[str] = None,
        indirect_object: Optional[str] = None,
        adverbial: Optional[str] = None,
        tense: str = "present_simple",
        politeness: str = "familiar",
        negative: bool = False,
        vector_verb: Optional[str] = None,
        classifier: Optional[str] = None,
        punctuation: str = "।"
    ) -> str:
        """Synthesizes a grammatical Bengali sentence."""
        return self.generator.generate_clause(
            verb_lemma=verb_lemma,
            subject=subject,
            direct_object=direct_object,
            indirect_object=indirect_object,
            adverbial=adverbial,
            tense=tense,
            politeness=politeness,
            negative=negative,
            vector_verb=vector_verb,
            classifier=classifier,
            punctuation=punctuation
        )
