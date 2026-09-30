"""
Dutch V2 Syntax & Clause Structure Cognitive Analyzer
"""

from typing import Dict, Any, List
from ..skills.tokenization import DutchTokenizer
from ..skills.pos_tagging import DutchPOSTagger
from ..skills.v2_syntax_engine import DutchV2SyntaxEngine

class DutchV2SyntaxAnalyzer:
    def __init__(self):
        self.tokenizer = DutchTokenizer()
        self.pos_tagger = DutchPOSTagger()
        self.syntax_engine = DutchV2SyntaxEngine()

    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = self.tokenizer.split_sentences(text)
        if not sentences:
            return {
                "text": text,
                "sentences_analyzed": 0,
                "v2_valid": True,
                "inversion_detected": False,
                "subordinate_sov_valid": True,
                "syntax_score": 100,
                "violations": []
            }

        all_violations = []
        inversion_detected = False
        all_v2_valid = True
        all_sov_valid = True
        score_sum = 0

        for s in sentences:
            tokens = self.tokenizer.tokenize(s)
            tagged = self.pos_tagger.tag(tokens)
            clause_analysis = self.syntax_engine.analyze_clause(tokens, tagged)

            if not clause_analysis["v2_valid"]:
                all_v2_valid = False
            if not clause_analysis["subordinate_sov_valid"]:
                all_sov_valid = False
            if clause_analysis["inversion_active"]:
                inversion_detected = True

            all_violations.extend(clause_analysis["errors"])
            score_sum += clause_analysis["syntax_score"]

        avg_score = int(score_sum / len(sentences)) if sentences else 100

        return {
            "text": text,
            "sentences_analyzed": len(sentences),
            "v2_valid": all_v2_valid,
            "inversion_detected": inversion_detected,
            "subordinate_sov_valid": all_sov_valid,
            "syntax_score": avg_score,
            "violations": all_violations
        }
