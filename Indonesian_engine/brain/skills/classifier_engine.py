"""
Indonesian Engine — Numeral Classifier Engine Skill
Validates and synthesizes Indonesian numeral classifier phrases:
[Number] + [Classifier] + [Noun] (e.g. seorang guru, dua ekor kucing, tiga buah buku)
"""

import json
import os
from typing import Dict, Any, List, Optional

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")
CLASSIFIER_FILE = os.path.join(RULES_DIR, "classifier_matrix.json")

def load_classifier_matrix() -> Dict[str, Any]:
    if os.path.exists(CLASSIFIER_FILE):
        with open(CLASSIFIER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def select_classifier(noun: str) -> str:
    """Select appropriate classifier for a noun."""
    n = noun.lower().strip()
    matrix = load_classifier_matrix()
    classifiers = matrix.get("classifiers", {})
    
    for clf_name, data in classifiers.items():
        if n in data.get("valid_nouns", []):
            return clf_name
            
    # Heuristic fallback
    if n in {"guru", "anak", "dokter", "siswa", "presiden", "teman", "orang"}:
        return "orang"
    elif n in {"kucing", "anjing", "burung", "ikan", "ayam", "kuda", "sapi"}:
        return "ekor"
    elif n in {"kertas", "kain", "surat", "foto"}:
        return "lembar"
    elif n in {"pohon", "pensil", "rokok"}:
        return "batang"
    return "buah"

def format_numeral_classifier(number: str, noun: str, classifier: Optional[str] = None) -> str:
    """
    Synthesize numeral classifier phrase:
    Example: format_numeral_classifier('satu', 'guru') -> 'seorang guru'
             format_numeral_classifier('dua', 'kucing') -> 'dua ekor kucing'
             format_numeral_classifier('tiga', 'buku') -> 'tiga buah buku'
    """
    clf = classifier if classifier else select_classifier(noun)
    num_clean = number.lower().strip()
    
    if num_clean in {"satu", "1", "se"}:
        return f"se{clf} {noun}"
    return f"{number} {clf} {noun}"

def validate_classifier_phrase(classifier_used: str, noun: str) -> Dict[str, Any]:
    """Validate whether classifier matches noun semantic category."""
    expected = select_classifier(noun)
    actual = classifier_used.lower().strip()
    # Strip any leading 'se' prefix (e.g. seorang -> orang)
    if actual.startswith("se") and len(actual) > 2:
        actual = actual[2:]
        
    is_valid = actual == expected
    violations = []
    if not is_valid:
        violations.append({
            "noun": noun,
            "used_classifier": classifier_used,
            "expected_classifier": expected,
            "rule": "classifier_semantic_clash",
            "error": f"Noun '{noun}' requires classifier '{expected}', but '{classifier_used}' was used."
        })
        
    return {
        "valid": is_valid,
        "noun": noun,
        "classifier": actual,
        "expected": expected,
        "violations": violations
    }
