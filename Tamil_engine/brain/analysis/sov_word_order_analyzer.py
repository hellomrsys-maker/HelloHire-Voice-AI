"""
Tamil SOV Word Order Cognitive Analyzer.
Audits clause syntax for canonical head-final SOV structure and postpositions.
"""

from typing import Dict, List
from Tamil_engine.brain.skills.pos_tagging import tag_pos
from Tamil_engine.brain.skills.tokenization import tokenize_tamil

class SovWordOrderAnalyzer:
    """
    Validates that Tamil clauses adhere to head-final SOV topology.
    """
    def __init__(self):
        self.name = "Tamil SOV Word Order Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        tokens = tokenize_tamil(text.rstrip(".,!?"))
        if not tokens:
            return {
                "text": text,
                "is_sov": True,
                "has_finite_verb_at_end": True,
                "score": 1.0
            }
            
        tagged = tag_pos(tokens)
        
        # Check if the final word (or near end) is a finite verb or predicate
        last_word, last_pos = tagged[-1]
        has_final_verb = last_pos in {"VERB", "PART"} or any(p in {"VERB", "PART"} for _, p in tagged[-2:])
        
        # Check for presence of subject, object, verb
        has_subject = any(pos in {"NOUN", "PRON"} for _, pos in tagged[:-1])
        has_verb = any(pos == "VERB" for _, pos in tagged)
        
        is_sov = has_final_verb and has_verb
        score = 1.0 if is_sov else (0.8 if has_verb else 0.5)
        
        return {
            "text": text,
            "tokens": tokens,
            "tagged": tagged,
            "is_sov": is_sov,
            "has_final_verb": has_final_verb,
            "score": score
        }
