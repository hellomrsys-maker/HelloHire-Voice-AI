"""
German Engine — Part of Speech (POS) Tagging Skill
Provides STTS and UPOS annotations for German tokens,
with special awareness of substantive capitalization and modal particles.
"""

from typing import List, Dict, Any

# Common closed-class lexicons
ARTICLES = {
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einen", "einem", "einer", "eines",
    "kein", "keine", "keinen", "keinem", "keiner", "keines"
}

DEMONSTRATIVES = {
    "dieser", "diese", "dieses", "diesen", "diesem",
    "jener", "jene", "jenes", "jeder", "jede", "jedes"
}

PRONOUNS_PERSONAL = {
    "ich", "du", "er", "sie", "es", "wir", "ihr",
    "mich", "dich", "ihn", "uns", "euch",
    "mir", "dir", "ihm", "ihr", "ihnen",
    "Sie", "Ihnen", "sich"
}

PRONOUNS_POSSESSIVE = {
    "mein", "meine", "meinem", "meinen", "meiner", "meines",
    "dein", "deine", "deinem", "deinen", "deiner", "deines",
    "sein", "seine", "seinem", "seinen", "seiner", "seines",
    "ihr", "ihre", "ihrem", "ihren", "ihrer", "ihres",
    "unser", "unsere", "unserem", "unseren", "unserer", "unseres",
    "euer", "eure", "eurem", "euren", "eurer", "eures",
    "Ihr", "Ihre", "Ihrem", "Ihren", "Ihrer", "Ihres"
}

PREPOSITIONS = {
    "an", "auf", "aus", "bei", "bis", "durch", "für", "gegen", "gegenüber",
    "hinter", "in", "mit", "nach", "neben", "ohne", "seit", "trotz", "über",
    "um", "unter", "von", "vor", "während", "wegen", "zu", "zwischen",
    "ans", "am", "aufs", "beim", "durchs", "fürs", "im", "ins", "ums", "vom", "zum", "zur"
}

COORDINATING_CONJUNCTIONS = {
    "und", "oder", "aber", "denn", "sondern", "doch"
}

SUBORDINATING_CONJUNCTIONS = {
    "weil", "dass", "daß", "da", "wenn", "ob", "obwohl", "obgleich", "während",
    "bevor", "ehe", "nachdem", "damit", "sodass", "so dass", "falls", "seitdem"
}

MODAL_PARTICLES = {
    "ja", "doch", "mal", "denn", "eben", "halt", "wohl", "schon", "bloß", "nur"
}

MODAL_VERBS = {
    "können", "kann", "kannst", "könnt", "konnte", "konntest", "konnten", "könnte",
    "müssen", "muss", "musst", "müsst", "musste", "musstest", "mussten", "müsste",
    "dürfen", "darf", "darfst", "dürft", "durfte", "durftest", "durften", "dürfte",
    "sollen", "soll", "sollst", "sollt", "sollte", "solltest", "sollten",
    "wollen", "will", "willst", "wollt", "wollte", "wolltest", "wollten",
    "mögen", "mag", "magst", "mögt", "mochte", "mochtest", "mochten", "möchte", "möchtest", "möchten"
}

AUXILIARIES = {
    "sein", "bin", "bist", "ist", "sind", "seid", "war", "warst", "waren", "wart", "wäre", "wären", "gewesen",
    "haben", "habe", "hast", "hat", "haben", "habt", "hatte", "hattest", "hatten", "hattet", "hätte", "hätten", "gehabt",
    "werden", "werde", "wirst", "wird", "werden", "werdet", "wurde", "wurdest", "wurden", "würde", "würden", "geworden"
}

ADVERBS = {
    "heute", "gestern", "morgen", "jetzt", "oft", "immer", "nie", "manchmal",
    "hier", "dort", "da", "oben", "unten", "links", "rechts",
    "sehr", "besonders", "extrem", "kaum", "leider", "glücklicherweise", "gern", "gerne"
}

