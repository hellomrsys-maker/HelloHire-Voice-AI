"""
Arabic Engine — Deflected Agreement Analyzer
Audits the core Semitic rule: All non-human plurals require Feminine Singular concord.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.broken_plural_engine import analyze_plural
from ..skills.concord_agreement_engine import validate_noun_adjective_agreement

class DeflectedAgreementAnalyzer:
    """Cognitive analyzer for Arabic non-human plural deflected concord (جمع غير العاقل)."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        violations = []
        checked_pairs = []
        
        current_noun = None
        current_noun_info = None
        
        for i, tag in enumerate(tags):
            if tag["upos"] in {"NOUN", "PROPN"}:
                current_noun = tag["token"]
                current_noun_info = analyze_plural(current_noun)
            elif tag["upos"] in {"ADJ", "DET"} and current_noun:
                mod = tag["token"]
                res = validate_noun_adjective_agreement(current_noun, mod)
                checked_pairs.append({"noun": current_noun, "modifier": mod, "valid": res["valid"]})
                if not res["valid"]:
                    violations.append(res)
                    
        return {
            "text": text,
            "checked_pairs": checked_pairs,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
