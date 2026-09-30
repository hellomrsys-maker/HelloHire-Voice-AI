"""
Indonesian Engine — Classifier Concord Analyzer
Audits semantic category agreement between numeral classifiers (orang/ekor/buah/lembar/batang) and head nouns.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.classifier_engine import validate_classifier_phrase

CLASSIFIER_SET = {"orang", "ekor", "buah", "lembar", "batang", "butir", "pucuk", "bilah"}

class ClassifierConcordAnalyzer:
    """Cognitive analyzer for Indonesian numeral classifier semantic agreement."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        violations = []
        checked_phrases = []
        
        # Scan for [NUMBER/se-] + [CLASSIFIER] + [NOUN] patterns
        # Case 1: Prefixed classifier e.g. "seorang", "seekor", "sebuah", "selembar"
        for i in range(len(tokens) - 1):
            w1 = tokens[i].lower()
            w2 = tokens[i + 1].lower()
            
            if w1.startswith("se") and len(w1) > 2:
                clf_cand = w1[2:]
                if clf_cand in CLASSIFIER_SET:
                    res = validate_classifier_phrase(clf_cand, w2)
                    checked_phrases.append({"classifier": clf_cand, "noun": w2, "valid": res["valid"]})
                    if not res["valid"]:
                        violations.extend(res["violations"])
                        
            # Case 2: Separate number + classifier + noun (e.g. "dua ekor kucing", "tiga orang guru")
            if i < len(tokens) - 2:
                w_clf = tokens[i + 1].lower()
                w_noun = tokens[i + 2].lower()
                if w_clf in CLASSIFIER_SET and w1 in {"dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "banyak", "beberapa"}:
                    res = validate_classifier_phrase(w_clf, w_noun)
                    checked_phrases.append({"number": w1, "classifier": w_clf, "noun": w_noun, "valid": res["valid"]})
                    if not res["valid"]:
                        violations.extend(res["violations"])
                        
        return {
            "text": text,
            "checked_phrases": checked_phrases,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
