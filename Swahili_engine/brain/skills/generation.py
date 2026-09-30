"""
Swahili Engine — Surface Generation Skill
Generates concordial Swahili SVO clauses, agreement-verified noun phrases, and formal correspondence.
"""

from typing import Dict, Any, Optional
from .noun_class_engine import identify_noun_class
from .concord_engine import generate_concordial_np
from .verbal_template_engine import synthesize_verb

CLASS_SP_MAP = {
    1: "cl1", 2: "cl2", 3: "cl3", 4: "cl4", 5: "cl5", 6: "cl6",
    7: "cl7", 8: "cl8", 9: "cl9", 10: "cl10", 11: "cl11", 15: "cl15", 16: "cl16"
}

def generate_svo_clause(
    subject_noun: str,
    verb_root: str,
    object_noun: Optional[str] = None,
    tense: str = "present",
    include_object_prefix: bool = False
) -> str:
    """
    Generate a canonical Swahili SVO clause with verified concordial agreement.
    Example: subject='Watoto', verb_root='soma', object_noun='vitabu', tense='present'
             -> 'Watoto wanasoma vitabu.'
    """
    s_class = identify_noun_class(subject_noun)
    sp_key = CLASS_SP_MAP.get(s_class, "cl1")
    
    op_marker = None
    if object_noun and include_object_prefix:
        o_class = identify_noun_class(object_noun)
        from .verbal_template_matrix import OBJECT_PREFIXES
        op_marker = OBJECT_PREFIXES.get(f"cl{o_class}")
        
    verb = synthesize_verb(subject=sp_key, root=verb_root, tense=tense, object_marker=op_marker)
    
    # Capitalize subject
    cap_subj = subject_noun[0].upper() + subject_noun[1:] if subject_noun else ""
    
    parts = [cap_subj, verb]
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
    """Generate a formal business letter / email adhering to East African protocol."""
    salutation = f"Kwa Mheshimiwa {recipient_title} {recipient_name},"
    opening = f"Heshima kwako. Ninaandika barua hii kwa niaba ya {organization}."
    closing = "Wasalaam,\n\n" + f"Wako mwaminifu,\n{sender_name}"
    
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
    """Generate a polite, friendly everyday message."""
    opening = f"Hujambo {recipient_name},\nNatumai u mzima wa afya."
    closing = f"Wasalaam na kila la heri,\nWako rafiki,\n{sender_name}"
    return f"{opening}\n\n{body_text}\n\n{closing}"

