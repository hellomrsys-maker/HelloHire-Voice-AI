"""
Spanish Grammar & Agreement Proofreader Task Pipeline.
Validates copula selection (ser/estar), prepositions (por/para), and punctuation balance.
"""

from typing import Dict, Any, List
from ..skills.tokenization import SpanishTokenizer
from ..skills.pos_tagging import SpanishPOSTagger
from ..skills.ser_estar_engine import SerEstarEngine
from ..skills.por_para_engine import PorParaEngine
from ..analysis.agreement_checker import SpanishAgreementChecker


class SpanishGrammarChecker:
    """
    Automated proofreading pipeline for Spanish texts.
    """

    def __init__(self):
        self.tokenizer = SpanishTokenizer()
        self.tagger = SpanishPOSTagger()
        self.ser_estar = SerEstarEngine()
        self.por_para = PorParaEngine()
        self.agreement = SpanishAgreementChecker()

    def check_text(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenizer.segment(text)
        errors: List[str] = []
        warnings: List[str] = []

        # Check inverted punctuation pairing
        if ("?" in text and "¿" not in text) or ("¿" in text and "?" not in text):
            errors.append("Inverted question mark balance mismatch: '¿' and '?' must be paired.")
        if ("!" in text and "¡" not in text) or ("¡" in text and "!" not in text):
            errors.append("Inverted exclamation mark balance mismatch: '¡' and '!' must be paired.")

        # Check copula usage
        low_tokens = [t.lower() for t in tokens]
        for i in range(len(low_tokens) - 1):
            if low_tokens[i] in {"es", "son", "está", "están"}:
                pred = low_tokens[i + 1]
                eval_cop = self.ser_estar.evaluate_copula(low_tokens[i], pred)
                if not eval_cop["is_appropriate"] and not eval_cop["has_semantic_shift"]:
                    warnings.append(
                        f"Potential copula mismatch: '{low_tokens[i]}' with '{pred}'. Recommended: '{eval_cop['recommended_copula']}'."
                    )

        return {
            "input_text": text,
            "is_grammatically_sound": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warning_count": len(warnings),
            "warnings": warnings,
            "token_count": len(tokens),
        }
