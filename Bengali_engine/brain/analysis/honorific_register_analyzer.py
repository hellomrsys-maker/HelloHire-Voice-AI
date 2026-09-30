"""
Bengali Honorific & Register Analyzer: Evaluates subject-verb politeness concord
and diagnoses Guru-Chondali stylistic solecisms.
"""

from typing import Dict, Any, List
from ..skills.pragmatics_engine import BengaliPragmaticsEngine
from ..skills.parsing import BengaliParser
from ..skills.tokenization import BengaliTokenizer


class HonorificRegisterAnalyzer:
    """
    Validates pragmatic consistency and flags register solecisms.
    """

    def __init__(self):
        self.tokenizer = BengaliTokenizer()
        self.pragmatics_engine = BengaliPragmaticsEngine()
        self.parser = BengaliParser()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(sentence)
        diagnostics = []

        # 1. Guru-Chondali check
        gc_violations = self.pragmatics_engine.detect_guru_chondali(tokens)
        for v in gc_violations:
            diagnostics.append({
                "error_type": "GURU_CHONDALI_DOSH",
                "message": v["message"],
                "sadhu_tokens": v["sadhu_tokens"],
                "cholito_tokens": v["cholito_tokens"]
            })

        # 2. Subject-verb agreement check
        parsed = self.parser.parse_sentence(sentence)
        if not parsed["agreement_valid"]:
            diagnostics.append({
                "error_type": "HONORIFIC_AGREEMENT_MISMATCH",
                "subject": parsed["subject"],
                "verb": parsed["verb"],
                "detected_tier": parsed["agreement_tier"],
                "message": f"Subject '{parsed['subject']}' conflicts with verbal inflection '{parsed['verb']}'."
            })

        pragmatic_eval = self.pragmatics_engine.evaluate_pragmatics(tokens)

        is_valid = len(diagnostics) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - (len(diagnostics) * 0.4))

        return {
            "is_valid": is_valid,
            "honorific_score": score,
            "detected_tier": pragmatic_eval["tier"],
            "politeness_score": pragmatic_eval["politeness_score"],
            "register": pragmatic_eval["register"],
            "diagnostics": diagnostics
        }
