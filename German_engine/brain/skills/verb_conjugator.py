"""
German Engine — Verb Conjugation Skill
Conjugates weak, strong, modal, and auxiliary verbs across person, number, tense, and mood.
"""

from typing import Dict, Any, Optional

PRONOUN_PERSON_MAP = {
    "ich": ("1", "sg"),
    "du": ("2", "sg"),
    "er": ("3", "sg"),
    "sie": ("3", "sg"),
    "es": ("3", "sg"),
    "wir": ("1", "pl"),
    "ihr": ("2", "pl"),
    "Sie": ("3", "pl") # Polite
}

AUXILIARIES = {
    "sein": {
        "present": {"ich": "bin", "du": "bist", "er": "ist", "sie": "ist", "es": "ist", "wir": "sind", "ihr": "seid", "Sie": "sind"},
        "preterite": {"ich": "war", "du": "warst", "er": "war", "sie": "war", "es": "war", "wir": "waren", "ihr": "wart", "Sie": "waren"},
        "participle_ii": "gewesen",
        "perf_aux": "sein"
    },
    "haben": {
        "present": {"ich": "habe", "du": "hast", "er": "hat", "sie": "hat", "es": "hat", "wir": "haben", "ihr": "habt", "Sie": "haben"},
        "preterite": {"ich": "hatte", "du": "hattest", "er": "hatte", "sie": "hatte", "es": "hatte", "wir": "hatten", "ihr": "hattet", "Sie": "hatten"},
        "participle_ii": "gehabt",
        "perf_aux": "haben"
    },
    "werden": {
        "present": {"ich": "werde", "du": "wirst", "er": "wird", "sie": "wird", "es": "wird", "wir": "werden", "ihr": "werdet", "Sie": "werden"},
        "preterite": {"ich": "wurde", "du": "wurdest", "er": "wurde", "sie": "wurde", "es": "wurde", "wir": "wurden", "ihr": "wurdet", "Sie": "wurden"},
        "participle_ii": "geworden",
        "perf_aux": "sein"
    }
}

MODALS = {
    "können": {"ich": "kann", "du": "kannst", "er": "kann", "wir": "können", "ihr": "könnt", "Sie": "können"},
    "müssen": {"ich": "muss", "du": "musst", "er": "muss", "wir": "müssen", "ihr": "müsst", "Sie": "müssen"},
    "dürfen": {"ich": "darf", "du": "darfst", "er": "darf", "wir": "dürfen", "ihr": "dürft", "Sie": "dürfen"},
    "sollen": {"ich": "soll", "du": "sollst", "er": "soll", "wir": "sollen", "ihr": "sollt", "Sie": "sollen"},
    "wollen": {"ich": "will", "du": "willst", "er": "will", "wir": "wollen", "ihr": "wollt", "Sie": "wollen"},
    "mögen":  {"ich": "mag", "du": "magst", "er": "mag", "wir": "mögen", "ihr": "mögt", "Sie": "mögen"}
}

STRONG_VERB_VOWEL_CHANGES = {
    "geben": {"du": "gibst", "er": "gibt"},
    "sehen": {"du": "siehst", "er": "sieht"},
    "lesen": {"du": "liest", "er": "liest"},
    "sprechen": {"du": "sprichst", "er": "spricht"},
    "fahren": {"du": "fährst", "er": "fährt"},
    "schlafen": {"du": "schläfst", "er": "schläft"},
    "laufen": {"du": "läufst", "er": "läuft"},
    "tragen": {"du": "trägst", "er": "trägt"}
}

def conjugate_present(infinitive: str, pronoun: str) -> str:
    """Conjugate verb in Präsens for a subject pronoun."""
    p = pronoun.strip()
    inf = infinitive.lower().strip()
    
    # Check Auxiliaries
    if inf in AUXILIARIES:
        return AUXILIARIES[inf]["present"].get(p, AUXILIARIES[inf]["present"]["er"])
        
    # Check Modals
    if inf in MODALS:
        return MODALS[inf].get(p, MODALS[inf]["er"])
        
    # Check Strong verb 2nd/3rd person singular vowel change
    if inf in STRONG_VERB_VOWEL_CHANGES and p in {"du", "er", "sie", "es"}:
        mapped_key = "du" if p == "du" else "er"
        return STRONG_VERB_VOWEL_CHANGES[inf][mapped_key]
        
    # Regular weak conjugation
    stem = inf[:-2] if inf.endswith("en") else (inf[:-1] if inf.endswith("n") else inf)
    
    # Dental stems take connecting e: arbeit- -> arbeitest, arbeitet
    dental = stem.endswith(("t", "d", "fn", "chn", "gn"))
    
    if p == "ich":
        return stem + "e"
    elif p == "du":
        return stem + ("est" if dental else "st")
    elif p in {"er", "sie", "es"}:
        return stem + ("et" if dental else "t")
    elif p == "wir":
        return stem + "en"
    elif p == "ihr":
        return stem + ("et" if dental else "t")
    elif p in {"Sie", "sie"}:
        return stem + "en"
        
    return stem + "t"

def form_participle_ii(infinitive: str) -> str:
    """Form Partizip II (e.g. machen -> gemacht, lernen -> gelernt)."""
    inf = infinitive.lower().strip()
    if inf in AUXILIARIES:
        return AUXILIARIES[inf]["participle_ii"]
        
    if inf.endswith("ieren"):
        # Verbs in -ieren do not take ge- prefix: studieren -> studiert
        return inf[:-2] + "t"
        
    stem = inf[:-2] if inf.endswith("en") else inf
    return "ge" + stem + ("et" if stem.endswith(("t", "d")) else "t")
