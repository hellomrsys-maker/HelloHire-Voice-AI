"""
Vietnamese Classifier Concord Analyzer
Cognitive analysis module auditing numeral classifier selection and missing classifiers.
"""

from typing import Dict, Any, List
from Vietnamese_engine.brain.skills.pos_tagging import VietnamesePOSTagger
from Vietnamese_engine.brain.skills.classifier_engine import VietnameseClassifierEngine, NOUN_CLASSIFIER_MAP

class ClassifierConcordAnalyzer:
    """
    Audits noun phrases to detect:
    - Missing classifiers when numerals precede countable nouns (e.g. 'hai sách' -> 'hai cuốn sách')
    - Semantic mismatches between classifier and noun (e.g. 'cái chó' -> 'con chó')
    """

    def __init__(self):
        self.tagger = VietnamesePOSTagger()
        self.clf_engine = VietnameseClassifierEngine()

    def audit_classifier_usage(self, text: str) -> Dict[str, Any]:
        """Audits classifier concordance across the text."""
        tagged = self.tagger.tag_sentence(text)
        issues = []
        valid_pairs = 0
        
        for i in range(len(tagged)):
            word, pos = tagged[i]
            
            # Check pattern: NUM + NOUN without intervening CLF
            if pos == "NUM" and i + 1 < len(tagged):
                next_w, next_p = tagged[i + 1]
                if next_p == "NOUN":
                    # Check if this noun normally demands a classifier
                    clean_n = next_w.lower().strip()
                    if clean_n in NOUN_CLASSIFIER_MAP:
                        pref_clf = NOUN_CLASSIFIER_MAP[clean_n]
                        issues.append({
                            "type": "missing_classifier",
                            "numeral": word,
                            "noun": next_w,
                            "suggested_classifier": pref_clf,
                            "suggestion": f"{word} {pref_clf} {next_w}",
                            "message": f"Countable noun '{next_w}' preceded by numeral '{word}' requires classifier '{pref_clf}'."
                        })
                elif next_p == "CLF" and i + 2 < len(tagged):
                    noun_w, noun_p = tagged[i + 2]
                    # Validate classifier-noun pairing
                    if not self.clf_engine.validate_classifier_noun_pair(next_w, noun_w):
                        issues.append({
                            "type": "classifier_mismatch",
                            "classifier": next_w,
                            "noun": noun_w,
                            "message": f"Classifier '{next_w}' is semantically incompatible with noun '{noun_w}'."
                        })
                    else:
                        valid_pairs += 1

        accuracy = 1.0 if not issues else max(0.0, 1.0 - (len(issues) * 0.2))
        return {
            "total_classifier_pairs": valid_pairs,
            "issues": issues,
            "accuracy": round(accuracy, 2),
            "is_valid": len(issues) == 0
        }
