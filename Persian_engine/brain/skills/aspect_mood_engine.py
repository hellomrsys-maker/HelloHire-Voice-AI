"""
Persian Aspect & Mood Engine
Validates durative aspect (mi-), subjunctive mood (be-), imperative, and negation.
"""

from typing import Dict, Any, List
from Persian_engine.brain.skills.tokenization import ZWNJ

class PersianAspectMoodEngine:
    """
    Evaluates aspectual and modal markers on Persian verbs.
    """

    def analyze_verb_form(self, verb_token: str) -> Dict[str, Any]:
        """
        Decomposes a verbal surface form into prefix, stem, ending, aspect, mood, and polarity.
        """
        token = verb_token.strip()
        is_negative = False
        mood = "indicative"
        aspect = "simple"
        
        # Check negative
        if token.startswith(f"نمی{ZWNJ}") or token.startswith("نمی‌") or token.startswith("نمی"):
            is_negative = True
            aspect = "durative_continuous"
        elif token.startswith(f"می{ZWNJ}") or token.startswith("می‌") or token.startswith("می"):
            aspect = "durative_continuous"
        elif token.startswith("ن"):
            is_negative = True
            mood = "subjunctive_or_simple"
        elif token.startswith("ب"):
            mood = "subjunctive"

        # Check imperative
        # Often marked by 'be-' without personal ending or with -id for plural
        is_imperative = False
        if token.startswith("ب") and (token.endswith("ید") or not any(token.endswith(e) for e in ["م", "ی", "د", "یم", "ند"])):
            is_imperative = True

        return {
            "token": token,
            "is_negative": is_negative,
            "aspect": aspect,
            "mood": mood,
            "is_imperative": is_imperative,
            "has_zwnj": ZWNJ in token
        }

    def validate_subjunctive_clause(self, matrix_verb: str, subordinate_verb: str) -> bool:
        """
        Checks if a modal matrix verb (like خواستن - want, توانستن - can, باید - must)
        is properly followed by a subjunctive verb in the subordinate clause.
        """
        modal_triggers = {"باید", "شاید", "می‌خواهم", "می‌خواهد", "می‌تواند", "می‌توانم", "لازم است"}
        if any(trig in matrix_verb for trig in modal_triggers):
            sub_analysis = self.analyze_verb_form(subordinate_verb)
            return sub_analysis["mood"] == "subjunctive"
        return True
