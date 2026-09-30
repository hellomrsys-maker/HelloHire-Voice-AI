"""
Swahili Engine — Verbal Template Skill
Synthesizes and parses Swahili finite verbal prefix/suffix chains across 8 morphological slots:
[Neg] + [SP] + [TAM] + [Rel] + [OP] + [Root] + [Ext] + [FV].
"""

from typing import Dict, Any, Optional

SUBJECT_PREFIXES = {
    "1sg": "ni", "2sg": "u", "3sg": "a",
    "1pl": "tu", "2pl": "m", "3pl": "wa",
    "cl1": "a", "cl2": "wa", "cl3": "u", "cl4": "i",
    "cl5": "li", "cl6": "ya", "cl7": "ki", "cl8": "vi",
    "cl9": "i", "cl10": "zi", "cl11": "u", "cl15": "ku", "cl16": "pa"
}

NEGATIVE_SUBJECT_PREFIXES = {
    "1sg": "si", "2sg": "hu", "3sg": "ha",
    "1pl": "hatu", "2pl": "ham", "3pl": "hawa",
    "cl1": "ha", "cl2": "hawa", "cl3": "hau", "cl4": "hai",
    "cl5": "hali", "cl6": "haya", "cl7": "haki", "cl8": "havi",
    "cl9": "hai", "cl10": "hazi", "cl11": "hau", "cl15": "haku", "cl16": "hapa"
}

TAM_AFFIRMATIVE = {
    "present": "na",
    "past": "li",
    "future": "ta",
    "perfect": "me",
    "conditional": "ki",
    "hypothetical": "nge",
    "narrative": "ka"
}

MONOSYLLABIC_ROOTS = {"la", "nywa", "ja", "fa", "pa", "cha", "enda", "isha"}

def synthesize_verb(
    subject: str,
    root: str,
    tense: str = "present",
    object_marker: Optional[str] = None,
    negative: bool = False
) -> str:
    """
    Synthesize a full agglutinative Swahili verb form.
    Handles tense prefixes, subject prefixes, object prefixes, monosyllabic ku- retention,
    and negation shifts.
    """
    clean_root = root.lower().strip()
    if clean_root.startswith("ku") and len(clean_root) > 2:
        # Strip infinitive ku- if passed
        clean_root = clean_root[2:]
        
    is_monosyllabic = clean_root in MONOSYLLABIC_ROOTS
    
    if negative:
        neg_sp = NEGATIVE_SUBJECT_PREFIXES.get(subject.lower(), "ha")
        if tense == "present":
            # Present negative: drop TAM and shift FV to -i (except monosyllabic -la -> hali)
            fv = "i"
            # If root ends with a, replace with i
            stem = clean_root[:-1] + fv if clean_root.endswith("a") else clean_root + fv
            if is_monosyllabic:
                # Monosyllabic verbs drop ku- in negative present: hali, hanywi
                return neg_sp + clean_root[:-1] + "i" if clean_root.endswith("a") else neg_sp + clean_root + "i"
            return neg_sp + (object_marker or "") + stem
            
        elif tense == "past":
            # Past negative: TAM is -ku-
            return neg_sp + "ku" + (object_marker or "") + clean_root
            
        elif tense == "future":
            # Future negative: TAM is -ta-
            return neg_sp + "ta" + (object_marker or "") + clean_root
            
        elif tense == "perfect":
            # Perfect negative: TAM is -ja- ("not yet")
            return neg_sp + "ja" + (object_marker or "") + clean_root
            
    # Affirmative conjugation
    sp = SUBJECT_PREFIXES.get(subject.lower(), "a")
    tam = TAM_AFFIRMATIVE.get(tense.lower(), "na")
    
    # Monosyllabic rule: retain ku- if affirmative, monosyllabic, and no OP
    if is_monosyllabic and not object_marker:
        return sp + tam + "ku" + clean_root
        
    # With OP or polysyllabic: drop ku-
    op_str = object_marker if object_marker else ""
    return sp + tam + op_str + clean_root

def parse_verb_structure(verb_str: str) -> Dict[str, Any]:
    """
    Deconstruct an inflected Swahili verb into its constituent slots:
    [Subject Prefix], [TAM], [Object Prefix / ku-], [Root].
    """
    v = verb_str.lower().strip()
    is_negative = False
    sp = ""
    tam = ""
    root = ""
    has_ku = False
    
    # Check 1sg negative: starts with 'si'
    if v.startswith("si"):
        is_negative = True
        sp = "si"
        rem = v[2:]
        if rem.startswith("ku"):
            tam = "past_neg (ku)"
            root = rem[2:]
        elif rem.startswith("ta"):
            tam = "future_neg (ta)"
            root = rem[2:]
        elif rem.startswith("ja"):
            tam = "perfect_neg (ja)"
            root = rem[2:]
        else:
            tam = "present_neg"
            root = rem
        return {"verb": v, "negative": True, "sp": sp, "tam": tam, "root": root}

    # General SP identification
    for sp_candidate in ["hawa", "hatu", "haki", "havi", "hali", "haya", "hazi", "haku", "hapa", "wa", "tu", "ki", "vi", "li", "ya", "zi", "ku", "pa", "ni", "u", "a"]:
        if v.startswith(sp_candidate):
            sp = sp_candidate
            rem = v[len(sp_candidate):]
            if sp.startswith("ha"):
                is_negative = True
            break
            
    # TAM identification
    for tam_candidate in ["na", "li", "ta", "me", "ki", "nge", "ka", "ku", "ja"]:
        if rem.startswith(tam_candidate):
            tam = tam_candidate
            rem = rem[len(tam_candidate):]
            break
            
    # Check dummy ku-
    if rem.startswith("ku") and rem[2:] in MONOSYLLABIC_ROOTS:
        has_ku = True
        root = rem[2:]
    else:
        root = rem
        
    return {
        "verb": v,
        "negative": is_negative,
        "subject_prefix": sp,
        "tam": tam,
        "monosyllabic_ku": has_ku,
        "root": root
    }

def parse_verbal_template(verb_str: str) -> Dict[str, Any]:
    """Parse verbal template into canonical slots: sp, tam, rel, op, root, fv."""
    res = parse_verb_structure(verb_str)
    root = res.get("root", "")
    fv = root[-1] if (root and root[-1] in {'a', 'i', 'e', 'u', 'o'}) else "a"
    sp = res.get("subject_prefix") or res.get("sp", "")
    return {
        "verb": verb_str,
        "negative": res.get("negative", False),
        "sp": sp,
        "tam": res.get("tam", ""),
        "rel": None,
        "op": None,
        "root": root,
        "fv": fv,
        "monosyllabic_ku": res.get("monosyllabic_ku", False)
    }

