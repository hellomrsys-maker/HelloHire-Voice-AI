"""
Vietnamese Kinship Deixis Engine
Resolves, validates, and audits interpersonal kinship address terms and social symmetry.
"""

from typing import Dict, Any, List, Optional, Tuple

RECIPROCAL_PAIRS = {
    ("em", "anh"): "younger_to_older_male",
    ("anh", "em"): "older_male_to_younger",
    ("em", "chị"): "younger_to_older_female",
    ("chị", "em"): "older_female_to_younger",
    ("cháu", "ông"): "grandchild_to_grandfather",
    ("ông", "cháu"): "grandfather_to_grandchild",
    ("cháu", "bà"): "grandchild_to_grandmother",
    ("bà", "cháu"): "grandmother_to_grandchild",
    ("cháu", "bác"): "youth_to_elder",
    ("cháu", "chú"): "youth_to_uncle",
    ("cháu", "cô"): "youth_to_aunt_or_teacher",
    ("con", "bố"): "child_to_father",
    ("con", "mẹ"): "child_to_mother"
}

KINSHIP_PRONOUNS = {
    "anh", "chị", "em", "ông", "bà", "cháu", "cô", "chú", "bác", "con", "bố", "mẹ"
}

class VietnameseKinshipEngine:
    """
    Validates symmetrical reciprocal address pairs in Vietnamese discourse.
    """

    def is_valid_reciprocal_pair(self, speaker_term: str, listener_term: str) -> bool:
        """
        Checks if (speaker_term, listener_term) is a culturally valid reciprocal pair.
        (e.g., em - anh, cháu - ông, con - mẹ)
        """
        s = speaker_term.lower().strip()
        l = listener_term.lower().strip()
        return (s, l) in RECIPROCAL_PAIRS

    def extract_kinship_terms(self, text: str) -> List[str]:
        """Extracts kinship terms used as pronouns in the input text."""
        words = text.lower().split()
        return [w.strip(",.?!:;") for w in words if w.strip(",.?!:;") in KINSHIP_PRONOUNS]

    def audit_kinship_consistency(self, speaker_term: str, listener_term: str) -> Dict[str, Any]:
        """Audits whether an interaction conforms to reciprocal kinship rules."""
        is_valid = self.is_valid_reciprocal_pair(speaker_term, listener_term)
        relation = RECIPROCAL_PAIRS.get((speaker_term.lower(), listener_term.lower()), "unknown_or_asymmetric")
        
        return {
            "speaker_term": speaker_term,
            "listener_term": listener_term,
            "is_reciprocal_valid": is_valid,
            "relationship": relation
        }
