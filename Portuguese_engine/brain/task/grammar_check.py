"""
Portuguese Grammar Check Task: Comprehensive proofreading pipeline evaluating
clitic placement, crase errors, contraction fusions, and mood concordance.
"""

from typing import Dict, Any, List
from ..analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from ..analysis.crase_contraction_analyzer import CraseContractionAnalyzer
from ..analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer


class PortugueseGrammarCheckTask:
    """
    Unified grammatical and orthographic proofreading task for Portuguese.
    """

    def __init__(self):
        self.clitic_analyzer = CliticPlacementAnalyzer()
        self.crase_analyzer = CraseContractionAnalyzer()
        self.subjunctive_analyzer = SubjunctiveConcordAnalyzer()

    def run(self, text: str) -> Dict[str, Any]:
        clitic_res = self.clitic_analyzer.analyze_sentence(text)
        crase_res = self.crase_analyzer.analyze_sentence(text)
        sub_res = self.subjunctive_analyzer.analyze_sentence(text)

        all_diagnostics = (
            clitic_res["diagnostics"] +
            crase_res["diagnostics"] +
            sub_res["diagnostics"]
        )

        composite_score = (
            clitic_res["clitic_score"] * 0.40 +
            crase_res["crase_score"] * 0.40 +
            sub_res["subjunctive_score"] * 0.20
        )

        return {
            "is_valid": len(all_diagnostics) == 0,
            "overall_score": round(min(1.0, composite_score), 3),
            "diagnostics_count": len(all_diagnostics),
            "diagnostics": all_diagnostics
        }
