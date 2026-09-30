"""
Hebrew Language Engine Master Orchestrator.
Unifies all 9 layers, 4 dedicated Sub-AIs, and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.sub_ais.syntax_sub_ai import HebrewSyntaxSubAI, HebrewSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import HebrewPhonologySubAI, HebrewPhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import HebrewPragmaticSubAI, HebrewPragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import HebrewEditorialSubAI, HebrewEditorialEvaluationResult
from .six_language_matrix.python.hebrew_matrix_bridge import HebrewMatrixBridge


@dataclass
class HebrewEngineAnalysisResult:
    input_text: str
    syntax_eval: HebrewSyntaxEvaluationResult
    phonology_eval: HebrewPhonologyEvaluationResult
    pragmatic_eval: HebrewPragmaticEvaluationResult
    editorial_eval: HebrewEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class HebrewEngineOrchestrator:
    """Master Orchestrator for Hebrew Language Processing & Cognitive Assessment."""

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ):
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.checkpoint_path = checkpoint_path

        # Dedicated Sub-AIs
        self.syntax_sub_ai = HebrewSyntaxSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.phonology_sub_ai = HebrewPhonologySubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.pragmatic_sub_ai = HebrewPragmaticSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.editorial_sub_ai = HebrewEditorialSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)

        # Six-Language Matrix Bridge
        self.matrix_bridge = HebrewMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> HebrewEngineAnalysisResult:
        syntax_res = self.syntax_sub_ai.evaluate(text)
        phono_res = self.phonology_sub_ai.evaluate(text)
        prag_res = self.pragmatic_sub_ai.evaluate(text)
        edit_res = self.editorial_sub_ai.evaluate(text)

        matrix_res = self.matrix_bridge.execute_matrix_pipeline(
            text=text,
            syntax_score=syntax_res.syntax_score,
            phonology_score=phono_res.phonology_score,
            register_score=prag_res.politeness_score,
        )

        overall = round(
            (syntax_res.syntax_score * 0.35) +
            (phono_res.phonological_density_score * 0.20) +
            (prag_res.politeness_score * 0.20) +
            (edit_res.editorial_score * 0.25),
            3,
        )

        return HebrewEngineAnalysisResult(
            input_text=text,
            syntax_eval=syntax_res,
            phonology_eval=phono_res,
            pragmatic_eval=prag_res,
            editorial_eval=edit_res,
            matrix_status=matrix_res,
            overall_linguistic_score=overall,
            amsv_synced=True,
        )
