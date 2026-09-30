"""
Arabic Engine — Broken Plural & Number Engine Skill
Resolves Arabic sound and broken plurals and categorizes human vs non-human animacy
for deflected agreement rules.
"""

from typing import Dict, Any, Optional

PLURAL_DATABASE = {
    # Non-human broken plurals (Trigger Feminine Singular Agreement)
    "kitab": {"plural": "kutub", "pattern": "fu'ul", "is_human": False, "gender": "m"},
    "madina": {"plural": "mudun", "pattern": "fu'ul", "is_human": False, "gender": "f"},

    "qalb": {"plural": "qulub", "pattern": "fu'ul", "is_human": False, "gender": "m"},
    "dars": {"plural": "durus", "pattern": "fu'ul", "is_human": False, "gender": "m"},
    "bayt": {"plural": "buyut", "pattern": "fu'ul", "is_human": False, "gender": "m"},
    "qalam": {"plural": "aqlam", "pattern": "af'al", "is_human": False, "gender": "m"},
    "maktab": {"plural": "makatib", "pattern": "mafa'il", "is_human": False, "gender": "m"},
    "masjid": {"plural": "masajid", "pattern": "mafa'il", "is_human": False, "gender": "m"},
    "miftah": {"plural": "mafatih", "pattern": "mafa'il", "is_human": False, "gender": "m"},
    "sayyara": {"plural": "sayyarat", "pattern": "sound_fem", "is_human": False, "gender": "f"},
    "risala": {"plural": "rasa'il", "pattern": "fa'a'il", "is_human": False, "gender": "f"},

    # Human broken & sound plurals (Trigger Plural Agreement)
    "walad": {"plural": "awlad", "pattern": "af'al", "is_human": True, "gender": "m"},
    "rajul": {"plural": "rijal", "pattern": "fi'al", "is_human": True, "gender": "m"},
    "talib": {"plural": "tullab", "pattern": "fu''al", "is_human": True, "gender": "m"},
    "mu'allim": {"plural": "mu'allimun", "pattern": "sound_masc", "is_human": True, "gender": "m"},
    "mu'allima": {"plural": "mu'allimat", "pattern": "sound_fem", "is_human": True, "gender": "f"},
    "tabib": {"plural": "atibba", "pattern": "af'ila", "is_human": True, "gender": "m"}
}

# Reverse mapping for plural lookup
PLURAL_TO_SINGULAR = {}
for sg, info in PLURAL_DATABASE.items():
    PLURAL_TO_SINGULAR[info["plural"]] = {
        "singular": sg,
        "is_human": info["is_human"],
        "pattern": info["pattern"],
        "gender": info["gender"]
    }

def strip_al_prefix(s: str) -> str:
    clean = s.lower().strip()
    for pfx in ["al-", "ar-", "ash-", "an-", "as-", "ad-", "at-", "ath-", "adh-", "az-"]:
        if clean.startswith(pfx):
            return clean[len(pfx):]
    if clean.startswith("al") and len(clean) > 4 and clean not in {"allah"}:
        return clean[2:]
    return clean

def get_plural(singular: str) -> Optional[Dict[str, Any]]:
    """Return plural form and metadata for a singular noun."""
    s_clean = strip_al_prefix(singular)
    if s_clean in PLURAL_DATABASE:
        res = PLURAL_DATABASE[s_clean].copy()
        res["singular"] = s_clean
        return res
    return None

def analyze_plural(word: str) -> Dict[str, Any]:
    """
    Determine whether a word is plural, identify its singular, and check if it is non-human (deflected).
    """
    w_clean = strip_al_prefix(word)

    if w_clean in PLURAL_TO_SINGULAR:
        info = PLURAL_TO_SINGULAR[w_clean]
        return {
            "word": word,
            "is_plural": True,
            "singular": info["singular"],
            "is_human": info["is_human"],
            "requires_deflected_agreement": not info["is_human"], # Non-human plurals require fem sg
            "pattern": info["pattern"]
        }
        
    # Check sound feminine plural suffix -at
    if w_clean.endswith("at") and len(w_clean) > 3:
        return {
            "word": word,
            "is_plural": True,
            "singular": w_clean[:-2] + "a",
            "is_human": False,
            "requires_deflected_agreement": True,
            "pattern": "sound_fem"
        }
        
    # Check sound masculine plural suffix -un / -in
    if (w_clean.endswith("un") or w_clean.endswith("in")) and len(w_clean) > 4:
        return {
            "word": word,
            "is_plural": True,
            "singular": w_clean[:-2],
            "is_human": True,
            "requires_deflected_agreement": False,
            "pattern": "sound_masc"
        }
        
    return {
        "word": word,
        "is_plural": False,
        "singular": w_clean,
        "is_human": True,
        "requires_deflected_agreement": False,
        "pattern": None
    }
