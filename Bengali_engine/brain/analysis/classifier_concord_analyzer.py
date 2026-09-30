"""
Bengali Classifier Concord Analyzer: Diagnoses agreement anomalies between nouns,
numerals, and nominal classifiers (-Ta, -Ti, -gulo, -guli, -khana, -khani, -jon).
"""

from typing import Dict, Any, List
from ..skills.classifier_engine import BengaliClassifierEngine
from ..skills.tokenization import BengaliTokenizer


class ClassifierConcordAnalyzer:
    """
    Analyzes and validates nominal classifier concord across a sentence.
    """

    def __init__(self):
        self.tokenizer = BengaliTokenizer()
        self.clf_engine = BengaliClassifierEngine()

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(sentence)
        diagnostics = []

        for tok in tokens:
            clf_info = self.clf_engine.analyze_classifier(tok)
            if clf_info["has_classifier"]:
                noun = clf_info["base_noun"]
                clf = clf_info["classifier"]
                valid, reason = self.clf_engine.validate_animacy(noun, clf)
                if not valid:
                    diagnostics.append({
                        "token": tok,
                        "noun": noun,
                        "classifier": clf,
                        "error_type": "CLASSIFIER_ANIMACY_MISMATCH",
                        "message": reason
                    })

        is_valid = len(diagnostics) == 0
        score = 1.0 if is_valid else max(0.0, 1.0 - (len(diagnostics) * 0.3))

        return {
            "is_valid": is_valid,
            "classifier_score": score,
            "diagnostics": diagnostics
        }
