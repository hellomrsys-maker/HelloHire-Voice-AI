"""
Polish Genitive of Negation Cognitive Analyzer
Validates that direct objects under verbal negation take the Genitive case.
"""

from typing import Dict, Any, List
from ..skills.tokenization import PolishTokenizer
from ..skills.genitive_negation_engine import PolishGenitiveNegationEngine

class PolishGenitiveNegationAnalyzer:
    def __init__(self):
        self.tokenizer = PolishTokenizer()
        self.engine = PolishGenitiveNegationEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = self.tokenizer.split_sentences(text)
        all_errors = []
        is_all_valid = True
        negated_clauses = 0

        for s in sentences:
            tokens = self.tokenizer.tokenize(s)
            res = self.engine.verify_sentence(tokens)
            if res["is_negated"]:
                negated_clauses += 1
                if not res["genitive_of_negation_valid"]:
                    is_all_valid = False
                    all_errors.extend(res["errors"])

        score = 100 if is_all_valid else max(20, 100 - len(all_errors) * 40)

        return {
            "text": text,
            "negated_clauses": negated_clauses,
            "is_valid": is_all_valid,
            "case_score": score,
            "violations": all_errors
        }
