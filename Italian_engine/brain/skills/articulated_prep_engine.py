"""
Italian Engine — Articulated Preposition Engine Skill
Fuses prepositions (di, a, da, in, su) with definite articles into articulated prepositions.
"""

import json
import os
from typing import Dict, Any, Optional

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
PREPS_FILE = os.path.join(RULES_DIR, "preposition_articulated_matrix.json")

def load_preposition_matrix() -> Dict[str, Any]:
    if os.path.exists(PREPS_FILE):
        with open(PREPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def select_article(noun: str, gender: str = "m", number: str = "sg") -> str:
    """Determine the standard Italian definite article for a noun."""
    n = noun.lower().strip()
    is_vowel = n[0] in {"a", "e", "i", "o", "u", "y"}
    
    # S impure (s + consonant), z, gn, ps, x
    is_impure = (
        (n.startswith("s") and len(n) > 1 and n[1] not in {"a", "e", "i", "o", "u", "h"})
        or n.startswith(("z", "gn", "ps", "pn", "x"))
    )
    
    if gender.lower() == "m":
        if number.lower() in {"sg", "s"}:
            if is_vowel:
                return "l'"
            elif is_impure:
                return "lo"
            else:
                return "il"
        else: # plural
            if is_vowel or is_impure:
                return "gli"
            else:
                return "i"
    else: # feminine
        if number.lower() in {"sg", "s"}:
            if is_vowel:
                return "l'"
            else:
                return "la"
        else:
            return "le"

def fuse_preposition(preposition: str, article: str) -> str:
    """
    Fuse preposition and article:
    Example: fuse_preposition('di', 'il') -> 'del'
             fuse_preposition('in', 'la') -> 'nella'
             fuse_preposition('su', 'i') -> 'sui'
    """
    p = preposition.lower().strip()
    a = article.lower().strip()
    
    matrix = load_preposition_matrix()
    key = f"{p}_{a}"
    contractions = matrix.get("contractions", {})
    if key in contractions:
        return contractions[key]
        
    return f"{p} {a}"
