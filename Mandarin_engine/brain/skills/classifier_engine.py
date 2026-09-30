"""
Mandarin Measure Word (量词) Resolution and Classifier Agreement Skill.
Verifies nominal shape classifiers, numeral collocations, and flags agreement mismatches.
"""

import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "measure_word_db.json")


class ClassifierEngine:
    """
    Validates noun-classifier concord and semantic shape agreement.
    """

    def __init__(self, db_path: Optional[str] = None):
        target = db_path or DB_PATH
        self.classifiers: Dict[str, Any] = {}
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self.classifiers = raw.get("classifiers", {})

        # Inverted index: noun -> valid classifiers
        self.noun_to_classifiers: Dict[str, List[str]] = {}
        for clf, data in self.classifiers.items():
            for noun in data.get("nouns", []):
                self.noun_to_classifiers.setdefault(noun, []).append(clf)

    def get_valid_classifiers_for_noun(self, noun: str) -> List[str]:
        """Returns valid classifiers for a specific noun."""
        valid = self.noun_to_classifiers.get(noun, ["个"])
        if "个" not in valid:
            valid.append("个")
        return valid

    def verify_collocation(self, classifier: str, noun: str) -> Dict[str, Any]:
        """Verifies whether a given classifier is appropriate for a noun."""
        valid_clfs = self.get_valid_classifiers_for_noun(noun)
        is_valid = classifier in valid_clfs
        clf_data = self.classifiers.get(classifier, {})

        return {
            "classifier": classifier,
            "noun": noun,
            "is_valid": is_valid,
            "recommended_classifiers": valid_clfs,
            "classifier_type": clf_data.get("type", "unknown"),
        }
