"""
Italian Engine — Auxiliary Selector & Agreement Skill
Disambiguates 'essere' vs 'avere' selection and computes past participle gender/number concord.
"""

import json
import os
from typing import Dict, Any, Tuple

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
VERBS_FILE = os.path.join(RULES_DIR, "verb_conjugation_matrix.json")

def load_verb_matrix() -> Dict[str, Any]:
    if os.path.exists(VERBS_FILE):
        with open(VERBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def select_auxiliary(verb_lemma: str, is_reflexive: bool = False, is_passive: bool = False) -> str:
    """
    Select appropriate auxiliary ('essere' vs 'avere') for an Italian verb.
    - Reflexive and passive obligatorily take 'essere'.
    - Unaccusative verbs of motion and state change take 'essere'.
    - Transitive and unergative verbs take 'avere'.
    """
    if is_reflexive or is_passive:
        return "essere"
        
    v_clean = verb_lemma.lower().strip()
    matrix = load_verb_matrix()
    
    # Check explicitly defined auxiliary in irregular verbs
    irregs = matrix.get("irregular_verbs", {})
    if v_clean in irregs and "auxiliary" in irregs[v_clean]:
        return irregs[v_clean]["auxiliary"]
        
    essere_verbs = set(matrix.get("auxiliary_classification", {}).get("essere", []))
    if v_clean in essere_verbs:
        return "essere"
        
    return "avere"

def compute_participle_concord(
    participle_base: str,
    auxiliary: str,
    subject_gender: str = "m",
    subject_number: str = "sg",
    preceding_clitic_gender: str = None,
    preceding_clitic_number: str = None
) -> str:
    """
    Compute agreed past participle ending:
    - With 'essere': agrees with Subject (m/f, sg/pl).
    - With 'avere': invariable (-o) unless preceding direct object clitic (lo, la, li, le).
    """
    stem = participle_base[:-1] if participle_base.endswith(("o", "a", "i", "e")) else participle_base
    
    # Preceding direct object clitic overrides avere invariability
    if auxiliary == "avere" and preceding_clitic_gender:
        target_g = preceding_clitic_gender.lower()
        target_n = preceding_clitic_number.lower() if preceding_clitic_number else "sg"
    elif auxiliary == "essere":
        target_g = subject_gender.lower()
        target_n = subject_number.lower()
    else:
        # Standard avere: default masculine singular -o
        return stem + "o"
        
    if target_g == "f" and target_n == "sg":
        return stem + "a"
    elif target_g == "f" and target_n in {"pl", "p"}:
        return stem + "e"
    elif target_g == "m" and target_n in {"pl", "p"}:
        return stem + "i"
    else:
        return stem + "o"

def validate_passato_prossimo(
    auxiliary_used: str,
    participle_used: str,
    verb_lemma: str,
    subject_gender: str = "m",
    subject_number: str = "sg"
) -> Dict[str, Any]:
    """Audit correctness of a Passato Prossimo construction."""
    correct_aux = select_auxiliary(verb_lemma)
    violations = []
    
    aux_clean = auxiliary_used.lower().strip()
    # Check auxiliary lemma
    is_essere_form = aux_clean in {"sono", "sei", "è", "siamo", "siete", "era", "eri", "stato"}
    is_avere_form = aux_clean in {"ho", "hai", "ha", "abbiamo", "avete", "hanno", "avevo", "avuto"}
    
    if correct_aux == "essere" and not is_essere_form:
        violations.append({
            "rule": "auxiliary_choice",
            "error": f"Verb '{verb_lemma}' requires auxiliary 'essere', but '{auxiliary_used}' was used."
        })
    elif correct_aux == "avere" and not is_avere_form:
        violations.append({
            "rule": "auxiliary_choice",
            "error": f"Verb '{verb_lemma}' requires auxiliary 'avere', but '{auxiliary_used}' was used."
        })
        
    # Check participle concord if auxiliary is essere
    if correct_aux == "essere":
        expected_participle = compute_participle_concord(participle_used, "essere", subject_gender, subject_number)
        if participle_used.lower() != expected_participle:
            violations.append({
                "rule": "participle_concord",
                "error": f"With 'essere', participle must agree with subject ({subject_gender}/{subject_number}): expected '{expected_participle}', got '{participle_used}'."
            })
            
    return {
        "valid": len(violations) == 0,
        "correct_auxiliary": correct_aux,
        "violations": violations
    }
