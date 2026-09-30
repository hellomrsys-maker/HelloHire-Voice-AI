"""
Indonesian Engine — Aspect & Negation Engine Skill
Audits aspectual particles (sudah, belum, sedang, akan) and negation distribution (tidak vs bukan).
"""

from typing import Dict, Any, List

def validate_negation(negator: str, next_word_pos: str, next_word: str) -> Dict[str, Any]:
    """
    Validate Indonesian negation syntax:
    - 'tidak' negates verbs, adjectives, prepositions
    - 'bukan' negates nouns, pronouns, identity predicates
    """
    neg = negator.lower().strip()
    pos = next_word_pos.upper().strip()
    w = next_word.lower().strip()
    
    violations = []
    
    if neg in {"tidak", "tak"}:
        if pos in {"NOUN", "PRON", "PROPN"}:
            violations.append({
                "negator": neg,
                "target": next_word,
                "rule": "negation_tidak_with_noun",
                "error": f"'tidak' cannot negate noun '{next_word}'. Use 'bukan' for nouns/pronouns."
            })
    elif neg == "bukan":
        if pos in {"VERB", "AUX"} and not w.startswith("adalah"):
            violations.append({
                "negator": neg,
                "target": next_word,
                "rule": "negation_bukan_with_verb",
                "error": f"'bukan' cannot negate main verb '{next_word}'. Use 'tidak' for verbs."
            })
            
    return {
        "valid": len(violations) == 0,
        "negator": neg,
        "target": next_word,
        "violations": violations
    }

def detect_aspect(text: str) -> Dict[str, Any]:
    """Scan text for Indonesian aspectual particles."""
    t_clean = text.lower()
    tokens = t_clean.split()
    
    aspects = []
    if "sudah" in tokens or "telah" in tokens:
        aspects.append("perfective")
    if "belum" in tokens:
        aspects.append("negative_perfective")
    if "sedang" in tokens or "tengah" in tokens:
        aspects.append("progressive")
    if "akan" in tokens:
        aspects.append("prospective")
        
    return {
        "has_aspect": len(aspects) > 0,
        "aspects": aspects
    }
