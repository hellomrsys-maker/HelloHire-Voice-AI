"""
Italian Engine — POS Tagging Skill
Maps Italian tokens to Universal Dependencies (UD) Part-of-Speech tags.
"""

from typing import List, Dict, Any

# Closed-class function word dictionaries
ARTICLES = {
    "il", "lo", "la", "l'", "i", "gli", "le", "un", "uno", "una", "un'"
}
ARTICULATED_PREPS = {
    "del", "dello", "dell'", "della", "dei", "degli", "delle",
    "al", "allo", "all'", "alla", "ai", "agli", "alle",
    "dal", "dallo", "dall'", "dalla", "dai", "dagli", "dalle",
    "nel", "nello", "nell'", "nella", "nei", "negli", "nelle",
    "sul", "sullo", "sull'", "sulla", "sui", "sugli", "sulle"
}
PREPOSITIONS = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra", "senza", "verso", "sopra", "sotto"
}
PRONOUNS = {
    "io", "tu", "lui", "lei", "noi", "voi", "loro", "esso", "essa", "essi", "esse",
    "mi", "ti", "lo", "la", "gli", "le", "ci", "vi", "si", "ne",
    "me", "te", "sé", "ce", "ve", "glielo", "gliela", "glieli", "gliele", "gliene",
    "questo", "quello", "chi", "che", "cui", "quale"
}
AUXILIARY_VERBS = {
    "sono", "sei", "è", "siamo", "siete", "era", "eri", "eravamo", "eravate", "erano",
    "fui", "fosti", "fu", "fummo", "foste", "furono", "sarò", "sarai", "sarà", "saremo",
    "sarete", "saranno", "sia", "siate", "siano", "fossi", "fosse", "fossimo", "fossero",
    "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero", "essendo", "stato",
    "stata", "stati", "state",
    "ho", "hai", "ha", "abbiamo", "avete", "hanno", "avevo", "avevi", "aveva", "avevamo",
    "avevate", "avevano", "ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero",
    "avrò", "avrai", "avrà", "avremo", "avrete", "avranno", "abbia", "abbiate", "abbiano",
    "avessi", "avesse", "avessimo", "avessero", "avrei", "avresti", "avrebbe", "avremmo",
    "avreste", "avrebbero", "avendo", "avuto", "avuta", "avuti", "avute",
    "sto", "stai", "sta", "stiamo", "state", "stanno", "stava", "stavo"
}
CONJUNCTIONS = {
    "e", "ed", "o", "ma", "però", "tuttavia", "quindi", "dunque", "perché", "poiché",
    "se", "mentre", "quando", "affinché", "benché", "sebbene"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, str]]:
    """Assign UD POS tags to a tokenized sequence."""
    tagged = []
    for tok in tokens:
        t_clean = tok.lower().strip()
        
        # Punctuation
        if tok in {".", ",", ";", ":", "!", "?", "...", "-", "(", ")", "\"", "'", "«", "»"}:
            tagged.append({"token": tok, "upos": "PUNCT", "lemma": tok})
            continue
            
        # Articles and prepositions
        if t_clean in ARTICLES:
            tagged.append({"token": tok, "upos": "DET", "lemma": "il"})
        elif t_clean in ARTICULATED_PREPS:
            tagged.append({"token": tok, "upos": "ADP", "lemma": t_clean})
        elif t_clean in PREPOSITIONS:
            tagged.append({"token": tok, "upos": "ADP", "lemma": t_clean})
        elif t_clean in PRONOUNS:
            tagged.append({"token": tok, "upos": "PRON", "lemma": t_clean})
        elif t_clean in AUXILIARY_VERBS:
            tagged.append({"token": tok, "upos": "AUX", "lemma": "essere" if t_clean.startswith("s") or t_clean.startswith("è") else "avere"})
        elif t_clean in CONJUNCTIONS:
            tagged.append({"token": tok, "upos": "CCONJ" if t_clean in {"e", "ed", "o", "ma"} else "SCONJ", "lemma": t_clean})
        elif t_clean.endswith("mente"):
            tagged.append({"token": tok, "upos": "ADV", "lemma": t_clean})
        elif t_clean in {"non", "mai", "sempre", "più", "molto", "bene", "male", "già", "allora", "mica"}:
            tagged.append({"token": tok, "upos": "ADV", "lemma": t_clean})
        elif tok[0].isupper() and t_clean not in {"il", "la", "i", "gli", "le", "un", "una", "gentile", "egregio"}:
            tagged.append({"token": tok, "upos": "PROPN", "lemma": tok})
        elif t_clean.endswith(("are", "ere", "ire", "ando", "endo", "ato", "uto", "ito", "ata", "uta", "ita")):
            tagged.append({"token": tok, "upos": "VERB", "lemma": tok})
        else:
            tagged.append({"token": tok, "upos": "NOUN", "lemma": tok})
            
    return tagged
