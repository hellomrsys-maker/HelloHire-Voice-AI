"""
Portuguese Clitic Placement Analyzer: Diagnoses clitic positioning errors,
próclise attractor violations, and allomorphy failures.
"""

from typing import Dict, Any, List
from ..skills.clitic_engine import PortugueseCliticEngine
from ..skills.tokenization import PortugueseTokenizer


class CliticPlacementAnalyzer:
    """
    Analyzes clitic placement validity in sentences.
    """

    def __init__(self):
        self.tokenizer = PortugueseTokenizer()
        self.clitic_engine = PortugueseCliticEngine()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(sentence)
        diagnostics = []

        for i, tok in enumerate(tokens):
            if "-" in tok:
                stem, clitic = self.tokenizer.split_clitic(tok)
                preceding = tokens[:i]
                valid, reason = self.clitic_engine.validate_placement(
                    preceding_tokens=preceding,
                    verb=stem,
                    clitic=clitic,
                    is_enclitic=True
                )
                if not valid:
                    diagnostics.append({
                        "token": tok,
                        "verb_stem": stem,
                        "clitic": clitic,
                        "error_type": "CLITIC_PLACEMENT_VIOLATION",
                        "message": reason
                    })

        is_valid = len(diagnostics) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - (len(diagnostics) * 0.35))

        return {
            "is_valid": is_valid,
            "clitic_score": score,
            "diagnostics": diagnostics
        }
