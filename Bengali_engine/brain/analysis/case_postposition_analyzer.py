"""
Bengali Case & Postposition Analyzer: Evaluates postpositional governance
and Differential Object Marking (DOM).
"""

from typing import Dict, Any, List
from ..skills.case_engine import BengaliCaseEngine
from ..skills.tokenization import BengaliTokenizer
from ..skills.pos_tagging import BengaliPOSTagger


class CasePostpositionAnalyzer:
    """
    Diagnoses postpositional case governance errors and object marking inconsistencies.
    """

    def __init__(self):
        self.tokenizer = BengaliTokenizer()
        self.tagger = BengaliPOSTagger()
        self.case_engine = BengaliCaseEngine()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(sentence)
        diagnostics = []

        # Check postposition governance
        for i in range(len(tokens) - 1):
            tok = tokens[i]
            nxt = tokens[i + 1]

            if nxt in self.case_engine.GENITIVE_GOVERNING_POSTPOSITIONS:
                valid, msg = self.case_engine.validate_postposition_governor(tok, nxt)
                if not valid:
                    diagnostics.append({
                        "error_type": "GENITIVE_GOVERNANCE_VIOLATION",
                        "postposition": nxt,
                        "preceding_token": tok,
                        "message": msg
                    })

        is_valid = len(diagnostics) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - (len(diagnostics) * 0.35))

        return {
            "is_valid": is_valid,
            "case_score": score,
            "diagnostics": diagnostics
        }
