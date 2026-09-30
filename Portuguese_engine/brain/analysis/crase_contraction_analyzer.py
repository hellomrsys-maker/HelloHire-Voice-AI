"""
Portuguese Crase & Contraction Analyzer: Evaluates valid usage of the grave accent (Crase)
and flags prohibited crase before masculine nouns and verbs.
"""

from typing import Dict, Any, List
from ..skills.contraction_engine import PortugueseContractionEngine
from ..skills.tokenization import PortugueseTokenizer


class CraseContractionAnalyzer:
    """
    Diagnoses crase and preposition contraction errors.
    """

    def __init__(self):
        self.tokenizer = PortugueseTokenizer()
        self.contraction_engine = PortugueseContractionEngine()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(sentence)
        diagnostics = []

        for i in range(len(tokens) - 1):
            tok = tokens[i].lower()
            nxt = tokens[i + 1].lower()

            # Check crase misuse (à / às)
            if tok in ("à", "às"):
                valid, msg = self.contraction_engine.validate_crase(following_word=nxt, has_crase=True)
                if not valid:
                    diagnostics.append({
                        "token": f"{tokens[i]} {tokens[i+1]}",
                        "error_type": "PROHIBITED_CRASE",
                        "message": msg
                    })

        is_valid = len(diagnostics) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - (len(diagnostics) * 0.40))

        return {
            "is_valid": is_valid,
            "crase_score": score,
            "diagnostics": diagnostics
        }
