"""
Cantonese Sentence-Final Particle (SFP) Engine.
Analyzes single and clustered sentence-final particles (SFPs),
stripping punctuation robustly to prevent false negatives.
"""

from typing import Dict, List, Optional
import re

SFP_DATABASE = {
    "喇": {
        "jyutping": "laa3",
        "tone": 3,
        "function": "change_of_state",
        "meaning": "currently relevant state / change of state",
        "register": "colloquial"
    },
    "啦": {
        "jyutping": "laa1",
        "tone": 1,
        "function": "suggestion_imperative",
        "meaning": "friendly suggestion or imperative",
        "register": "colloquial"
    },
    "呀": {
        "jyutping": "aa3",
        "tone": 3,
        "function": "assertion_softener",
        "meaning": "softening tone in assertion or inquiry",
        "register": "colloquial"
    },
    "㗎": {
        "jyutping": "gaa3",
        "tone": 3,
        "function": "epistemic_assertion",
        "meaning": "fused (ge3+aa3) asserting certainty or habitual fact",
        "register": "colloquial"
    },
    "啫": {
        "jyutping": "ze1",
        "tone": 1,
        "function": "restrictive_downplaying",
        "meaning": "only / merely / downplaying significance",
        "register": "colloquial"
    },
    "喎": {
        "jyutping": "wo3",
        "tone": 3,
        "function": "hearsay_evidential",
        "meaning": "reportative evidential ('they say')",
        "register": "colloquial"
    },
    "囉": {
        "jyutping": "lo1",
        "tone": 1,
        "function": "obviousness_consequence",
        "meaning": "stating obvious outcome or natural consequence",
        "register": "colloquial"
    },
    "添": {
        "jyutping": "tim1",
        "tone": 1,
        "function": "additive_exclamatory",
        "meaning": "additional surprise / even more so",
        "register": "colloquial"
    },
    "咩": {
        "jyutping": "me1",
        "tone": 1,
        "function": "skeptical_interrogative",
        "meaning": "rhetorical doubt / surprised question",
        "register": "colloquial"
    },
    "咋": {
        "jyutping": "zaa3",
        "tone": 3,
        "function": "exclusive_limitative",
        "meaning": "fused (ze1+aa3) expressing strict limitation ('only')",
        "register": "colloquial"
    }
}

PUNCTUATION_PATTERN = re.compile(r"[，。！？,.!?～~…\s]+$")

def extract_sfps(sentence: str) -> List[Dict[str, any]]:
    """
    Extracts sentence-final particles from the coda of a sentence,
    stripping punctuation robustly.
    """
    cleaned = PUNCTUATION_PATTERN.sub("", sentence)
    if not cleaned:
        return []
        
    found_sfps = []
    
    # Check backwards for up to 3 final particles (clusters)
    tail_chars = list(cleaned[-3:])
    for char in reversed(tail_chars):
        if char in SFP_DATABASE:
            info = SFP_DATABASE[char]
            found_sfps.insert(0, {
                "particle": char,
                "jyutping": info["jyutping"],
                "tone": info["tone"],
                "function": info["function"],
                "meaning": info["meaning"]
            })
        else:
            # Stop when a non-SFP character is reached from right to left
            break
            
    # Also check if any SFP occurs anywhere near the end (last 4 characters)
    if not found_sfps:
        for char in cleaned[-4:]:
            if char in SFP_DATABASE and not any(f["particle"] == char for f in found_sfps):
                info = SFP_DATABASE[char]
                found_sfps.append({
                    "particle": char,
                    "jyutping": info["jyutping"],
                    "tone": info["tone"],
                    "function": info["function"],
                    "meaning": info["meaning"]
                })
                
    return found_sfps

def has_sfp(sentence: str, particle: Optional[str] = None) -> bool:
    """
    Returns True if the sentence ends with an SFP (or matches a specific particle).
    """
    sfps = extract_sfps(sentence)
    if particle:
        return any(s["particle"] == particle for s in sfps)
    return len(sfps) > 0
