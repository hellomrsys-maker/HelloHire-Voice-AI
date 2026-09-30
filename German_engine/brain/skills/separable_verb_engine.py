"""
German Engine — Separable Verb Engine Skill
Handles identification, splitting, and Satzklammer re-unification of separable verbs (Trennbare Verben).
"""

from typing import List, Dict, Any, Optional, Tuple

SEPARABLE_PREFIXES = [
    "ab", "an", "auf", "aus", "bei", "dar", "ein", "empor", "entgegen", "entlang",
    "fehl", "fest", "fort", "frei", "gegenüber", "heim", "her", "heran", "herauf",
    "heraus", "herbei", "herein", "herüber", "herum", "herunter", "hervor", "hin",
    "hinab", "hinauf", "hinaus", "hinein", "hinterher", "hinüber", "hinunter", "hinweg",
    "hinzu", "los", "mit", "nach", "nieder", "statt", "teil", "vor", "voran", "voraus",
    "vorbei", "vorher", "vorüber", "weg", "weiter", "wieder", "zu", "zurecht", "zurück", "zusammen"
]

COMMON_VERB_STEMS = {
    "stehen", "stehen", "steht", "stand", "gestanden",
    "gehen", "geht", "ging", "gegangen",
    "fangen", "fängt", "fing", "gefangen",
    "kommen", "kommt", "kam", "gekommen",
    "machen", "macht", "machte", "gemacht",
    "hören", "hört", "hörte", "gehört",
    "geben", "gibt", "gab", "gegeben",
    "bereiten", "bereitet", "bereitete", "bereitet",
    "nehmen", "nimmt", "nahm", "genommen",
    "schlagen", "schlägt", "schlug", "geschlagen",
    "bringen", "bringt", "brachte", "gebracht",
    "sehen", "sieht", "sah", "gesehen",
    "rufen", "ruft", "rief", "gerufen",
    "reisen", "reist", "reiste", "gereist"
}

def is_separable_prefix(token: str) -> bool:
    """Check if token is a standard separable prefix."""
    return token.lower() in SEPARABLE_PREFIXES

def split_infinitive(infinitive: str) -> Optional[Tuple[str, str]]:
    """
    Given an infinitive like 'aufstehen', split into prefix ('auf') and base ('stehen').
    """
    inf_lower = infinitive.lower()
    for prefix in sorted(SEPARABLE_PREFIXES, key=len, reverse=True):
        if inf_lower.startswith(prefix) and len(inf_lower) > len(prefix) + 2:
            base = inf_lower[len(prefix):]
            if base in COMMON_VERB_STEMS or base.endswith("en") or base.endswith("eln") or base.endswith("ern"):
                return prefix, base
    return None

def detect_clause_separable_verb(tokens: List[str]) -> Optional[Dict[str, Any]]:
    """
    Detect if a main clause has a finite verb in position 2 (or 1) and a separable prefix at the end.
    Example: ['Er', 'steht', 'morgen', 'früh', 'auf', '.']
    """
    if len(tokens) < 3:
        return None
        
    # Strip terminal punctuation for scanning
    clean_tokens = [t for t in tokens if t not in {".", "!", "?", ",", ";", ":"}]
    if not clean_tokens:
        return None
        
    # Check if last token is a separable prefix
    last_token = clean_tokens[-1].lower()
    if last_token not in SEPARABLE_PREFIXES:
        return None
        
    # Find potential finite verb in positions 0, 1, 2
    for pos in range(min(3, len(clean_tokens) - 1)):
        candidate = clean_tokens[pos].lower()
        if candidate in COMMON_VERB_STEMS or candidate.endswith(("t", "st", "te", "ten", "en")):
            reunified_lemma = last_token + candidate
            return {
                "has_separable_verb": True,
                "prefix": last_token,
                "prefix_index": len(tokens) - 1 if tokens[-1] not in {".", "!", "?"} else len(tokens) - 2,
                "verb_stem": clean_tokens[pos],
                "verb_index": pos,
                "unified_lemma_approx": reunified_lemma
            }
            
    return None
