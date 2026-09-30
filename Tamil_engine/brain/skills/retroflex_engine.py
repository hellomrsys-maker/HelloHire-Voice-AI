"""
Tamil Retroflex and Coronal Phonology Engine.
Audits the distinct Dravidian tri-way coronal contrast (Dental vs Alveolar vs Retroflex)
and specifically monitors the voiced retroflex approximant ழ் / ழ (ḻ).
"""

from typing import Dict, List, Set

RETROFLEX_CHARS = {"ட்", "ட", "டா", "டி", "டீ", "டு", "டூ", "டெ", "டே", "டை", "டொ", "டோ", "டௌ",
                   "ண்", "ண", "ணா", "ணி", "ணீ", "ணு", "ணூ", "ணெ", "ணே", "ணை", "ணொ", "ணோ", "ணௌ",
                   "ள்", "ள", "ளா", "ளி", "ளீ", "ளு", "ளூ", "ளெ", "ளே", "ளை", "ளொ", "ளோ", "ளௌ",
                   "ழ்", "ழ", "ழா", "ழி", "ழீ", "ழு", "ழூ", "ழெ", "ழே", "ழை", "ழொ", "ழோ", "ழௌ"}

ZHA_APPROXIMANT_CHARS = {"ழ்", "ழ", "ழா", "ழி", "ழீ", "ழு", "ழூ", "ழெ", "ழே", "ழை", "ழொ", "ழோ", "ழௌ"}

ALVEOLAR_CHARS = {"ற்", "ற", "றா", "றி", "றீ", "று", "றூ", "றெ", "றே", "றை", "றொ", "றோ", "றௌ",
                  "ன்", "ன", "னா", "னி", "னீ", "னு", "னூ", "னெ", "னே", "னை", "னொ", "னோ", "னௌ",
                  "ல்", "ல", "லா", "லி", "லீ", "லு", "லூ", "லெ", "லே", "லை", "லொ", "லோ", "லௌ"}

DENTAL_CHARS = {"த்", "த", "தா", "தி", "தீ", "து", "தூ", "தெ", "தே", "தை", "தொ", "தோ", "தௌ",
                "ந்", "ந", "நா", "நி", "நீ", "நு", "நூ", "நெ", "நே", "நை", "நொ", "நோ", "நௌ"}

def analyze_phonological_profile(text: str) -> Dict[str, any]:
    """
    Analyzes Tamil text for coronal and retroflex phonetic markers,
    particularly isolating the unique retroflex approximant 'ழ' (ḻ).
    """
    has_retroflex = any(any(c in word for c in RETROFLEX_CHARS) for word in text.split())
    has_zha = any(any(c in word for c in ZHA_APPROXIMANT_CHARS) for word in text.split())
    has_alveolar = any(any(c in word for c in ALVEOLAR_CHARS) for word in text.split())
    has_dental = any(any(c in word for c in DENTAL_CHARS) for word in text.split())
    
    retroflex_count = sum(1 for char in text if any(char == rc for rc in RETROFLEX_CHARS))
    zha_count = sum(1 for char in text if any(char == zc for zc in ZHA_APPROXIMANT_CHARS))
    
    # Bitfield encoding:
    # Bit 0: Text valid
    # Bit 1: Contains retroflex consonants
    # Bit 2: Contains retroflex approximant 'ழ' (ḻ)
    byte_20_val = 0
    if len(text.strip()) > 0:
        byte_20_val |= 0x01
    if has_retroflex:
        byte_20_val |= 0x02
    if has_zha:
        byte_20_val |= 0x04
        
    return {
        "text": text,
        "has_retroflex": has_retroflex,
        "has_zha_approximant": has_zha,
        "has_alveolar": has_alveolar,
        "has_dental": has_dental,
        "retroflex_count": retroflex_count,
        "zha_count": zha_count,
        "byte_20_val": byte_20_val
    }
