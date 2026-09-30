"""
Indonesian Engine — POS Tagging Skill
Maps Indonesian tokens to Universal Dependencies (UD) Part-of-Speech tags.
"""

from typing import List, Dict, Any

PRONOUNS = {
    "saya", "aku", "kami", "kita", "kamu", "engkau", "kau", "anda", "dia", "ia", "beliau",
    "mereka", "kalian", "ini", "itu", "siapa", "apa", "mana", "yang", "gue", "lu"
}
PREPOSITIONS = {
    "di", "ke", "dari", "pada", "kepada", "untuk", "bagi", "dengan", "tanpa", "tentang",
    "dalam", "atas", "antara", "oleh", "sampai", "seperti", "sebagai"
}
CONJUNCTIONS = {
    "dan", "atau", "tetapi", "tapi", "namun", "melainkan", "karena", "sebab", "sehingga",
    "jika", "kalau", "apabila", "meskipun", "walaupun", "bahwa", "supaya", "agar"
}
ASPECT_NEGATION = {
    "sudah", "telah", "belum", "sedang", "tengah", "lagi", "akan", "tidak", "bukan", "tak", "tiada"
}
CLASSIFIERS = {
    "orang", "ekor", "buah", "lembar", "batang", "butir", "pucuk", "bilah", "keping", "helai"
}
NUMERALS = {
    "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh",
    "sebelas", "seratus", "seribu", "sejuta", "sebuah", "seorang", "seekor", "selembar", "sebatang"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, str]]:
    """Assign UD POS tags to an Indonesian token sequence."""
    tagged = []
    for tok in tokens:
        t_clean = tok.lower().strip()
        
        # Punctuation
        if tok in {".", ",", ";", ":", "!", "?", "-", "(", ")", "\"", "'", "—"}:
            tagged.append({"token": tok, "upos": "PUNCT", "lemma": tok})
            continue
            
        if t_clean in PRONOUNS:
            tagged.append({"token": tok, "upos": "PRON", "lemma": t_clean})
        elif t_clean in PREPOSITIONS:
            tagged.append({"token": tok, "upos": "ADP", "lemma": t_clean})
        elif t_clean in CONJUNCTIONS:
            tagged.append({"token": tok, "upos": "CCONJ" if t_clean in {"dan", "atau", "tetapi", "tapi"} else "SCONJ", "lemma": t_clean})
        elif t_clean in ASPECT_NEGATION:
            tagged.append({"token": tok, "upos": "PART" if t_clean in {"tidak", "bukan", "tak"} else "AUX", "lemma": t_clean})
        elif t_clean in NUMERALS or tok.isdigit():
            tagged.append({"token": tok, "upos": "NUM", "lemma": t_clean})
        elif t_clean in CLASSIFIERS:
            tagged.append({"token": tok, "upos": "NOUN", "lemma": t_clean})
        elif t_clean.startswith(("me", "di", "ber", "ter")):
            tagged.append({"token": tok, "upos": "VERB", "lemma": t_clean})
        elif t_clean in {"sangat", "amat", "sekali", "terlalu", "cukup", "paling", "selalu", "sering", "hanya", "juga"}:
            tagged.append({"token": tok, "upos": "ADV", "lemma": t_clean})
        elif tok[0].isupper() and t_clean not in {"bapak", "ibu", "anda", "dengan"}:
            tagged.append({"token": tok, "upos": "PROPN", "lemma": tok})
        else:
            tagged.append({"token": tok, "upos": "NOUN", "lemma": t_clean})
            
    return tagged
