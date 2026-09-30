"""
Tamil Sentence Generation Engine.
Synthesizes canonical head-final SOV clauses with case agglutination,
PNG verb concord, and sandhi plosive doubling.
"""

from typing import Optional
from Tamil_engine.brain.skills.case_engine import inflect_case
from Tamil_engine.brain.skills.sandhi_engine import apply_sandhi

def generate_sov_sentence(
    subject: str,
    verb: str,
    object_noun: Optional[str] = None,
    indirect_object: Optional[str] = None,
    adverb: Optional[str] = None
) -> str:
    """
    Synthesizes a canonical Tamil SOV sentence:
    [Subject] + [Indirect Object (Dative)] + [Direct Object (Accusative)] + [Adverb] + [Verb]
    """
    parts = [subject]
    
    if indirect_object:
        parts.append(inflect_case(indirect_object, 4))  # Dative
        
    if object_noun:
        parts.append(inflect_case(object_noun, 2))      # Accusative
        
    if adverb:
        parts.append(adverb)
        
    parts.append(verb)
    raw_sentence = " ".join(parts) + "."
    
    # Apply sandhi plosive doubling
    return apply_sandhi(raw_sentence)

def generate_dative_experiencer_sentence(
    experiencer: str,
    modal_verb: str,
    theme: Optional[str] = None
) -> str:
    """
    Synthesizes a dative subject construction (e.g. எனக்கு தமிழ் தெரியும்).
    """
    exp_dat = inflect_case(experiencer, 4)
    if theme:
        raw = f"{exp_dat} {theme} {modal_verb}."
    else:
        raw = f"{exp_dat} {modal_verb}."
    return apply_sandhi(raw)
