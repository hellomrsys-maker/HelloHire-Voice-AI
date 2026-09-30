"""
Indonesian Engine — Sentence Generation Skill
Synthesizes Indonesian sentences in canonical SVO order with accurate voice affixation,
aspect particles, and classifier phrases.
"""

from typing import Optional, List
from .voice_affix_engine import derive_verb
from .classifier_engine import format_numeral_classifier

def generate_sentence(
    subject: str,
    verb_root: str,
    direct_object: Optional[str] = None,
    voice: str = "active",
    aspect: Optional[str] = None,
    negator: Optional[str] = None,
    object_number: Optional[str] = None
) -> str:
    """
    Synthesize an Indonesian clause.
    Example: generate_sentence("Budi", "baca", "buku", voice="active", aspect="sudah")
             -> "Budi sudah membaca buku."
             generate_sentence("Buku itu", "baca", direct_object="Budi", voice="passive")
             -> "Buku itu dibaca oleh Budi."
    """
    parts = []
    
    # 1. Subject
    if subject:
        parts.append(subject)
        
    # 2. Aspect / Aux
    if aspect:
        parts.append(aspect)
        
    # 3. Negation
    if negator:
        parts.append(negator)
        
    # 4. Verb derivation
    derived_v = derive_verb(verb_root, voice=voice)
    parts.append(derived_v)
    
    # 5. Object / Agent
    if direct_object:
        if voice == "passive":
            parts.append(f"oleh {direct_object}")
        else:
            if object_number:
                obj_phrase = format_numeral_classifier(object_number, direct_object)
                parts.append(obj_phrase)
            else:
                parts.append(direct_object)
                
    clause = " ".join(parts).strip()
    if clause and not clause.endswith((".", "!", "?")):
        clause += "."
    return clause[0].upper() + clause[1:] if clause else ""
