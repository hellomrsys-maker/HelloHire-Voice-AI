"""
Bengali Case Engine: Manages the four-case nominal declension system
(Nominative, Objective -ke, Genitive -er/-r, Locative -te/-e/-y),
Differential Object Marking (DOM), and postpositional case governance.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class BengaliCaseEngine:
    """
    Handles case inflection, Differential Object Marking, and postpositional governance.
    """

    PRONOUN_CASES = {
        "আমি": { "objective": "আমাকে", "genitive": "আমার", "locative": "আমাতে" },
        "তুমি": { "objective": "তোমাকে", "genitive": "তোমার", "locative": "তোমাতে" },
        "তুই": { "objective": "তোকে", "genitive": "তোর", "locative": "তোতে" },
        "আপনি": { "objective": "আপনাকে", "genitive": "আপনার", "locative": "আাপনাতে" },
        "সে": { "objective": "তাকে", "genitive": "তার", "locative": "তাতে" },
        "তিনি": { "objective": "তাঁকে", "genitive": "তাঁর", "locative": "তাঁতে" },
        "আমরা": { "objective": "আমাদের", "genitive": "আমাদের", "locative": "আমাদেরে" },
        "তোমরা": { "objective": "তোমাদের", "genitive": "তোমাদের", "locative": "তোমাদেরে" },
        "তারা": { "objective": "তাদের", "genitive": "তাদের", "locative": "তাদেরে" },
        "তাঁরা": { "objective": "তাঁদের", "genitive": "তাঁদের", "locative": "তাঁদেরে" }
    }

    VOWEL_SIGNS = {"া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ", "য়"}

    GENITIVE_GOVERNING_POSTPOSITIONS = {
        "জন্য", "সাথে", "সঙ্গে", "কাছে", "সামনে", "পিছনে", "ভিতরে", "বাইরে",
        "উপরে", "নিচে", "পরে", "কারণে", "বদলে"
    }

    NOMINATIVE_GOVERNING_POSTPOSITIONS = {
        "দিয়ে", "থেকে", "হতে", "পর্যন্ত"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "case_postposition_matrix.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)

    def is_vowel_stem(self, noun: str) -> bool:
        """Determines whether a noun ends in a vowel sound or vowel sign."""
        if not noun:
            return False
        last_char = noun[-1]
        return last_char in self.VOWEL_SIGNS or last_char in ("আ", "ই", "ঈ", "উ", "ঊ", "এ", "ও")

    def inflect_case(self, noun: str, case: str = "nominative") -> str:
        """
        Inflects a noun or pronoun into the target case.
        Cases: 'nominative', 'objective', 'genitive', 'locative'.
        """
        if not noun:
            return ""
        
        # Check pronoun table
        if noun in self.PRONOUN_CASES:
            if case == "nominative":
                return noun
            return self.PRONOUN_CASES[noun].get(case, noun)
        
        if case == "nominative":
            return noun
        elif case == "objective":
            return f"{noun}কে"
        elif case == "genitive":
            if self.is_vowel_stem(noun):
                return f"{noun}র"
            else:
                return f"{noun}ের"
        elif case == "locative":
            if self.is_vowel_stem(noun):
                if noun.endswith("া"):
                    return f"{noun}য়"
                return f"{noun}তে"
            else:
                return f"{noun}ে"
        
        return noun

    def validate_differential_object_marking(self, noun: str, is_animate: bool, has_ke: bool) -> Tuple[bool, str]:
        """
        Differential Object Marking: Animate/definite objects should be marked with -ke,
        inanimate bare objects should generally be unmarked.
        """
        if is_animate and not has_ke:
            return False, f"Animate specific direct object '{noun}' requires objective case marker '-কে'."
        if not is_animate and has_ke:
            return False, f"Inanimate generic direct object '{noun}' should not take objective '-কে'."
        return True, "Differential Object Marking is valid."

    def validate_postposition_governor(self, preceding_token: str, postposition: str) -> Tuple[bool, str]:
        """
        Validates case agreement between postposition and preceding noun/pronoun.
        """
        if postposition in self.GENITIVE_GOVERNING_POSTPOSITIONS:
            # Must end in genitive 'র' or 'ের' or pronoun genitive
            if not (preceding_token.endswith("র") or preceding_token in ("আমার", "তোমার", "তোর", "আপনার", "তার", "তাঁর", "আমাদের", "তোমাদের", "তাদের", "তাঁদের")):
                return False, f"Postposition '{postposition}' requires preceding noun in Genitive case (-র/-ের); found '{preceding_token}'."
        return True, f"Postposition '{postposition}' case governance is valid."
