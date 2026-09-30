"""
Arabic Engine — Idafa Construct Analyzer
Audits Genitive Construct (الإضافة) state compliance, forbidden definite articles, and nunation errors.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.idafa_engine import validate_idafa

class IdafaConstructAnalyzer:
    """Cognitive analyzer for Arabic genitive constructs (Idafa)."""

    def __init__(self):
        pass

    @staticmethod
    def _is_definite(word: str) -> bool:
        w = word.strip().lower()
        if w.startswith("ال"):
            return True
        for pfx in ["al-", "ash-", "ath-", "adh-", "ar-", "az-", "as-", "at-", "ad-", "an-"]:
            if w.startswith(pfx):
                return True
        return False

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        violations = []
        constructs_found = []
        
        # Look for consecutive NOUN-NOUN sequences
        for i in range(len(tags) - 1):
            t1 = tags[i]
            t2 = tags[i + 1]
            if t1["upos"] in {"NOUN", "PROPN"} and t2["upos"] in {"NOUN", "PROPN"}:
                # If preceded by a VERB in a verbal clause, t1 is the Subject and t2 is the Direct Object
                if i > 0 and tags[i - 1]["upos"] == "VERB":
                    continue
                w1 = t1["token"]
                w2 = t2["token"]
                # If both terms are overtly marked with the definite article, this is not an Idafa construct
                if self._is_definite(w1) and self._is_definite(w2):
                    continue
                res = validate_idafa(w1, w2)
                constructs_found.append({"mudaf": w1, "mudaf_ilayh": w2, "valid": res["valid"]})
                if not res["valid"]:
                    violations.extend(res["violations"])
                    
        return {
            "text": text,
            "constructs_found": constructs_found,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
