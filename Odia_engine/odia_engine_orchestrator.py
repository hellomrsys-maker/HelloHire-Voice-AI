"""
Odia Language Engine Master Orchestrator.
Unifies all 9 layers, 4 dedicated Sub-AIs, and Six-Language Matrix under The Zero-Bridge Synchronous Memory Rule.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from amsv.python.amsv_embedded import AMSVEmbeddedView

from .brain.sub_ais.syntax_sub_ai import OdiaSyntaxSubAI, OdiaSyntaxEvaluationResult
from .brain.sub_ais.phonology_sub_ai import OdiaPhonologySubAI, OdiaPhonologyEvaluationResult
from .brain.sub_ais.pragmatic_sub_ai import OdiaPragmaticSubAI, OdiaPragmaticEvaluationResult
from .brain.sub_ais.editorial_sub_ai import OdiaEditorialSubAI, OdiaEditorialEvaluationResult
from .six_language_matrix.python.odia_matrix_bridge import OdiaMatrixBridge


@dataclass
class OdiaEngineAnalysisResult:
    input_text: str
    syntax_eval: OdiaSyntaxEvaluationResult
    phonology_eval: OdiaPhonologyEvaluationResult
    pragmatic_eval: OdiaPragmaticEvaluationResult
    editorial_eval: OdiaEditorialEvaluationResult
    matrix_status: Dict[str, Any]
    overall_linguistic_score: float
    amsv_synced: bool


class OdiaEngineOrchestrator:
    """Master Orchestrator for Odia Language Processing & Cognitive Assessment."""

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None,
    ):
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.checkpoint_path = checkpoint_path

        # Dedicated Sub-AIs
        self.syntax_sub_ai = OdiaSyntaxSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.phonology_sub_ai = OdiaPhonologySubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.pragmatic_sub_ai = OdiaPragmaticSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)
        self.editorial_sub_ai = OdiaEditorialSubAI(amsv_view=self.amsv, checkpoint_path=checkpoint_path)

        # Six-Language Matrix Bridge
        self.matrix_bridge = OdiaMatrixBridge(amsv_view=self.amsv)

    def analyze(self, text: str) -> OdiaEngineAnalysisResult:
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

        return OdiaEngineAnalysisResult(
            input_text=text,
            syntax_eval=syntax_res,
            phonology_eval=phono_res,
            pragmatic_eval=prag_res,
            editorial_eval=edit_res,
            matrix_status=matrix_res,
            overall_linguistic_score=overall,
            amsv_synced=True,
        )
