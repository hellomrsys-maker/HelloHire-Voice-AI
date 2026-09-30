"""
Arabic Engine — Concordial Agreement Skill
Implements the rules of Arabic clausal and phrasal concord:
1. VSO Partial Agreement (Singular verb before post-verbal subject)
2. SVO Full Agreement (Subject precedes verb with full number/gender concord)
3. Deflected Agreement (All non-human plurals trigger Feminine Singular concord)
"""

from typing import Dict, Any, Optional
from .broken_plural_engine import analyze_plural

def is_feminine_adjective(adj: str) -> bool:
    """Check if adjective has feminine marker (e.g. ends with 'a', 'ah', 'at', or 'ya')."""
    clean = adj.lower().replace("al-", "").replace("al", "").strip()
    return clean.endswith("a") or clean.endswith("ah") or clean.endswith("at") or clean.endswith("ya")

def is_plural_verb(verb: str) -> bool:
    """Check if verb contains plural inflection suffixes (e.g. -u, -w, -na, -una)."""
    v = verb.lower().strip()
    return (
        v.endswith("u") or v.endswith("w") or v.endswith("oo") or
        v.endswith("na") or v.endswith("una") or v.endswith("un")
    )

def is_feminine_verb(verb: str) -> bool:
    """Check if verb has 3rd person feminine marker (prefix 't-' or suffix '-at')."""
    v = verb.lower().strip()
    return v.startswith("t") or v.endswith("at") or v.endswith("et")

def validate_vso_agreement(verb: str, subject: str) -> Dict[str, Any]:
    """
    Validate VSO Word Order agreement:
    In VSO, the verb MUST be singular regardless of subject number.
    It matches only in gender.
    """
    s_info = analyze_plural(subject)
    v_is_plural = is_plural_verb(verb)
    
    # If verb is plural before an overt subject, it violates classical VSO agreement!
    if v_is_plural:
        return {
            "valid": False,
            "order": "VSO",
            "verb": verb,
            "subject": subject,
            "error": f"VSO order violation: Verb '{verb}' must be singular before overt post-verbal subject '{subject}'"
        }
        
    return {
        "valid": True,
        "order": "VSO",
        "verb": verb,
        "subject": subject,
        "is_singular_verb": True
    }

def validate_svo_agreement(subject: str, verb: str) -> Dict[str, Any]:
    """
    Validate SVO Word Order agreement:
    In SVO, if the subject is plural:
    - If human plural: verb must be plural!
    - If non-human plural: verb must be feminine singular (deflected agreement)!
    """
    s_info = analyze_plural(subject)
    
    if s_info["is_plural"]:
        if s_info["requires_deflected_agreement"]:
            # Non-human plural requires feminine singular verb
            fem_v = is_feminine_verb(verb)
            pl_v = is_plural_verb(verb)
            valid = fem_v and not pl_v
            return {
                "valid": valid,
                "order": "SVO",
                "subject": subject,
                "verb": verb,
                "rule": "deflected_agreement_non_human_plural",
                "error": None if valid else f"Non-human plural '{subject}' requires feminine singular verb, not '{verb}'"
            }
        else:
            # Human plural requires plural verb
            pl_v = is_plural_verb(verb)
            return {
                "valid": pl_v,
                "order": "SVO",
                "subject": subject,
                "verb": verb,
                "rule": "human_plural_full_concord",
                "error": None if pl_v else f"Human plural '{subject}' requires plural verb, not singular '{verb}'"
            }
            
    return {"valid": True, "order": "SVO", "subject": subject, "verb": verb}

def validate_noun_adjective_agreement(noun: str, adjective: str) -> Dict[str, Any]:
    """
    Validate Noun-Adjective concord including Deflected Agreement:
    - Non-human plural nouns MUST take Feminine Singular adjectives!
    - Demonstratives for non-human plurals must be 'hadhihi', NOT 'ha'ula'i'.
    """
    n_info = analyze_plural(noun)
    adj_clean = adjective.lower().replace("al-", "").replace("al", "").strip()
    
    if n_info["is_plural"] and n_info["requires_deflected_agreement"]:
        # Non-human plural: adjective MUST be feminine singular
        is_fem = is_feminine_adjective(adj_clean)
        # Check demonstrative
        if adj_clean in {"ha'ula'i", "haolai", "haula"}:
            return {
                "valid": False,
                "noun": noun,
                "modifier": adjective,
                "error": f"Demonstrative '{adjective}' is strictly for human plurals; non-human plural '{noun}' requires 'hadhihi'"
            }
        if not is_fem:
            return {
                "valid": False,
                "noun": noun,
                "modifier": adjective,
                "error": f"Deflected agreement violation: Non-human plural '{noun}' requires feminine singular adjective (e.g. ending in -a/-at), not '{adjective}'"
            }
            
    return {"valid": True, "noun": noun, "modifier": adjective}