def tag_pos(tokens: List[str]) -> List[Dict[str, Any]]:
    """
    Assign UPOS and STTS tags to tokens with morphological clues.
    """
    tagged = []
    
    for i, token in enumerate(tokens):
        lower = token.lower()
        
        # Punctuation
        if token in {".", ",", "!", "?", ":", ";", "-", "–", "„", "“", "\"", "'", "(", ")"}:
            tagged.append({"token": token, "upos": "PUNCT", "stts": "$." if token in ".!?" else "$,", "lemma": token})
            continue
            
        # Particles
        if lower == "nicht":
            tagged.append({"token": token, "upos": "PART", "stts": "PTKNEG", "lemma": "nicht"})
            continue
        if lower == "zu" and i + 1 < len(tokens) and tokens[i+1].endswith("en"):
            tagged.append({"token": token, "upos": "PART", "stts": "PTKZU", "lemma": "zu"})
            continue
            
        # Conjunctions
        if lower in COORDINATING_CONJUNCTIONS:
            tagged.append({"token": token, "upos": "CCONJ", "stts": "KON", "lemma": lower})
            continue
        if lower in SUBORDINATING_CONJUNCTIONS:
            tagged.append({"token": token, "upos": "SCONJ", "stts": "KOUS", "lemma": lower})
            continue
            
        # Prepositions
        if lower in PREPOSITIONS:
            tagged.append({"token": token, "upos": "ADP", "stts": "APPR", "lemma": lower})
            continue
            
        # Determiners
        if lower in ARTICLES or lower in DEMONSTRATIVES:
            tagged.append({"token": token, "upos": "DET", "stts": "ART", "lemma": lower})
            continue
            
        # Pronouns
        if token in {"Sie", "Ihnen", "Ihr", "Ihre", "Ihrem", "Ihren", "Ihres"}:
            tagged.append({"token": token, "upos": "PRON", "stts": "PPER", "lemma": "Sie", "polite": True})
            continue
        if lower in PRONOUNS_PERSONAL:
            tagged.append({"token": token, "upos": "PRON", "stts": "PPER", "lemma": lower})
            continue
        if lower in PRONOUNS_POSSESSIVE:
            tagged.append({"token": token, "upos": "DET", "stts": "PPOSAT", "lemma": lower})
            continue
            
        # Auxiliaries & Modals
        if lower in AUXILIARIES:
            tagged.append({"token": token, "upos": "AUX", "stts": "VAFIN", "lemma": lower})
            continue
        if lower in MODAL_VERBS:
            tagged.append({"token": token, "upos": "AUX", "stts": "VMFIN", "lemma": lower})
            continue
            
        # Adverbs
        if lower in ADVERBS:
            tagged.append({"token": token, "upos": "ADV", "stts": "ADV", "lemma": lower})
            continue
            
        # Substantive Nouns (Capitalized in German, except at sentence start where check is ambiguous)
        # Suffix clues for nouns: -ung, -heit, -keit, -schaft, -tion, -tät, -tum, -nis, -ling
        noun_suffixes = ("ung", "heit", "keit", "schaft", "tion", "tät", "tum", "nis", "ling", "mus")
        if token[0].isupper() and (i > 0 or lower.endswith(noun_suffixes) or not lower.endswith(("en", "st", "t", "te", "ten"))):
            tagged.append({"token": token, "upos": "NOUN", "stts": "NN", "lemma": token})
            continue
            
        # Adjectives (Common adjective endings: -ig, -lich, -isch, -bar, -sam, -haft, -los, -voll, -e, -er, -es, -en, -em)
        adj_suffixes = ("ig", "lich", "isch", "bar", "sam", "haft", "los", "voll", "wert")
        if any(lower.endswith(sfx) for sfx in adj_suffixes) or (i > 0 and tagged[-1]["upos"] in {"DET", "ADP"} and lower.endswith(("e", "er", "es", "en", "em"))):
            tagged.append({"token": token, "upos": "ADJ", "stts": "ADJA", "lemma": lower})
            continue
            
        # Verbs (typical verbal endings: -en, -et, -est, -te, -ten, -tet, or ge-...-t / ge-...-en)
        if lower.endswith(("en", "eln", "ern", "est", "te", "ten", "tet")) or lower.startswith("ge") and lower.endswith(("t", "en")):
            tagged.append({"token": token, "upos": "VERB", "stts": "VVFIN", "lemma": lower})
            continue
            
        # Default fallback
        tagged.append({"token": token, "upos": "NOUN" if token[0].isupper() else "ADV", "stts": "NN" if token[0].isupper() else "ADV", "lemma": lower})

    return tagged
