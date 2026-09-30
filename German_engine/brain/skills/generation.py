"""
German Engine — Surface Realization & Generation Skill
Generates well-formed German noun phrases, clauses, and epistolary communications.
"""

from typing import Dict, Any, List, Optional
from .adjective_declension_engine import inflect_adjective
from .verb_conjugator import conjugate_present, form_participle_ii

def generate_noun_phrase(determiner: Optional[str], adjective: Optional[str], noun: str, gender: str, case: str) -> str:
    """
    Generate an inflected German noun phrase.
    Example: det='der', adj='gut', noun='Mann', gender='masculine', case='accusative' -> 'den guten Mann'
    """
    parts = []
    
    # Map determiner to inflected form
    det_map = {
        ("der", "masculine", "nominative"): "der",
        ("der", "masculine", "accusative"): "den",
        ("der", "masculine", "dative"): "dem",
        ("der", "masculine", "genitive"): "des",
        ("der", "feminine", "nominative"): "die",
        ("der", "feminine", "accusative"): "die",
        ("der", "feminine", "dative"): "der",
        ("der", "feminine", "genitive"): "der",
        ("der", "neuter", "nominative"): "das",
        ("der", "neuter", "accusative"): "das",
        ("der", "neuter", "dative"): "dem",
        ("der", "neuter", "genitive"): "des",
        ("der", "plural", "nominative"): "die",
        ("der", "plural", "accusative"): "die",
        ("der", "plural", "dative"): "den",
        ("der", "plural", "genitive"): "der",
        
        ("ein", "masculine", "nominative"): "ein",
        ("ein", "masculine", "accusative"): "einen",
        ("ein", "masculine", "dative"): "einem",
        ("ein", "masculine", "genitive"): "eines",
        ("ein", "feminine", "nominative"): "eine",
        ("ein", "feminine", "accusative"): "eine",
        ("ein", "feminine", "dative"): "einer",
        ("ein", "feminine", "genitive"): "einer",
        ("ein", "neuter", "nominative"): "ein",
        ("ein", "neuter", "accusative"): "ein",
        ("ein", "neuter", "dative"): "einem",
        ("ein", "neuter", "genitive"): "eines"
    }
    
    surface_det = None
    if determiner:
        key = (determiner.lower(), gender.lower(), case.lower())
        surface_det = det_map.get(key, determiner)
        parts.append(surface_det)
        
    if adjective:
        inflected_adj = inflect_adjective(adjective, gender, case, surface_det)
        parts.append(inflected_adj)
        
    # Noun (properly capitalized)
    capitalized_noun = noun[0].upper() + noun[1:] if noun else ""
    
    # Add Genitive -s/-es for masc/neut singular if applicable
    if case.lower() == "genitive" and gender.lower() in {"masculine", "neuter"} and not capitalized_noun.endswith(("s", "es")):
        capitalized_noun += "s"
    elif case.lower() == "dative" and gender.lower() == "plural" and not capitalized_noun.endswith(("n", "s")):
        capitalized_noun += "n"
        
    parts.append(capitalized_noun)
    return " ".join(parts)

def generate_formal_email(recipient_title: str, recipient_name: str, body_text: str, sender_name: str) -> str:
    """Generate a formal business email complying with DIN 5008 standards."""
    salutation = f"Sehr geehrte Frau {recipient_name}," if recipient_title.lower() == "frau" else f"Sehr geehrter Herr {recipient_name},"
    # German epistolary rule: first line after comma is lowercase unless it's a noun
    lines = [
        salutation,
        "",
        body_text,
        "",
        "Mit freundlichen Grüßen",
        sender_name
    ]
    return "\n".join(lines)

def generate_informal_message(friend_name: str, message: str, sender_name: str) -> str:
    """Generate an informal message with Duzen address."""
    lines = [
        f"Hallo {friend_name},",
        "",
        message,
        "",
        "Liebe Grüße",
        sender_name
    ]
    return "\n".join(lines)
