"""
Mandarin Classifier Agreement Checker.
Deep diagnostic checker for nominal classifier compatibility.
"""

from typing import Dict, Any, List
from ..skills.classifier_engine import ClassifierEngine


class ClassifierAgreementChecker:
    """
    Validates noun-classifier pairs and provides corrections.
    """

    def __init__(self):
        self.engine = ClassifierEngine()

    def check_phrase(self, numeral_str: str, classifier: str, noun: str) -> Dict[str, Any]:
        res = self.engine.verify_collocation(classifier, noun)
        phrase = f"{numeral_str}{classifier}{noun}"
        correct_phrase = f"{numeral_str}{res['recommended_classifiers'][0]}{noun}" if not res["is_valid"] else phrase

        return {
            "phrase": phrase,
            "is_correct": res["is_valid"],
            "suggested_correction": None if res["is_valid"] else correct_phrase,
            "recommended_classifiers": res["recommended_classifiers"],
        }
