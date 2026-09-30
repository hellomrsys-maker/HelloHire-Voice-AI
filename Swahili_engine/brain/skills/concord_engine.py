"""
Swahili Engine — Concordial Agreement Skill
Generates and validates alliterative noun class agreement across adjectives, demonstratives, and possessives.
"""

from typing import Dict, Any, Optional
from .noun_class_engine import identify_noun_class

ADJECTIVE_PREFIXES = {
    1: "m", 2: "wa", 3: "m", 4: "mi", 5: "", 6: "ma",
    7: "ki", 8: "vi", 9: "n", 10: "n", 11: "m", 15: "ku", 16: "pa"
}

DEMONSTRATIVES = {
    1: {"proximal": "huyu", "distal": "yule"},
    2: {"proximal": "hawa", "distal": "wale"},
    3: {"proximal": "huu", "distal": "ule"},
    4: {"proximal": "hii", "distal": "ile"},
    5: {"proximal": "hili", "distal": "lile"},
    6: {"proximal": "haya", "distal": "yale"},
    7: {"proximal": "hiki", "distal": "kile"},
    8: {"proximal": "hivi", "distal": "vile"},
    9: {"proximal": "hii", "distal": "ile"},
    10: {"proximal": "hizi", "distal": "zile"},
    11: {"proximal": "huu", "distal": "ule"},
    15: {"proximal": "huku", "distal": "kule"},
    16: {"proximal": "hapa", "distal": "pale"}
}

POSSESSIVE_CONCORDS = {
    1: "w", 2: "w", 3: "w", 4: "y", 5: "l", 6: "y",
    7: "ch", 8: "vy", 9: "y", 10: "z", 11: "w", 15: "kw", 16: "p"
}

ASSOCIATIVE_A = {
    1: "wa", 2: "wa", 3: "wa", 4: "ya", 5: "la", 6: "ya",
    7: "cha", 8: "vya", 9: "ya", 10: "za", 11: "wa", 15: "kwa", 16: "pa"
}

def get_adjective_form(noun_class: int, adj_stem: str) -> str:
    """Inflect adjective stem according to noun class."""
    stem = adj_stem.lower().strip()
    prefix = ADJECTIVE_PREFIXES.get(noun_class, "")
    
    # Phonetic adjustments
    if stem == "zuri":
        if noun_class in {9, 10}:
            return "nzuri"
        elif noun_class == 5:
            return "zuri"
        return prefix + stem
    elif stem == "kubwa":
        if noun_class in {9, 10}:
            return "kubwa"
        elif noun_class == 5:
            return "kubwa"
        return prefix + stem
    elif stem == "dogo":
        if noun_class in {9, 10}:
            return "ndogo"
        elif noun_class == 5:
            return "dogo"
        return prefix + stem
        
    return prefix + stem

def get_demonstrative(noun_class: int, dem_type: str = "proximal") -> str:
    """Return proximal ('this') or distal ('that') demonstrative for noun class."""
    d_dict = DEMONSTRATIVES.get(noun_class, DEMONSTRATIVES[9])
    return d_dict.get(dem_type, d_dict["proximal"])

def get_possessive(noun_class: int, poss_stem: str = "angu") -> str:
    """Inflect possessive stem (angu, ako, ake, etu, enu, ao) for noun class."""
    concord = POSSESSIVE_CONCORDS.get(noun_class, "y")
    return concord + poss_stem

def get_associative_a(noun_class: int) -> str:
    """Return associative particle '-a' for noun class."""
    return ASSOCIATIVE_A.get(noun_class, "ya")

def generate_concordial_np(
    noun: str,
    poss_stem: Optional[str] = None,
    dem_type: Optional[str] = None,
    adj_stem: Optional[str] = None
) -> str:
    """
    Generate an agreement-verified Swahili noun phrase according to modifier hierarchy:
    [Noun] > [Possessive] > [Demonstrative] > [Adjective]
    Example: noun='kitabu', poss_stem='angu', dem_type='proximal', adj_stem='zuri'
             -> 'kitabu changu hiki kizuri'
    """
    n_class = identify_noun_class(noun)
    parts = [noun]
    
    if poss_stem:
        parts.append(get_possessive(n_class, poss_stem))
    if dem_type:
        parts.append(get_demonstrative(n_class, dem_type))
    if adj_stem:
        parts.append(get_adjective_form(n_class, adj_stem))
        
    return " ".join(parts)

def validate_concord(noun: str, modifier: str, mod_type: str) -> Dict[str, Any]:
    """Validate whether modifier agrees with noun's class."""
    n_class = identify_noun_class(noun)
    
    if mod_type == "demonstrative":
        expected_prox = get_demonstrative(n_class, "proximal")
        expected_dist = get_demonstrative(n_class, "distal")
        valid = modifier.lower() in {expected_prox, expected_dist}
        return {
            "valid": valid,
            "noun": noun,
            "class": n_class,
            "modifier": modifier,
            "expected": f"{expected_prox} / {expected_dist}"
        }
    elif mod_type == "possessive":
        expected_concord = POSSESSIVE_CONCORDS.get(n_class, "w")
        valid = modifier.lower().startswith(expected_concord)
        return {
            "valid": valid,
            "noun": noun,
            "class": n_class,
            "modifier": modifier,
            "expected_prefix": expected_concord
        }
    elif mod_type == "adjective":
        # Check prefix
        expected_pfx = ADJECTIVE_PREFIXES.get(n_class, "")
        valid = modifier.lower().startswith(expected_pfx) or (n_class == 5 and not modifier.lower().startswith(("ki", "vi", "wa")))
        return {
            "valid": valid,
            "noun": noun,
            "class": n_class,
            "modifier": modifier,
            "expected_prefix": expected_pfx
        }
        
    return {"valid": True, "noun": noun, "class": n_class, "modifier": modifier}
