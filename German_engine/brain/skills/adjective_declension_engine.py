"""
German Engine — Adjective Declension Skill
Handles inflection generation and validation across Strong, Weak, and Mixed declension paradigms.
"""

from typing import Dict, Any, Optional, Tuple, List

DECLENSION_TABLE = {
    "weak": {
        "masculine": {"nominative": "e",  "accusative": "en", "dative": "en", "genitive": "en"},
        "feminine":  {"nominative": "e",  "accusative": "e",  "dative": "en", "genitive": "en"},
        "neuter":    {"nominative": "e",  "accusative": "e",  "dative": "en", "genitive": "en"},
        "plural":    {"nominative": "en", "accusative": "en", "dative": "en", "genitive": "en"}
    },
    "mixed": {
        "masculine": {"nominative": "er", "accusative": "en", "dative": "en", "genitive": "en"},
        "feminine":  {"nominative": "e",  "accusative": "e",  "dative": "en", "genitive": "en"},
        "neuter":    {"nominative": "es", "accusative": "es", "dative": "en", "genitive": "en"},
        "plural":    {"nominative": "en", "accusative": "en", "dative": "en", "genitive": "en"}
    },
    "strong": {
        "masculine": {"nominative": "er", "accusative": "en", "dative": "em", "genitive": "en"},
        "feminine":  {"nominative": "e",  "accusative": "e",  "dative": "er", "genitive": "er"},
        "neuter":    {"nominative": "es", "accusative": "es", "dative": "em", "genitive": "en"},
        "plural":    {"nominative": "e",  "accusative": "e",  "dative": "en", "genitive": "er"}
    }
}

DEFINITE_DETERMINERS = {
    "der", "die", "das", "den", "dem", "des",
    "dieser", "diese", "dieses", "diesen", "diesem",
    "jener", "jene", "jenes", "jeder", "jede", "jedes",
    "alle", "beide", "welcher", "welche", "welches"
}

MIXED_DETERMINERS = {
    "ein", "eine", "einen", "einem", "einer", "eines",
    "kein", "keine", "keinen", "keinem", "keiner", "keines",
    "mein", "meine", "meinen", "meinem", "meiner", "meines",
    "dein", "deine", "deinen", "deinem", "deiner", "deines",
    "sein", "seine", "seinen", "seinem", "seiner", "seines",
    "ihr", "ihre", "ihren", "ihrem", "ihrer", "ihres",
    "unser", "unsere", "unseren", "unserem", "unserer", "unseres",
    "euer", "eure", "euren", "eurem", "eurer", "eures",
    "Ihr", "Ihre", "Ihren", "Ihrem", "Ihrer", "Ihres"
}

def determine_declension_type(determiner: Optional[str]) -> str:
    """Determine whether weak, mixed, or strong declension applies based on determiner."""
    if not determiner:
        return "strong"
    det_lower = determiner.lower()
    if det_lower in DEFINITE_DETERMINERS:
        return "weak"
    if det_lower in MIXED_DETERMINERS:
        return "mixed"
    return "strong"

def inflect_adjective(base_adj: str, gender: str, case: str, determiner: Optional[str] = None) -> str:
    """
    Inflect base adjective stem according to gender, case, and determiner.
    gender: 'masculine' | 'feminine' | 'neuter' | 'plural'
    case: 'nominative' | 'accusative' | 'dative' | 'genitive'
    """
    # Stem clean up (e.g. teuer -> teur-, dunkel -> dunkl-)
    stem = base_adj
    if stem.endswith("el"):
        stem = stem[:-2] + "l"
    elif stem.endswith("er") and stem not in {"schwer", "leer"}:
        stem = stem[:-2] + "r"
        
    decl_type = determine_declension_type(determiner)
    ending = DECLENSION_TABLE[decl_type][gender.lower()][case.lower()]
    return stem + ending

def validate_adjective_agreement(determiner: Optional[str], surface_adj: str, gender: str, case: str) -> Dict[str, Any]:
    """
    Validate whether surface_adj matches the expected inflection given determiner, gender, and case.
    """
    decl_type = determine_declension_type(determiner)
    expected_ending = DECLENSION_TABLE[decl_type][gender.lower()][case.lower()]
    
    # Check if surface_adj ends with expected ending
    valid = surface_adj.lower().endswith(expected_ending)
    
    # Specific edge case: masculine accusative weak/mixed/strong MUST end in -en
    if gender.lower() == "masculine" and case.lower() == "accusative" and not surface_adj.lower().endswith("en"):
        valid = False
        
    return {
        "valid": valid,
        "declension_type": decl_type,
        "expected_ending": expected_ending,
        "surface_form": surface_adj,
        "determiner": determiner,
        "gender": gender,
        "case": case
    }
