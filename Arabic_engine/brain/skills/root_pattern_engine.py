"""
Arabic Engine — Root & Pattern Engine Skill
Operates on triconsonantal roots (C1-C2-C3) and derives Forms I through X verbal templates
and nominal participles.
"""

from typing import Dict, Any, Optional, Tuple

KNOWN_ROOTS = {
    "ktb": ("k", "t", "b"),
    "drs": ("d", "r", "s"),
    "slm": ("s", "l", "m"),
    "'lm": ("'", "l", "m"),
    "ksr": ("k", "s", "r"),
    "jm'": ("j", "m", "'"),
    "xrj": ("x", "r", "j"),
    "qbl": ("q", "b", "l"),
    "hrk": ("h", "r", "k")
}

def derive_form(root: str, form_number: str = "I") -> Dict[str, str]:
    """
    Derive past, present, masdar, and participles for a given triconsonantal root.
    root: 3-character root string (e.g. 'ktb', 'drs', 'slm')
    form_number: 'I' .. 'X'
    """
    clean = root.lower().strip()
    if clean in KNOWN_ROOTS:
        c1, c2, c3 = KNOWN_ROOTS[clean]
    elif len(clean) == 3:
        c1, c2, c3 = clean[0], clean[1], clean[2]
    else:
        c1, c2, c3 = "f", "'", "l"
        
    fn = form_number.upper()
    if fn == "I":
        return {
            "past": f"{c1}a{c2}a{c3}a",
            "present": f"ya{c1}{c2}u{c3}u",
            "masdar": f"{c1}i{c2}ā{c3}a",
            "active_participle": f"{c1}ā{c2}i{c3}",
            "passive_participle": f"ma{c1}{c2}ū{c3}"
        }
    elif fn == "II":
        return {
            "past": f"{c1}a{c2}{c2}a{c3}a",
            "present": f"yu{c1}a{c2}{c2}i{c3}u",
            "masdar": f"ta{c1}{c2}ī{c3}",
            "active_participle": f"mu{c1}a{c2}{c2}i{c3}",
            "passive_participle": f"mu{c1}a{c2}{c2}a{c3}"
        }
    elif fn == "III":
        return {
            "past": f"{c1}ā{c2}a{c3}a",
            "present": f"yu{c1}ā{c2}i{c3}u",
            "masdar": f"mu{c1}ā{c2}a{c3}a",
            "active_participle": f"mu{c1}ā{c2}i{c3}",
            "passive_participle": f"mu{c1}ā{c2}a{c3}"
        }
    elif fn == "IV":
        return {
            "past": f"a{c1}{c2}a{c3}a",
            "present": f"yu{c1}{c2}i{c3}u",
            "masdar": f"i{c1}{c2}ā{c3}",
            "active_participle": f"mu{c1}{c2}i{c3}",
            "passive_participle": f"mu{c1}{c2}a{c3}"
        }
    elif fn == "V":
        return {
            "past": f"ta{c1}a{c2}{c2}a{c3}a",
            "present": f"yata{c1}a{c2}{c2}a{c3}u",
            "masdar": f"ta{c1}a{c2}{c2}u{c3}",
            "active_participle": f"muta{c1}a{c2}{c2}i{c3}",
            "passive_participle": f"muta{c1}a{c2}{c2}a{c3}"
        }
    elif fn == "VI":
        return {
            "past": f"ta{c1}ā{c2}a{c3}a",
            "present": f"yata{c1}ā{c2}a{c3}u",
            "masdar": f"ta{c1}ā{c2}u{c3}",
            "active_participle": f"muta{c1}ā{c2}i{c3}",
            "passive_participle": f"muta{c1}ā{c2}a{c3}"
        }
    elif fn == "VII":
        return {
            "past": f"in{c1}a{c2}a{c3}a",
            "present": f"yan{c1}a{c2}i{c3}u",
            "masdar": f"in{c1}i{c2}ā{c3}",
            "active_participle": f"mun{c1}a{c2}i{c3}",
            "passive_participle": f"mun{c1}a{c2}a{c3}"
        }
    elif fn == "VIII":
        return {
            "past": f"i{c1}ta{c2}a{c3}a",
            "present": f"ya{c1}ta{c2}i{c3}u",
            "masdar": f"i{c1}ti{c2}ā{c3}",
            "active_participle": f"mu{c1}ta{c2}i{c3}",
            "passive_participle": f"mu{c1}ta{c2}a{c3}"
        }
    elif fn == "X":
        return {
            "past": f"ista{c1}{c2}a{c3}a",
            "present": f"yasta{c1}{c2}i{c3}u",
            "masdar": f"isti{c1}{c2}ā{c3}",
            "active_participle": f"musta{c1}{c2}i{c3}",
            "passive_participle": f"musta{c1}{c2}a{c3}"
        }
        
    return {
        "past": f"{c1}a{c2}a{c3}a",
        "present": f"ya{c1}{c2}u{c3}u",
        "masdar": f"{c1}i{c2}ā{c3}a",
        "active_participle": f"{c1}ā{c2}i{c3}",
        "passive_participle": f"ma{c1}{c2}ū{c3}"
    }

def extract_root_heuristic(word: str) -> Optional[str]:
    """
    Extract probable 3-consonant root by stripping known Arabic prefixes and affixes.
    """
    w = word.lower().strip()
    # Strip definite article
    if w.startswith("al-") or w.startswith("al"):
        w = w[3:] if w.startswith("al-") else w[2:]
        
    # Strip prefix 'wa-' (and)
    if w.startswith("wa") and len(w) > 4:
        w = w[2:]
        
    # Match against known roots
    for root_key in KNOWN_ROOTS:
        c1, c2, c3 = KNOWN_ROOTS[root_key]
        if c1 in w and c2 in w and c3 in w:
            idx1 = w.find(c1)
            idx2 = w.find(c2, idx1 + 1)
            idx3 = w.find(c3, idx2 + 1)
            if idx1 != -1 and idx2 != -1 and idx3 != -1:
                return root_key
                
    return None
