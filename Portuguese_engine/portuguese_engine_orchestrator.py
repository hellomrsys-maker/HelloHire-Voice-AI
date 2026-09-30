"""
Portuguese Language Engine Master Orchestrator.
Unifies all 9 layers, computational skills, cognitive analyzers, 4 dedicated Sub-AIs,
and the Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.skills.tokenization import PortugueseTokenizer
from .brain.skills.pos_tagging import PortuguesePOSTagger
from .brain.skills.verb_conjugator import PortugueseVerbConjugator
from .brain.skills.clitic_engine import PortugueseCliticEngine
from .brain.skills.contraction_engine import PortugueseContractionEngine
from .brain.skills.ser_estar_engine import PortugueseSerEstarEngine
from .brain.skills.pragmatics_engine import PortuguesePragmaticsEngine
from .brain.skills.parsing import PortugueseParser
from .brain.skills.generation import PortugueseGenerator

from .brain.analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from .brain.analysis.crase_contraction_analyzer import CraseContractionAnalyzer
from .brain.analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer

from .brain.task.grammar_check import PortugueseGrammarCheckTask
from .brain.task.email_pipeline import PortugueseEmailPipelineTask
from .brain.task.composition_pipeline import PortugueseCompositionPipelineTask

from .brain.sub_ais.syntax_sub_ai import PortugueseSyntaxSubAI, PortugueseSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import PortuguesePhonologySubAI, PortuguesePhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import PortuguesePragmaticSubAI, PortuguesePragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import PortugueseEditorialSubAI, PortugueseEditorialEvaluationResult

from .six_language_matrix.python.portuguese_matrix_bridge import PortugueseMatrixBridge


@dataclass
class PortugueseEngineAnalysisResult:
    input_text: str
    tokens: List[str]
    pos_tags: List[Dict[str, str]]
    parsed_structure: Dict[str, Any]
    clitic_analysis: Dict[str, Any]
    crase_analysis: Dict[str, Any]
    subjunctive_analysis: Dict[str, Any]
    syntax_eval: PortugueseSyntaxEvaluationResult
    phonology_eval: PortuguesePhonologyEvaluationResult
    pragmatic_eval: PortuguesePragmaticEvaluationResult
    editorial_eval: PortugueseEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class PortugueseEngineOrchestrator:
    """
    Master Orchestrator for Portuguese Language Processing & Cognitive Assessment.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()

        # Brain Skills
        self.tokenizer = PortugueseTokenizer()
        self.tagger = PortuguesePOSTagger()
        self.conjugator = PortugueseVerbConjugator()
        self.clitic_engine = PortugueseCliticEngine()
        self.contraction_engine = PortugueseContractionEngine()
        self.ser_estar = PortugueseSerEstarEngine()
        self.pragmatics = PortuguesePragmaticsEngine()
        self.parser = PortugueseParser()
        self.generator = PortugueseGenerator()

        # Cognitive Analyzers
        self.clitic_analyzer = CliticPlacementAnalyzer()
        self.crase_analyzer = CraseContractionAnalyzer()
        self.subjunctive_analyzer = SubjunctiveConcordAnalyzer()

        # Task Pipelines
        self.grammar_task = PortugueseGrammarCheckTask()
        self.email_task = PortugueseEmailPipelineTask()
        self.composition_task = PortugueseCompositionPipelineTask()

        # Dedicated Sub-AIs
        self.syntax_sub_ai = PortugueseSyntaxSubAI(amsv_view=self.amsv)
        self.phonology_sub_ai = PortuguesePhonologySubAI(amsv_view=self.amsv)
        self.pragmatic_sub_ai = PortuguesePragmaticSubAI(amsv_view=self.amsv)
        self.editorial_sub_ai = PortugueseEditorialSubAI(amsv_view=self.amsv)

        # Six-Language Matrix Bridge
        self.matrix_bridge = PortugueseMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> PortugueseEngineAnalysisResult:
        """
        Executes complete multi-layer linguistic analysis and zero-bridge AMSV synchronization.
        """
        tokens = self.tokenizer.tokenize(text)
        tagged = self.tagger.tag_tokens(tokens)
        parsed = self.parser.parse_sentence(text)

        clitic_res = self.clitic_analyzer.analyze_sentence(text)
        crase_res = self.crase_analyzer.analyze_sentence(text)
        sub_res = self.subjunctive_analyzer.analyze_sentence(text)

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

        return PortugueseEngineAnalysisResult(
            input_text=text,
            tokens=tokens,
            pos_tags=tagged,
            parsed_structure=parsed,
            clitic_analysis=clitic_res,
            crase_analysis=crase_res,
            subjunctive_analysis=sub_res,
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
        tier: str = "formal",
        custom_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a complete Portuguese email/letter."""
        return self.email_task.compose_email(
            recipient_name=recipient_name,
            sender_name=sender_name,
            purpose=purpose,
            tier=tier,
            custom_body=custom_body
        )

    def compose_prose(
        self,
        topic: str = "daily_work",
        subject: str = "Nós",
        dialect: str = "pt_br"
    ) -> Dict[str, Any]:
        """Generates multi-clause Portuguese prose."""
        return self.composition_task.compose_narrative(
            topic=topic,
            subject=subject,
            dialect=dialect
        )

    def generate_sentence(
        self,
        verb_lemma: str,
        subject: Optional[str] = None,
        direct_object: Optional[str] = None,
        indirect_object: Optional[str] = None,
        clitic: Optional[str] = None,
        mood: str = "indicativo",
        tense: str = "presente",
        person: str = "ele",
        negative: bool = False,
        punctuation: str = "."
    ) -> str:
        """Synthesizes a grammatical Portuguese sentence."""
        return self.generator.generate_clause(
            verb_lemma=verb_lemma,
            subject=subject,
            direct_object=direct_object,
            indirect_object=indirect_object,
            clitic=clitic,
            mood=mood,
            tense=tense,
            person=person,
            negative=negative,
            punctuation=punctuation
        )
