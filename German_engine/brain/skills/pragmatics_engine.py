"""
German Engine — Pragmatics & Register Skill
Handles Duzen vs. Siezen classification, register consistency, honorifics, and epistolary etiquette.
"""

from typing import List, Dict, Any

INFORMAL_PRONOUNS = {
    "du", "dich", "dir", "dein", "deine", "deinem", "deinen", "deiner", "deines",
    "ihr", "euch", "euer", "eure", "eurem", "euren", "eurer", "eures"
}

FORMAL_PRONOUNS = {
    "sie", "ihnen", "ihr", "ihre", "ihrem", "ihren", "ihrer", "ihres"
}

FORMAL_SALUTATIONS = [
    "sehr geehrte damen und herren",
    "sehr geehrte frau",
    "sehr geehrter herr",
    "guten tag, frau",
    "guten tag, herr"
]

INFORMAL_SALUTATIONS = [
    "liebe", "lieber", "hallo", "hi", "servus", "moin"
]

FORMAL_CLOSINGS = [
    "mit freundlichen grüßen",
    "mit besten grüßen",
    "freundliche grüße"
]

INFORMAL_CLOSINGS = [
    "liebe grüße", "herzliche grüße", "viele grüße", "bis bald", "tschüss"
]

def analyze_register(text: str, tokens: List[str]) -> Dict[str, Any]:
    """
    Analyze text for Duzen (informal), Siezen (formal), or Neutral register.
    Detect register clash if both informal and formal address occur.
    """
    text_lower = text.lower()
    informal_hits = []
    formal_hits = []
    
    for token in tokens:
        lower = token.lower()
        if lower in INFORMAL_PRONOUNS:
            informal_hits.append(token)
        # Check capitalized Sie/Ihnen/Ihr
        elif token in {"Sie", "Ihnen", "Ihr", "Ihre", "Ihrem", "Ihren", "Ihrer", "Ihres"}:
            formal_hits.append(token)
            
    # Check salutations
    is_formal_salutation = any(sal in text_lower for sal in FORMAL_SALUTATIONS)
    is_informal_salutation = any(sal in text_lower for sal in INFORMAL_SALUTATIONS)
    
    # Check closings
    is_formal_closing = any(close in text_lower for close in FORMAL_CLOSINGS)
    is_informal_closing = any(close in text_lower for close in INFORMAL_CLOSINGS)
    
    if is_formal_salutation or is_formal_closing:
        formal_hits.append("FORMAL_TEMPLATE")
    if is_informal_salutation or is_informal_closing:
        informal_hits.append("INFORMAL_TEMPLATE")
        
    has_informal = len(informal_hits) > 0
    has_formal = len(formal_hits) > 0
    
    if has_informal and has_formal:
        register = "mixed_clash"
    elif has_formal:
        register = "siezen"
    elif has_informal:
        register = "duzen"
    else:
        register = "neutral"
        
    return {
        "register": register,
        "informal_count": len(informal_hits),
        "formal_count": len(formal_hits),
        "informal_tokens": informal_hits,
        "formal_tokens": formal_hits,
        "is_consistent": register != "mixed_clash"
    }

def validate_substantive_capitalization(tokens: List[str], pos_tags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check if substantives are properly capitalized in German.
    """
    violations = []
    for i, tag in enumerate(pos_tags):
        token = tag["token"]
        # Skip sentence initial
        if i == 0:
            continue
        # If tagger classified as NOUN but token starts with lowercase
        if tag.get("upos") == "NOUN" and token[0].islower():
            violations.append({
                "index": i,
                "token": token,
                "suggested": token.capitalize(),
                "rule": "Substantive-Großschreibung"
            })
    return violations
