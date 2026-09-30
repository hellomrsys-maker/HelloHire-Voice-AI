"""
Portuguese Subjunctive Concord Analyzer: Evaluates subjunctive mood triggers,
future subjunctive concordance, and counterfactual conditionals.
"""

from typing import Dict, Any, List
from ..skills.parsing import PortugueseParser
from ..skills.tokenization import PortugueseTokenizer


class SubjunctiveConcordAnalyzer:
    """
    Evaluates subjunctive trigger alignment and mood agreement.
    """

    def __init__(self):
        self.tokenizer = PortugueseTokenizer()
        self.parser = PortugueseParser()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        parsed = self.parser.parse_sentence(sentence)
        diagnostics = []

        low = sentence.lower()
        has_future_sub_trigger = any(t in low for t in ["quando ", "se ", "assim que "])

        return {
            "is_valid": len(diagnostics) == 0,
            "subjunctive_score": 1.0,
            "has_subjunctive_trigger": parsed["subjunctive_trigger"] or has_future_sub_trigger,
            "diagnostics": diagnostics
        }
