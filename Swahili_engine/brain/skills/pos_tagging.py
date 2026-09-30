"""
Swahili Engine — Part-of-Speech Tagging Skill
Provides UPOS and morphological tagging for Swahili tokens.
"""

from typing import List, Dict, Any

PRONOUNS = {"mimi", "wewe", "yeye", "sisi", "ninyi", "wao"}

PREPOSITIONS = {"kwa", "katika", "na", "bila", "tangu", "hadi", "mpaka", "mbele ya", "nyuma ya"}

CONJUNCTIONS = {"na", "lakini", "au", "kwa sababu", "ingawa", "ili", "tena", "kama"}

ADVERBS = {"sana", "polepole", "haraka", "leo", "kesho", "jana", "hapa", "pale", "sasa", "tu", "bado", "zaidi"}

DEMONSTRATIVES_SET = {
    "huyu", "yule", "hawa", "wale", "huu", "ule", "hii", "ile",
    "hili", "lile", "haya", "yale", "hiki", "kile", "hivi", "vile",
    "hizi", "zile", "huku", "kule", "hapa", "pale", "humu", "mle"
}

ADJECTIVE_STEMS = [
    "zuri", "dogo", "kubwa", "baya", "refu", "fupi", "chache",
    "tamu", "pya", "kali", "tupu", "epesi", "gumu", "zee"
]

INVARIABLE_ADJECTIVES = {
    "safi", "bora", "ghali", "rahisi", "kamili", "wazi", "hodari", "maalum"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, Any]]:
    """Tag Swahili tokens with UPOS and linguistic attributes."""
    tagged = []
    
    for token in tokens:
        lower = token.lower()
        
        if token in {".", ",", "!", "?", ":", ";", "\"", "'", "-", "–"}:
            tagged.append({"token": token, "word": token, "upos": "PUNCT", "lemma": token})
            continue
            
        if lower in PRONOUNS:
            tagged.append({"token": token, "word": token, "upos": "PRON", "lemma": lower})
            continue
            
        if lower in DEMONSTRATIVES_SET:
            tagged.append({"token": token, "word": token, "upos": "DET", "lemma": lower})
            continue
            
        if lower in PREPOSITIONS:
            tagged.append({"token": token, "word": token, "upos": "ADP", "lemma": lower})
            continue
            
        if lower in CONJUNCTIONS:
            tagged.append({"token": token, "word": token, "upos": "CCONJ", "lemma": lower})
            continue
            
        if lower in ADVERBS:
            tagged.append({"token": token, "word": token, "upos": "ADV", "lemma": lower})
            continue
            
        # Adjectives (checked before verbs to avoid misclassifying words like kizuri, vizuri, wazuri)
        if lower in INVARIABLE_ADJECTIVES or any(lower.endswith(adj) for adj in ADJECTIVE_STEMS):
            tagged.append({"token": token, "word": token, "upos": "ADJ", "lemma": lower})
            continue

        # Known Swahili nouns (e.g. kitabu, vitabu, chakula, vyakula, etc. to avoid false verb matching)
        from .noun_class_engine import NOUN_CLASS_LEXICON
        if lower in NOUN_CLASS_LEXICON:
            tagged.append({"token": token, "word": token, "upos": "NOUN", "lemma": lower})
            continue


        # Common verb prefix chains: anasoma, alikula, ninasoma, wanasoma, etc.
        # Starts with SP + TAM
        is_verb = False
        for sp in ["wa", "tu", "ni", "u", "a", "ki", "vi", "li", "ya", "si", "ha", "hawa", "hatu"]:
            if lower.startswith(sp):
                rem = lower[len(sp):]
                if any(rem.startswith(tam) for tam in ["na", "li", "ta", "me", "ki", "nge", "ku", "ja", "ka"]) and len(lower) >= 4:
                    is_verb = True
                    break
                    
        # Infinitives (ku-)
        if not is_verb and lower.startswith("ku") and len(lower) >= 4:
            if lower.endswith("a") or lower.endswith("i") or lower.endswith("e"):
                is_verb = True

        if is_verb:
            tagged.append({"token": token, "word": token, "upos": "VERB", "lemma": lower})
            continue
            
        # Default to noun
        tagged.append({"token": token, "word": token, "upos": "NOUN", "lemma": lower})
        
    return tagged
