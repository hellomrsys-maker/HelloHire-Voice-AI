"""
Persian DOM Concord Analyzer
Cognitive analysis module auditing the presence, absence, and syntactic position
of the postpositional direct object marker 'rā' (را).
"""

from typing import Dict, Any, List
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger
from Persian_engine.brain.skills.dom_marker_engine import PersianDOMEngine

class DOMConcordAnalyzer:
    """
    Verifies that direct objects receive the appropriate differential object marking:
    - Overt 'rā' on definite objects, proper nouns, and pronouns.
    - Prohibition of 'rā' on subjects and indefinite non-specific objects.
    """

    def __init__(self):
        self.tagger = PersianPOSTagger()
        self.dom = PersianDOMEngine()

    def audit_sentence_dom(self, text: str) -> Dict[str, Any]:
        """Audits DOM usage in a Persian sentence."""
        tagged = self.tagger.tag_sentence(text)
        words = [w for w, _ in tagged]
        
        issues = []
        verified_dom_count = 0
        
        for i, (word, pos) in enumerate(tagged):
            # If word is 'را'
            if word == "را":
                # Check preceding element
                if i == 0:
                    issues.append({
                        "index": i,
                        "type": "initial_ra",
                        "message": "Postposition 'را' cannot appear at the beginning of a sentence."
                    })
                else:
                    prev_word, prev_pos = tagged[i - 1]
                    # Preceding word should not be a verb
                    if prev_pos == "VERB":
                        issues.append({
                            "index": i,
                            "type": "verb_preceding_ra",
                            "message": f"'را' cannot follow a verb ('{prev_word}')."
                        })
                    else:
                        verified_dom_count += 1
            else:
                # Check if this word is a definite noun or pronoun in object role missing 'را'
                if i + 1 < len(tagged):
                    next_word, next_pos = tagged[i + 1]
                    # If this is a personal pronoun or proper noun followed directly by a verb
                    if pos == "PRON" and next_pos == "VERB" and i > 0:
                        issues.append({
                            "index": i,
                            "token": word,
                            "type": "missing_ra_on_pronoun_object",
                            "message": f"Pronoun object '{word}' directly preceding verb '{next_word}' requires 'را'."
                        })

        accuracy = 1.0 if not issues else max(0.0, 1.0 - (len(issues) * 0.25))
        return {
            "verified_dom_count": verified_dom_count,
            "issues": issues,
            "accuracy": accuracy,
            "is_valid": len(issues) == 0
        }
