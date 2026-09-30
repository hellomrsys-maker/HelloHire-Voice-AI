"""
Polish Grammar Checking Task Pipeline
Orchestrates Genitive of Negation validation, honorific concord checking,
sibilant orthography auditing, and case government verification.
"""

from typing import Dict, Any, List
from ..analysis.genitive_negation_analyzer import PolishGenitiveNegationAnalyzer
from ..analysis.honorific_register_analyzer import PolishHonorificRegisterAnalyzer
from ..skills.phonology_sibilant_engine import PolishPhonologySibilantEngine
from ..skills.tokenization import PolishTokenizer

class PolishGrammarChecker:
    def __init__(self):
        self.negation_analyzer = PolishGenitiveNegationAnalyzer()
        self.honorific_analyzer = PolishHonorificRegisterAnalyzer()
        self.phonology_engine = PolishPhonologySibilantEngine()
        self.tokenizer = PolishTokenizer()

    def check(self, text: str) -> Dict[str, Any]:
        neg_res = self.negation_analyzer.analyze(text)
        hon_res = self.honorific_analyzer.analyze(text)
        tokens = self.tokenizer.tokenize(text)
        ortho_res = self.phonology_engine.check_orthography(tokens)

        all_errors = neg_res["violations"] + hon_res["errors"] + ortho_res["warnings"]
        is_valid = len(all_errors) == 0

        # Overall composite score
        score = int(0.4 * neg_res["case_score"] + 0.3 * hon_res["score"] + 0.3 * ortho_res["orthography_score"])
        if not is_valid and score > 85:
            score = 75

        return {
            "text": text,
            "is_valid": is_valid,
            "overall_score": score,
            "genitive_of_negation": {
                "valid": neg_res["is_valid"],
                "negated_clauses": neg_res["negated_clauses"]
            },
            "honorific_concord": {
                "valid": hon_res["concord_valid"],
                "register": hon_res["register"]
            },
            "orthography": {
                "valid": ortho_res["is_valid"],
                "score": ortho_res["orthography_score"]
            },
            "all_errors": all_errors
        }
