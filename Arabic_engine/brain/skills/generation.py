"""
Arabic Engine — Generation Skill
Synthesizes canonical VSO verbal clauses, SVO nominal clauses, agreement-verified noun phrases,
and formal business correspondence.
"""

from typing import Dict, Any, Optional
from .broken_plural_engine import analyze_plural
from .root_pattern_engine import derive_form
from .sun_moon_engine import apply_sun_moon_article

def generate_vso_clause(
    verb_root: str,
    subject_noun: str,
    object_noun: Optional[str] = None,
    tense: str = "past",
    subject_feminine: bool = False
) -> str:
    """
    Generate a canonical VSO verbal clause:
    [Verb (Singular)] + [Subject (Marfū')] + [Object (Manṣūb)]
    Example: verb_root='ktb', subject_noun='al-awlad', object_noun='al-kitab'
             -> 'Kataba al-awlad al-kitab.'
    """
    derived = derive_form(verb_root, "I")
    v = derived["past"] if tense == "past" else derived["present"]
    
    # Feminine adjustment for singular verb in VSO
    if subject_feminine:
        if tense == "past":
            v = v + "at" if v.endswith("a") else v + "at"
        else:
            v = "t" + v[1:] if v.startswith("y") else v
            
    cap_v = v[0].upper() + v[1:] if v else ""
    parts = [cap_v, subject_noun]
    if object_noun:
        parts.append(object_noun)
        
    return " ".join(parts) + "."

def generate_svo_clause(
    subject_noun: str,
    verb_root: str,
    object_noun: Optional[str] = None,
    tense: str = "past"
) -> str:
    """
    Generate an SVO nominal clause:
    [Subject] + [Verb (Full Concord / Deflected)] + [Object]
    """
    s_info = analyze_plural(subject_noun)
    derived = derive_form(verb_root, "I")
    base_v = derived["past"] if tense == "past" else derived["present"]
    
    if s_info["is_plural"]:
        if s_info["requires_deflected_agreement"]:
            # Non-human plural: feminine singular verb
            v = base_v + "at" if tense == "past" else ("t" + base_v[1:] if base_v.startswith("y") else base_v)
        else:
            # Human plural: plural verb suffix -u
            v = base_v + "u" if tense == "past" else (base_v + "una")
    else:
        v = base_v
        
    cap_s = subject_noun[0].upper() + subject_noun[1:] if subject_noun else ""
    parts = [cap_s, v]
    if object_noun:
        parts.append(object_noun)
        
    return " ".join(parts) + "."

def generate_formal_email(
    recipient_name: str,
    recipient_title: str,
    body_text: str,
    sender_name: str,
    organization: str = "Solo Rock"
) -> str:
    """Generate formal business letter adhering to Pan-Arab diplomatic protocol."""
    salutation = f"سعادة {recipient_title} / {recipient_name} المحترم،"
    opening = "تحية طيبة وبعد،"
    closing = "وتفضلوا بقبول فائق الاحترام والتقدير،\n\n" + f"{sender_name}\nشركة {organization}"
    
    lines = [
        salutation,
        "",
        opening,
        "",
        body_text,
        "",
        closing
    ]
    return "\n".join(lines)

def generate_polite_message(
    recipient_name: str,
    body_text: str,
    sender_name: str
) -> str:
    """Generate friendly polite correspondence."""
    opening = f"عزيزي {recipient_name}،\nالسلام عليكم ورحمة الله وبركاته."
    closing = f"مع خالص التحيات والتقدير،\n{sender_name}"
    return f"{opening}\n\n{body_text}\n\n{closing}"
