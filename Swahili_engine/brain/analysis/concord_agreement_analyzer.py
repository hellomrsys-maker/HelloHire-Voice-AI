"""
Swahili Engine — Concord Agreement Analyzer
Audits alliterative Bantu noun class agreement across noun phrases and sentential predicates.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.noun_class_engine import identify_noun_class
from ..skills.concord_engine import validate_concord

class ConcordAgreementAnalyzer:
    """Cognitive analyzer for Swahili concordial agreement (Upatanisho wa Kisarufi)."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        violations = []
        checked_modifiers = []
        
        current_noun = None
        current_class = None
        
        for i, tag in enumerate(tags):
            if tag["upos"] == "NOUN":
                current_noun = tag["token"]
                current_class = identify_noun_class(current_noun)
            elif tag["upos"] in {"DET", "ADJ", "PRON"} and current_noun:
                mod = tag["token"]
                mod_type = "demonstrative" if tag["upos"] == "DET" else "adjective"
                res = validate_concord(current_noun, mod, mod_type)
                checked_modifiers.append(res)
                if not res["valid"]:
                    violations.append({
                        "noun": current_noun,
                        "class": current_class,
                        "modifier": mod,
                        "type": mod_type,
                        "error": f"Modifier '{mod}' does not agree with Class {current_class} noun '{current_noun}'"
                    })
                    
        return {
            "token_count": len(tokens),
            "checked_count": len(checked_modifiers),
            "violations": violations,
            "is_valid": len(violations) == 0
        }
