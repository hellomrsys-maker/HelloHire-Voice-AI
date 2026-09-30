"""
Arabic Engine — Idafa Construct Engine Skill
Validates and synthesizes the Genitive Construct (الإضافة - al-Idafa):
- Mudāf (Term 1): Forbids definite article 'al-' and nunation (tanwīn); drops dual/sound plural -n.
- Mudāf Ilayh (Term 2): Obligatorily genitive (Majrūr).
"""

from typing import Dict, Any

def validate_idafa(mudaf: str, mudaf_ilayh: str) -> Dict[str, Any]:
    """
    Validate syntactic constraints on an Idafa construct:
    [Mudāf] + [Mudāf Ilayh]
    """
    m_clean = mudaf.lower().strip()
    mi_clean = mudaf_ilayh.lower().strip()
    
    violations = []
    
    # Rule 1: Mudāf must never take 'al-'
    if m_clean.startswith("al-") or m_clean.startswith("al"):
        violations.append({
            "term": mudaf,
            "rule": "mudaf_no_al",
            "error": f"Mudāf '{mudaf}' must not take the definite article 'al-'"
        })
        
    # Rule 2: Mudāf must never have tanwīn (-un, -an, -in)
    if m_clean.endswith("un") or m_clean.endswith("an") or m_clean.endswith("in"):
        # Except if part of root (like 'tin' or 'jinn')
        if len(m_clean) > 4:
            violations.append({
                "term": mudaf,
                "rule": "mudaf_no_tanwin",
                "error": f"Mudāf '{mudaf}' must not take nunation (tanwīn)"
            })
            
    # Rule 3: Mudāf must drop dual -ani/-ayni and plural -una/-ina nūn
    if m_clean.endswith("ani") or m_clean.endswith("una"):
        violations.append({
            "term": mudaf,
            "rule": "mudaf_drop_nuun",
            "error": f"Mudāf '{mudaf}' must drop terminal nūn in dual/sound plural constructs"
        })
        
    return {
        "valid": len(violations) == 0,
        "mudaf": mudaf,
        "mudaf_ilayh": mudaf_ilayh,
        "violations": violations
    }

def synthesize_idafa(mudaf_singular: str, mudaf_ilayh: str, term2_definite: bool = True) -> str:
    """
    Synthesize an Idafa construct ensuring Mudāf lacks 'al-' and Mudāf Ilayh has appropriate definiteness.
    Example: mudaf='kitab', mudaf_ilayh='rajul', term2_definite=True -> 'kitab ar-rajul' (or 'kitabu ar-rajuli')
    """
    m = mudaf_singular.lower().replace("al-", "").replace("al", "").strip()
    # Strip any tanwin
    if m.endswith("un") or m.endswith("an") or m.endswith("in"):
        if len(m) > 4:
            m = m[:-2]
            
    mi = mudaf_ilayh.lower().strip()
    if term2_definite and not (mi.startswith("al-") or mi.startswith("al")):
        from .sun_moon_engine import apply_sun_moon_article
        mi = apply_sun_moon_article(mi)
        
    return f"{m} {mi}"
