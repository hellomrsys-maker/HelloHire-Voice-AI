"""
Swahili Engine — Monosyllabic Verb Skill
Regulates the dummy 'ku-' retention and dropping rules for monosyllabic stems (-la, -nywa, -ja, -fa, -pa).
"""

from typing import Dict, Any

MONOSYLLABIC_STEMS = {
    "la": "kula",
    "nywa": "kunywa",
    "ja": "kuja",
    "fa": "kufa",
    "pa": "kupa",
    "cha": "kucha",
    "enda": "kwenda",
    "isha": "kwisha"
}

def is_monosyllabic_verb(stem_or_inf: str) -> bool:
    """Check if stem or infinitive is in the monosyllabic verb set."""
    clean = stem_or_inf.lower().strip()
    if clean.startswith("ku") and len(clean) > 2 and clean[2:] in MONOSYLLABIC_STEMS:
        return True
    if clean.startswith("kw") and len(clean) > 2 and clean[2:] in MONOSYLLABIC_STEMS:
        return True
    return clean in MONOSYLLABIC_STEMS

def should_retain_ku(tense: str, has_object_prefix: bool, is_negative: bool) -> bool:
    """
    Determine if monosyllabic dummy 'ku-' should be retained.
    Retained only in affirmative tenses (na, li, ta, me) when NO object prefix is present.
    """
    if is_negative:
        # In negative present (hali), ku- is dropped
        if tense == "present":
            return False
        # In past negative (hakula) and future negative (hatakula), ku- is dropped/managed by negative TAM
        return False
        
    if has_object_prefix:
        return False
        
    if tense in {"present", "past", "future", "perfect", "conditional"}:
        return True
        
    return False

def check_monosyllabic_ku(verb: str) -> Dict[str, Any]:
    """
    Analyze whether an inflected verb contains a monosyllabic root and whether dummy ku- is retained or dropped.
    """
    v = verb.lower().strip()
    
    # Check negative present forms (e.g. hali, hanywi, haji, hafi, si-li -> sili)
    neg_present_roots = {"li": "la", "nywi": "nywa", "ji": "ja", "fi": "fa"}
    for np_form, root in neg_present_roots.items():
        if v.endswith(np_form) and (v.startswith("si") or v.startswith("ha")):
            return {
                "verb": v,
                "is_monosyllabic": True,
                "root": root,
                "retains_ku": False,
                "is_negative_present": True,
                "has_object_prefix": False
            }
            
    # Check affirmative monosyllabic forms with dummy ku-
    for root in MONOSYLLABIC_STEMS.keys():
        if "ku" + root in v:
            return {
                "verb": v,
                "is_monosyllabic": True,
                "root": root,
                "retains_ku": True,
                "is_negative_present": False,
                "has_object_prefix": False
            }
        elif root in v:
            # Check if preceded by an object prefix (e.g. alikila)
            has_op = any(f"{op}{root}" in v for op in ["m", "wa", "u", "i", "li", "ya", "ki", "vi", "zi", "ch", "vy"])
            if has_op:
                return {
                    "verb": v,
                    "is_monosyllabic": True,
                    "root": root,
                    "retains_ku": False,
                    "is_negative_present": False,
                    "has_object_prefix": True
                }
                
    return {
        "verb": v,
        "is_monosyllabic": False,
        "root": None,
        "retains_ku": False,
        "is_negative_present": False,
        "has_object_prefix": False
    }

