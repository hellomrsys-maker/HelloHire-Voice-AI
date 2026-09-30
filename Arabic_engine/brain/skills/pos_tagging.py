"""
Arabic Engine — Part-of-Speech Tagging Skill
Provides Universal POS (UPOS) tagging and linguistic categorization for Arabic tokens.
"""

from typing import List, Dict, Any
from .broken_plural_engine import PLURAL_DATABASE, PLURAL_TO_SINGULAR

PRONOUNS = {
    "ana", "anta", "anti", "huwa", "hiya", "nahnu", "antum", "antunna", "hum", "hunna",
    "أنا", "أنت", "أنتِ", "هو", "هي", "نحن", "أنتم", "أنتن", "هم", "هن"
}

PREPOSITIONS = {
    "fi", "min", "ila", "'ala", "ala", "'an", "an", "ma'a", "hatta", "mundhu", "bayna",
    "في", "من", "إلى", "على", "عن", "مع", "حتى", "منذ", "بين"
}

CONJUNCTIONS = {
    "wa", "fa", "thumma", "aw", "lakin", "inna", "anna", "li'anna", "idha",
    "و", "ف", "ثم", "أو", "لكن", "إن", "أن", "لأن", "إذا"
}

DEMONSTRATIVES = {
    "hadha", "hadhihi", "dhalika", "tilka", "ha'ula'i", "haolai", "haula", "ula'ika",
    "هذا", "هذه", "ذلك", "تلك", "هؤلاء", "أولئك"
}

ADJECTIVE_STEMS = {
    "kabir", "saghir", "jadid", "qadim", "jamil", "jayyid", "karim", "tawil", "qasir",
    "shahir", "sari'", "batin", "sahil", "sa'b", "mumtaz", "mufid", "hasan",
    "كبير", "صغير", "جديد", "قديم", "جميل", "جيد", "كريم", "طويل", "قصير", "مفيد"
}

COMMON_VERBS = {
    "kataba", "katabat", "katabu", "yaktubu", "taktubu", "yaktubuna",
    "qara'a", "qara'at", "qara'u", "yaqra'u", "taqra'u", "yaqra'una",
    "darasa", "darasat", "darasu", "yadrusu", "tadrusu",
    "dhahaba", "dhahabat", "dhahabu", "yadhhabu", "tadhhabu", "yadhhabuna",
    "ja'a", "ja'at", "ja'u", "yaji'u", "taji'u",
    "wasala", "wasalat", "wasalu", "yasilu", "tasilu",
    "tufidu", "yufidu", "tawaqqafat", "inkasara", "ijtama'a", "istakhraja"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, Any]]:
    """Tag Arabic tokens with UPOS and linguistic properties."""
    tagged = []
    
    for token in tokens:
        lower = token.lower().strip()
        stem = lower.replace("al-", "").replace("al", "").strip()
        
        if token in {".", ",", "!", "?", "؟", "،", "؛", ":", ";", "\"", "'", "-", "–"}:
            tagged.append({"token": token, "word": token, "upos": "PUNCT", "lemma": token})
            continue
            
        if lower in PRONOUNS:
            tagged.append({"token": token, "word": token, "upos": "PRON", "lemma": lower})
            continue
            
        if lower in DEMONSTRATIVES or stem in DEMONSTRATIVES:
            tagged.append({"token": token, "word": token, "upos": "DET", "lemma": lower})
            continue
            
        if lower in PREPOSITIONS:
            tagged.append({"token": token, "word": token, "upos": "ADP", "lemma": lower})
            continue
            
        if lower in CONJUNCTIONS:
            tagged.append({"token": token, "word": token, "upos": "CCONJ", "lemma": lower})
            continue
            
        # Adjectives (including feminine forms ending in -a or -at)
        is_adj = stem in ADJECTIVE_STEMS or any(stem.startswith(adj) for adj in ADJECTIVE_STEMS)
        if is_adj:
            tagged.append({"token": token, "word": token, "upos": "ADJ", "lemma": stem})
            continue
            
        # Check known plural / singular nouns
        if stem in PLURAL_DATABASE or stem in PLURAL_TO_SINGULAR:
            tagged.append({"token": token, "word": token, "upos": "NOUN", "lemma": stem})
            continue
            
        # Verbs
        if lower in COMMON_VERBS or stem in COMMON_VERBS:
            tagged.append({"token": token, "word": token, "upos": "VERB", "lemma": stem})
            continue
            
        # Verbal prefix heuristics (ya-, ta-, na-, a-)
        if len(lower) >= 4 and (lower.startswith("ya") or lower.startswith("ta") or lower.startswith("yu") or lower.startswith("tu")):
            if not (lower.startswith("al-") or lower.startswith("al")):
                tagged.append({"token": token, "word": token, "upos": "VERB", "lemma": lower})
                continue
                
        # Default to NOUN
        tagged.append({"token": token, "word": token, "upos": "NOUN", "lemma": stem})
        
    return tagged
