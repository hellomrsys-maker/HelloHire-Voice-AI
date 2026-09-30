"""
Bengali Classifier Engine: Manages nominal classifiers (নির্দেশক - Nirdeshok),
definiteness enclitics, numeral counters, and semantic animacy constraints.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class BengaliClassifierEngine:
    """
    Analyzes, attaches, and validates Bengali nominal classifiers (-Ta, -Ti, -gulo, -guli, -khana, -khani, -jon).
    """

    NUMERAL_WORDS = {
        1: "এক", 2: "দুই", 3: "তিন", 4: "চার", 5: "পাঁচ",
        6: "ছয়", 7: "সাত", 8: "আট", 9: "নয়", 10: "দশ"
    }

    HUMAN_NOUNS = {
        "ছাত্র", "ছাত্রী", "শিক্ষক", "শিক্ষিকা", "মানুষ", "লোক", "বন্ধু", "মেয়ে",
        "ছেলে", "শিশু", "ডাক্তার", "বাবা", "মা", "ভাই", "বোন", "কবি", "লেখক"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "classifier_matrix.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        
        self.classifiers = self.db.get("classifiers", {})

    def analyze_classifier(self, token: str) -> Dict[str, Any]:
        """
        Deconstructs a nominal token to detect any attached classifier.
        """
        for clf, info in self.classifiers.items():
            if token.endswith(clf) and len(token) > len(clf):
                base_noun = token[:-len(clf)]
                return {
                    "has_classifier": True,
                    "base_noun": base_noun,
                    "classifier": clf,
                    "type": info.get("type"),
                    "animacy": info.get("animacy"),
                    "politeness": info.get("politeness")
                }
        return {
            "has_classifier": False,
            "base_noun": token,
            "classifier": None,
            "type": None,
            "animacy": None,
            "politeness": None
        }

    def attach_classifier(self, noun: str, classifier: str = "টা", count: Optional[int] = None) -> str:
        """
        Attaches a classifier to a noun or numeral.
        If count is specified: 'পাঁচজন ছাত্র' / 'দুটি বই'.
        If count is None: 'বইটা' (the book).
        """
        if count is not None:
            num_word = self.NUMERAL_WORDS.get(count, str(count))
            # If 2 + Ta -> দুটো
            if count == 2 and classifier == "টা":
                return f"দুটো {noun}"
            return f"{num_word}{classifier} {noun}"
        
        return f"{noun}{classifier}"

    def validate_animacy(self, noun: str, classifier: str) -> Tuple[bool, str]:
        """
        Validates semantic animacy agreement between noun and classifier.
        Returns: (is_valid, explanation).
        """
        if classifier == "জন":
            if noun not in self.HUMAN_NOUNS and not noun.endswith(("ী", "ক", "র")):
                return False, f"Classifier 'জন' is strictly reserved for human referents; '{noun}' is inanimate or unknown."
        elif classifier in ("খানা", "খানি"):
            if noun in self.HUMAN_NOUNS:
                return False, f"Flat-object classifier '{classifier}' cannot be applied to human referent '{noun}'."
        
        return True, "Classifier concord valid."
