"""
Bengali Grammar Check Task: Comprehensive proofreading pipeline evaluating
classifier concord, postpositional governance, honorific agreement, and Guru-Chondali solecisms.
"""

from typing import Dict, Any, List
from ..analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer
from ..analysis.case_postposition_analyzer import CasePostpositionAnalyzer
from ..analysis.honorific_register_analyzer import HonorificRegisterAnalyzer
from ..skills.tokenization import BengaliTokenizer


class BengaliGrammarCheckTask:
    """
    Unified proofreading task for Bengali text.
    """

    def __init__(self):
        self.tokenizer = BengaliTokenizer()
        self.clf_analyzer = ClassifierConcordAnalyzer()
        self.case_analyzer = CasePostpositionAnalyzer()
        self.honorific_analyzer = HonorificRegisterAnalyzer()

    def run(self, text: str) -> Dict[str, Any]:
        """
        Executes complete grammatical audit on text.
        """
        clf_res = self.clf_analyzer.analyze_sentence(text)
        case_res = self.case_analyzer.analyze_sentence(text)
        hon_res = self.honorific_analyzer.analyze_sentence(text)

        all_diagnostics = (
            clf_res["diagnostics"] +
            case_res["diagnostics"] +
            hon_res["diagnostics"]
        )

        # Check terminal punctuation (Dā̃ṛi '।')
        tokens = self.tokenizer.tokenize(text)
        has_proper_terminal = False
        if tokens and tokens[-1] in ("।", "॥", "?", "!"):
            has_proper_terminal = True
        elif text.strip().endswith("।"):
            has_proper_terminal = True
        else:
            all_diagnostics.append({
                "error_type": "PUNCTUATION_DARI_MISSING",
                "message": "Declarative Bengali sentences should terminate with a Dā̃ṛi ('।')."
            })

        # Calculate composite grammar score
        composite_score = (
            clf_res["classifier_score"] * 0.3 +
            case_res["case_score"] * 0.3 +
            hon_res["honorific_score"] * 0.3 +
            (0.1 if has_proper_terminal else 0.0)
        )

        return {
            "is_valid": len(all_diagnostics) == 0,
            "overall_score": round(min(1.0, composite_score), 3),
            "diagnostics_count": len(all_diagnostics),
            "diagnostics": all_diagnostics,
            "detected_tier": hon_res["detected_tier"],
            "register": hon_res["register"]
        }
