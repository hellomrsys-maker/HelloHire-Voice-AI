"""
Thai 5-Tone Calculation Engine.
Calculates phonemic pitch contour based on initial consonant class,
tone diacritics, vowel length, and live/dead syllable coda.
"""

from typing import Dict, Optional, Tuple

MIDDLE_CONSONANTS = set("กจดตฎฏบปอ")
HIGH_CONSONANTS = set("ขฃฉฐถผฝศษสห")
LOW_CONSONANTS = set("คฅฆชซฌฑฒทธพฟภฮงญณนมยรลวฬ")

STOP_CODAS = set("กขคฆดตถทธจชซฎฏบปพฟภ")
SONORANT_CODAS = set("งนมญณยรลวฬ")

def get_consonant_class(char: str) -> str:
    """Returns 'middle', 'high', or 'low' for a Thai initial consonant."""
    if char in MIDDLE_CONSONANTS:
        return "middle"
    elif char in HIGH_CONSONANTS:
        return "high"
    elif char in LOW_CONSONANTS:
        return "low"
    return "middle"

def calculate_syllable_tone(syllable: str) -> Dict[str, any]:
    """
    Computes the 5-tone value for a Thai syllable.
    Returns tone name, number (1-5), contour, and reasoning.
    """
    if not syllable or not any('\u0e01' <= c <= '\u0e2e' for c in syllable):
        return {
            "syllable": syllable,
            "tone_name": "unknown",
            "tone_number": 0,
            "contour": "00"
        }
        
    # 1. Find initial consonant
    initial = None
    for c in syllable:
        if '\u0e01' <= c <= '\u0e2e':
            initial = c
            break
            
    c_class = get_consonant_class(initial)
    
    # 2. Check tone marks
    has_mai_ek = '่' in syllable  # U+0E48
    has_mai_tho = '้' in syllable  # U+0E49
    has_mai_tri = '๊' in syllable  # U+0E4A
    has_mai_chattawa = '๋' in syllable  # U+0E4B
    
    if has_mai_ek:
        if c_class in ["middle", "high"]:
            tone = ("low", 2, "21")
        else:  # low class
            tone = ("falling", 3, "51")
        return {"syllable": syllable, "tone_name": tone[0], "tone_number": tone[1], "contour": tone[2], "rule": f"{c_class} + mai_ek"}
        
    if has_mai_tho:
        if c_class in ["middle", "high"]:
            tone = ("falling", 3, "51")
        else:  # low class
            tone = ("high", 4, "45")
        return {"syllable": syllable, "tone_name": tone[0], "tone_number": tone[1], "contour": tone[2], "rule": f"{c_class} + mai_tho"}
        
    if has_mai_tri:
        return {"syllable": syllable, "tone_name": "high", "tone_number": 4, "contour": "45", "rule": "mai_tri"}
        
    if has_mai_chattawa:
        return {"syllable": syllable, "tone_name": "rising", "tone_number": 5, "contour": "24", "rule": "mai_chattawa"}
        
    # 3. Unmarked syllable: live vs dead
    # Check coda
    last_char = syllable[-1]
    is_dead = last_char in STOP_CODAS or 'ะ' in syllable
    
    if c_class == "middle":
        if is_dead:
            tone = ("low", 2, "21")
        else:
            tone = ("mid", 1, "33")
    elif c_class == "high":
        if is_dead:
            tone = ("low", 2, "21")
        else:
            tone = ("rising", 5, "24")
    else:  # low class
        if is_dead:
            tone = ("high", 4, "45")
        else:
            tone = ("mid", 1, "33")
            
    return {
        "syllable": syllable,
        "tone_name": tone[0],
        "tone_number": tone[1],
        "contour": tone[2],
        "rule": f"{c_class} + {'dead' if is_dead else 'live'}"
    }
