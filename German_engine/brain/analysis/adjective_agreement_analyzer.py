"""
German Engine — Adjective Agreement Analyzer
Validates concord between Determiners, Adjectives, and Nouns in noun phrases.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.adjective_declension_engine import (
    determine_declension_type,
    DECLENSION_TABLE
)

# Common German noun genders for sample/benchmark validation
NOUN_GENDER_CACHE = {
    "Mann": "masculine", "Vater": "masculine", "Hund": "masculine", "Tisch": "masculine", "Wagen": "masculine", "Zug": "masculine",
    "Frau": "feminine", "Mutter": "feminine", "Katze": "feminine", "Stadt": "feminine", "Schule": "feminine", "Arbeit": "feminine",
    "Kind": "neuter", "Haus": "neuter", "Buch": "neuter", "Auto": "neuter", "Bier": "neuter", "Zimmer": "neuter",
    "Kinder": "plural", "Leute": "plural", "Freunde": "plural", "Bücher": "plural", "Hunde": "plural"
}

class AdjectiveAgreementAnalyzer:
    """Cognitive analyzer for German adjective inflection concord."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        phrases_checked = []
        violations = []
        
        for i in range(len(tags)):
            # Pattern 1: DET + ADJ + NOUN
            if i + 2 < len(tags) and tags[i]["upos"] == "DET" and tags[i+1]["upos"] == "ADJ" and tags[i+2]["upos"] == "NOUN":
                det = tags[i]["token"]
                adj = tags[i+1]["token"]
                noun = tags[i+2]["token"]
                
                gender = NOUN_GENDER_CACHE.get(noun, "masculine") # Default heuristic
                decl_type = determine_declension_type(det)
                
                # Check masculine accusative marker: den / einen -> adjective must end in -en
                if det.lower() in {"den", "einen", "meinen", "deinen", "seinen", "keinen"} and gender == "masculine":
                    valid = adj.lower().endswith("en")
                    if not valid:
                        violations.append({
                            "phrase": f"{det} {adj} {noun}",
                            "det": det, "adj": adj, "noun": noun,
                            "expected_ending": "en",
                            "message": f"Masculine accusative requires '-en' on adjective after '{det}', found '{adj}'"
                        })
                elif det.lower() in {"der"} and gender == "masculine":
                    # Nominative masculine weak declension -> -e
                    valid = adj.lower().endswith("e")
                    if not valid:
                        violations.append({
                            "phrase": f"{det} {adj} {noun}",
                            "det": det, "adj": adj, "noun": noun,
                            "expected_ending": "e",
                            "message": f"Masculine nominative weak declension requires '-e' on adjective after 'der', found '{adj}'"
                        })
                elif det.lower() in {"ein"} and gender == "masculine":
                    # Nominative masculine mixed declension -> -er
                    valid = adj.lower().endswith("er")
                    if not valid:
                        violations.append({
                            "phrase": f"{det} {adj} {noun}",
                            "det": det, "adj": adj, "noun": noun,
                            "expected_ending": "er",
                            "message": f"Masculine nominative mixed declension requires '-er' on adjective after 'ein', found '{adj}'"
                        })
                else:
                    valid = True
                    
                phrases_checked.append({
                    "phrase": f"{det} {adj} {noun}",
                    "declension_type": decl_type,
                    "valid": valid
                })
                
            # Pattern 2: Strong declension ADJ + NOUN (no determiner)
            elif i + 1 < len(tags) and tags[i]["upos"] == "ADJ" and tags[i+1]["upos"] == "NOUN" and (i == 0 or tags[i-1]["upos"] not in {"DET", "ADP"}):
                adj = tags[i]["token"]
                noun = tags[i+1]["token"]
                gender = NOUN_GENDER_CACHE.get(noun, "masculine")
                # Strong declension must carry distinctive ending (-er, -e, -es)
                valid = adj.lower().endswith(("er", "e", "es", "em", "en"))
                phrases_checked.append({
                    "phrase": f"{adj} {noun}",
                    "declension_type": "strong",
                    "valid": valid
                })
                
        return {
            "phrase_count": len(phrases_checked),
            "phrases_checked": phrases_checked,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
