"""
German Engine — Case Government Skill
Validates and identifies grammatical case government for prepositions and verbs.
"""

from typing import Dict, Any, List, Optional

ACCUSATIVE_PREPOSITIONS = {
    "bis", "durch", "für", "gegen", "ohne", "um", "wider"
}

DATIVE_PREPOSITIONS = {
    "aus", "bei", "mit", "nach", "seit", "von", "zu", "gegenüber", "außer", "gemäß", "samt"
}

GENITIVE_PREPOSITIONS = {
    "während", "wegen", "trotz", "anstatt", "statt", "außerhalb", "innerhalb",
    "oberhalb", "unterhalb", "diesseits", "jenseits", "inmitten", "unweit"
}

TWO_WAY_PREPOSITIONS = {
    "an", "auf", "hinter", "in", "neben", "über", "unter", "vor", "zwischen"
}

DATIVE_VERBS = {
    "helfen", "danken", "antworten", "gefallen", "gehören", "gratulieren",
    "passen", "schaden", "vertrauen", "widersprechen", "folgen", "drohen",
    "fehlen", "gelingen", "nützen", "schmecken", "wehtun", "zuhören"
}

GENITIVE_VERBS = {
    "gedenken", "bedürfen", "beschuldigen", "überführen", "anklagen", "entbehren"
}

# Mapping determiners to likely cases
DETERMINER_CASES = {
    "den": ["accusative_masculine", "dative_plural"],
    "dem": ["dative_masculine", "dative_neuter"],
    "des": ["genitive_masculine", "genitive_neuter"],
    "der": ["nominative_masculine", "dative_feminine", "genitive_feminine", "genitive_plural"],
    "die": ["nominative_feminine", "accusative_feminine", "nominative_plural", "accusative_plural"],
    "das": ["nominative_neuter", "accusative_neuter"],
    "einen": ["accusative_masculine"],
    "einem": ["dative_masculine", "dative_neuter"],
    "eines": ["genitive_masculine", "genitive_neuter"],
    "einer": ["dative_feminine", "genitive_feminine"],
    "eine": ["nominative_feminine", "accusative_feminine"],
    "ein": ["nominative_masculine", "nominative_neuter", "accusative_neuter"]
}

def get_preposition_governed_case(prep: str) -> str:
    """Return governed case: 'accusative', 'dative', 'genitive', or 'two_way'."""
    p = prep.lower()
    if p in ACCUSATIVE_PREPOSITIONS:
        return "accusative"
    if p in DATIVE_PREPOSITIONS:
        return "dative"
    if p in GENITIVE_PREPOSITIONS:
        return "genitive"
    if p in TWO_WAY_PREPOSITIONS:
        return "two_way"
    return "unknown"

def validate_prepositional_phrase(prep: str, article: str) -> Dict[str, Any]:
    """
    Check if the article following a preposition agrees with the preposition's case government.
    """
    governed = get_preposition_governed_case(prep)
    art_cases = DETERMINER_CASES.get(article.lower(), [])
    
    if governed == "unknown":
        return {"valid": True, "governed_case": "unknown", "article": article}
        
    if governed == "two_way":
        # Two-way prepositions permit both accusative and dative
        valid = any(c.startswith("accusative") or c.startswith("dative") for c in art_cases)
        return {
            "valid": valid,
            "governed_case": "two_way (accusative or dative)",
            "article": article,
            "detected_cases": art_cases
        }
        
    # Strict single-case prepositions
    valid = any(c.startswith(governed) for c in art_cases)
    return {
        "valid": valid,
        "governed_case": governed,
        "article": article,
        "detected_cases": art_cases
    }

def get_verb_valency(verb_lemma: str) -> Dict[str, Any]:
    """Return required object case(s) for a German verb."""
    v = verb_lemma.lower()
    if v in DATIVE_VERBS:
        return {"subject": "nominative", "object": "dative"}
    if v in GENITIVE_VERBS:
        return {"subject": "nominative", "object": "genitive"}
    return {"subject": "nominative", "object": "accusative"}
