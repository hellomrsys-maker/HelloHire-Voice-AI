"""
Italian Engine — Clitic Engine Skill
Combines indirect and direct clitic clusters and handles imperative/infinitive enclisis.
"""

import json
import os
from typing import Dict, Any, List

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
CLITICS_FILE = os.path.join(RULES_DIR, "clitic_cluster_matrix.json")

def load_clitic_matrix() -> Dict[str, Any]:
    if os.path.exists(CLITICS_FILE):
        with open(CLITICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def combine_clitics(indirect_or_first: str, direct_or_second: str) -> str:
    """
    Combine two clitics into an Italian double clitic cluster.
    Example: combine_clitics('mi', 'lo') -> 'me lo'
             combine_clitics('gli', 'lo') -> 'glielo'
             combine_clitics('le', 'lo') -> 'glielo'
             combine_clitics('ci', 'ne') -> 'ce ne'
    """
    c1 = indirect_or_first.lower().strip()
    c2 = direct_or_second.lower().strip()
    
    matrix = load_clitic_matrix()
    clusters = matrix.get("combined_clusters", {})
    key = f"{c1}_{c2}"
    if key in clusters:
        return clusters[key]
        
    # Standard rule: -i -> -e before lo/la/li/le/ne
    if c1 in {"mi", "ti", "ci", "vi", "si"} and c2 in {"lo", "la", "li", "le", "ne"}:
        base = c1[:-1] + "e"
        return f"{base} {c2}"
    if c1 in {"gli", "le"} and c2 in {"lo", "la", "li", "le", "ne"}:
        return f"glie{c2}"
        
    return f"{c1} {c2}"

def attach_enclitic(verb_form: str, clitic: str, is_imperative_monosyllable: bool = False) -> str:
    """
    Attach an enclitic pronoun to a verb form:
    - Infinitive drops final -e: parlare + lo -> parlarlo
    - Monosyllabic imperative doubles initial consonant: fa + mi -> fammi, di + lo -> dillo
    """
    v = verb_form.lower().strip()
    c = clitic.lower().strip()
    matrix = load_clitic_matrix()
    
    # Check monosyllabic imperative doubling
    geminates = matrix.get("imperative_geminates", {})
    if v in geminates and c in geminates[v]:
        return geminates[v][c]
        
    # Infinitive truncation
    if v.endswith(("are", "ere", "ire")):
        return v[:-1] + c
    if v.endswith(("ar", "er", "ir")):
        return v + c
    if v.endswith(("ando", "endo")):
        return v + c
        
    return v + c
