"""
Tamil PNG Concord Engine.
Audits Person-Number-Gender (PNG) agreement between subject and finite verb,
supporting both combining vowel signs and independent vowel forms.
"""

from typing import Dict, Optional, Tuple

SUBJECT_VERB_CONCORD_MAP = {
    "நான்": ("1SG", ["ேன்", "என்", "ஏன்", "ேன"]),
    "நாம்": ("1PL", ["ோம்", "ஓம்"]),
    "நாங்கள்": ("1PL", ["ோம்", "ஓம்"]),
    "நீ": ("2SG", ["ாய்", "ஆய்"]),
    "நீங்கள்": ("2PL", ["ீர்கள்", "ீங்க", "ஈர்கள்"]),
    "அவன்": ("3MSG", ["ான்", "ஆன்"]),
    "அவள்": ("3FSG", ["ாள்", "ஆள்"]),
    "அவர்": ("3HON", ["ார்", "ஆர்"]),
    "அவர்கள்": ("3PL", ["ார்கள்", "ாங்க", "ஆர்கள்"]),
    "அது": ("3NSG", ["அது", "து"]),
    "அவை": ("3NPL", ["அன", "ன"])
}

def check_png_concord(subject: str, verb: str) -> Dict[str, any]:
    """
    Verifies that the finite verb bears the appropriate PNG suffix for the subject.
    """
    if subject in SUBJECT_VERB_CONCORD_MAP:
        png_label, expected_suffixes = SUBJECT_VERB_CONCORD_MAP[subject]
        
        # Check if verb ends with any expected suffix
        matches = any(verb.endswith(suff) for suff in expected_suffixes)
        
        return {
            "subject": subject,
            "verb": verb,
            "png_category": png_label,
            "expected_suffixes": expected_suffixes,
            "is_concordant": matches,
            "error": None if matches else f"Subject '{subject}' ({png_label}) does not agree with verb '{verb}'"
        }
        
    # Default to valid if subject is non-pronominal noun
    return {
        "subject": subject,
        "verb": verb,
        "png_category": "NOUN_3RD",
        "expected_suffixes": ["ான்", "ாள்", "ார்", "ார்கள்", "து"],
        "is_concordant": True,
        "error": None
    }
