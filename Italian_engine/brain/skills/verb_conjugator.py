"""
Italian Engine — Verb Conjugator Skill
Inflects regular (-are, -ere, -ire, -isc-) and irregular verbs across tenses and moods.
"""

import json
import os
from typing import Dict, Any, Optional

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
VERBS_FILE = os.path.join(RULES_DIR, "verb_conjugation_matrix.json")

def load_verb_matrix() -> Dict[str, Any]:
    if os.path.exists(VERBS_FILE):
        with open(VERBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

PERSON_MAP = {
    "1sg": 0, "io": 0,
    "2sg": 1, "tu": 1,
    "3sg": 2, "lui": 2, "lei": 2, "Lei": 2,
    "1pl": 3, "noi": 3,
    "2pl": 4, "voi": 4,
    "3pl": 5, "loro": 5, "Loro": 5
}

def conjugate_verb(lemma: str, tense: str = "presente", person: str = "1sg") -> str:
    """
    Conjugate an Italian verb by lemma, tense, and grammatical person.
    Example: conjugate_verb('andare', 'presente', '1sg') -> 'vado'
             conjugate_verb('parlare', 'futuro', '3sg') -> 'parlerà'
    """
    lemma_clean = lemma.lower().strip()
    matrix = load_verb_matrix()
    p_idx = PERSON_MAP.get(person, 0)
    
    # 1. Check irregulars
    irregs = matrix.get("irregular_verbs", {})
    if lemma_clean in irregs:
        irreg = irregs[lemma_clean]
        if tense in irreg:
            forms = irreg[tense]
            if isinstance(forms, list) and p_idx < len(forms):
                return forms[p_idx]
            elif isinstance(forms, str):
                return forms
        elif tense == "participio_passato":
            return irreg.get("participio_passato", f"{lemma_clean[:-3]}ato")
        elif tense == "gerundio":
            return irreg.get("gerundio", f"{lemma_clean[:-3]}ando")

    # 2. Regular inflection
    if lemma_clean.endswith("are"):
        stem = lemma_clean[:-3]
        model = matrix.get("regular_models", {}).get("are", {})
    elif lemma_clean.endswith("ere"):
        stem = lemma_clean[:-3]
        model = matrix.get("regular_models", {}).get("ere", {})
    elif lemma_clean.endswith("ire"):
        stem = lemma_clean[:-3]
        model = matrix.get("regular_models", {}).get("ire", {})
    else:
        return lemma_clean
        
    if tense in model:
        forms = model[tense]
        if isinstance(forms, list) and p_idx < len(forms):
            return stem + forms[p_idx]
        elif isinstance(forms, str):
            return stem + forms
            
    if tense == "participio_passato":
        return stem + model.get("participio_passato", "ato")
    if tense == "gerundio":
        return stem + model.get("gerundio", "ando")
        
    return lemma_clean
