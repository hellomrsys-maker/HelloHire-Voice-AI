"""
Dutch Grammar Checking Task Pipeline
Orchestrates V2 syntax checking, gender concordance, diminutive invariants,
and adjective inflection validation.
"""

from typing import Dict, Any, List
from ..analysis.v2_syntax_analyzer import DutchV2SyntaxAnalyzer
from ..analysis.diminutive_gender_analyzer import DutchDiminutiveGenderAnalyzer
from ..analysis.adjective_concord_analyzer import DutchAdjectiveConcordAnalyzer
from ..skills.tokenization import DutchTokenizer

class DutchGrammarChecker:
    def __init__(self):
        self.syntax_analyzer = DutchV2SyntaxAnalyzer()
        self.gender_analyzer = DutchDiminutiveGenderAnalyzer()
        self.adjective_analyzer = DutchAdjectiveConcordAnalyzer()
        self.tokenizer = DutchTokenizer()

    def check(self, text: str) -> Dict[str, Any]:
        syntax_res = self.syntax_analyzer.analyze(text)
        gender_res = self.gender_analyzer.analyze(text)
        adj_res = self.adjective_analyzer.analyze(text)

        # Check IJ capitalization invariant
        orthography_errors = []
        tokens = self.tokenizer.tokenize(text)
        for tok in tokens:
            if tok.startswith("Ij") and len(tok) > 2 and tok[2].islower():
                orthography_errors.append(
                    f"IJ Capitalization Violation: Dutch digraph 'IJ' must be capitalized as a single unit ('IJ...'), not '{tok}'."
                )

        all_errors = syntax_res["violations"] + gender_res["gender_errors"] + adj_res["errors"] + orthography_errors
        is_valid = len(all_errors) == 0

        # Weighted overall score
        score = int(0.4 * syntax_res["syntax_score"] + 0.3 * gender_res["gender_score"] + 0.3 * adj_res["adjective_concord_score"])
        if not is_valid and score > 85:
            score = 80

        return {
            "text": text,
            "is_valid": is_valid,
            "overall_score": score,
            "syntax_status": {
                "v2_valid": syntax_res["v2_valid"],
                "subordinate_sov_valid": syntax_res["subordinate_sov_valid"],
                "inversion_detected": syntax_res["inversion_detected"]
            },
            "gender_status": {
                "concord_valid": gender_res["concord_valid"],
                "diminutive_count": gender_res["diminutive_count"]
            },
            "adjective_status": {
                "concord_valid": adj_res["concord_valid"]
            },
            "all_errors": all_errors
        }
