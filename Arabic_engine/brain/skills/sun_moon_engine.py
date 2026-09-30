"""
Arabic Engine — Sun & Moon Letters Engine Skill
Determines coronal assimilation of the definite article 'al-' (الحروف الشمسية والقمرية).
"""

from typing import Dict, Any

SUN_LETTERS_ARABIC = set("تثدذرunknownزسشصضطظلن")
# Standard 14 sun consonants in Arabic
SUN_LETTERS_CHARS = {'ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن'}

# Romanized sun letter starters
SUN_LETTERS_LATIN = [
    "sh", "th", "dh", "t", "d", "r", "z", "s", "l", "n"
]

def is_sun_letter(word: str) -> bool:
    """Check if the first letter of a word is a Sun letter."""
    w = word.strip()
    if not w:
        return False
        
    first_char = w[0]
    if first_char in SUN_LETTERS_CHARS:
        return True
        
    w_lower = w.lower()
    for sl in ["sh", "th", "dh"]:
        if w_lower.startswith(sl):
            return True
    return w_lower[0] in {'t', 'd', 'r', 'z', 's', 'l', 'n'}

def apply_sun_moon_article(noun: str) -> str:
    """
    Apply the appropriate assimilated (Sun) or unassimilated (Moon) definite article.
    Example: 'shams' -> 'ash-shams', 'qamar' -> 'al-qamar', 'rajul' -> 'ar-rajul'
    """
    clean = noun.lower().strip()
    if clean.startswith("al-") or clean.startswith("al"):
        clean = clean[3:] if clean.startswith("al-") else clean[2:]
        
    if is_sun_letter(clean):
        # Coronal assimilation
        if clean.startswith("sh"):
            return f"ash-{clean}"
        elif clean.startswith("th"):
            return f"ath-{clean}"
        elif clean.startswith("dh"):
            return f"adh-{clean}"
        else:
            coronal = clean[0]
            return f"a{coronal}-{clean}"
    else:
        return f"al-{clean}"

def check_phonological_assimilation(word: str) -> Dict[str, Any]:
    """Audit whether a romanized definite word properly assimilated its sun letter."""
    w = word.lower().strip()
    if not (w.startswith("al-") or w.startswith("al")):
        # Check if it has assimilated prefix e.g. ash-, ar-, an-, as-
        for pfx in ["ash-", "ath-", "adh-", "ar-", "az-", "as-", "at-", "ad-", "an-", "al-"]:
            if w.startswith(pfx):
                rem = w[len(pfx):]
                sun = is_sun_letter(rem)
                return {"is_definite": True, "is_assimilated": pfx != "al-", "is_sun_letter": sun, "valid": True}
        return {"is_definite": False, "is_assimilated": False, "is_sun_letter": False, "valid": True}
        
    stem = w[3:] if w.startswith("al-") else w[2:]
    sun = is_sun_letter(stem)
    # If it is a sun letter but prefixed with unassimilated 'al-', it's phonologically unassimilated
    return {
        "is_definite": True,
        "is_assimilated": not sun,
        "is_sun_letter": sun,
        "valid": True, # Orthographically in Arabic script it is written with Alif-Lam anyway
        "phonetic_transcription": apply_sun_moon_article(stem)
    }
