"""
Swahili Engine — Verbal Extensions Skill
Derives and analyzes productive verbal extensions (Mnyambuliko wa Vitenzi):
Applicative (-ia/-ea), Causative (-isha/-esha), Passive (-wa), Reciprocal (-ana), Stative (-ika/-eka),
governed by vowel harmony height assimilation.
"""

from typing import Dict, Any, Optional

def get_root_vowel(verb_infinitive: str) -> str:
    """Extract primary stem vowel governing height vowel harmony."""
    stem = verb_infinitive.lower().strip()
    if stem.startswith("ku") and len(stem) > 2:
        stem = stem[2:]
    if stem.endswith("a"):
        stem = stem[:-1]
        
    for ch in reversed(stem):
        if ch in {'a', 'e', 'i', 'o', 'u'}:
            return ch
    return 'a'

def derive_extension(verb_infinitive: str, extension_type: str) -> str:
    """
    Derive extended verb form adhering to vowel harmony rules.
    extension_type: 'applicative' | 'causative' | 'passive' | 'reciprocal' | 'stative'
    """
    stem = verb_infinitive.lower().strip()
    if stem.startswith("ku") and len(stem) > 2:
        stem = stem[2:]
        
    base = stem[:-1] if stem.endswith("a") else stem
    vowel = get_root_vowel(verb_infinitive)
    is_mid_vowel = vowel in {'e', 'o'}
    
    if extension_type == "applicative":
        ext = "ea" if is_mid_vowel else "ia"
        return "ku" + base + ext
    elif extension_type == "causative":
        ext = "esha" if is_mid_vowel else "isha"
        return "ku" + base + ext
    elif extension_type == "passive":
        return "ku" + base + "wa"
    elif extension_type == "reciprocal":
        return "ku" + base + "ana"
    elif extension_type == "stative":
        ext = "eka" if is_mid_vowel else "ika"
        return "ku" + base + ext
        
    return verb_infinitive
