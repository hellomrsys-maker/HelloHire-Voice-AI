"""
Arabic Engine — VSO / SVO Agreement Analyzer
Audits verb-subject concordial agreement across Classical VSO and SVO word orders.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.concord_agreement_engine import validate_vso_agreement, validate_svo_agreement

class VsoSvoAgreementAnalyzer:
    """Cognitive analyzer for Arabic verbal vs nominal clausal concord."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        # Filter content words
        content_tags = [t for t in tags if t["upos"] in {"VERB", "NOUN", "PROPN", "PRON"}]
        
        violations = []
        clause_order = "unknown"
        
        if len(content_tags) >= 2:
            first = content_tags[0]
            second = content_tags[1]
            
            if first["upos"] == "VERB" and second["upos"] in {"NOUN", "PROPN", "PRON"}:
                clause_order = "VSO"
                v_res = validate_vso_agreement(first["token"], second["token"])
                if not v_res["valid"]:
                    violations.append(v_res)
                    
            elif first["upos"] in {"NOUN", "PROPN", "PRON"} and second["upos"] == "VERB":
                clause_order = "SVO"
                s_res = validate_svo_agreement(first["token"], second["token"])
                if not s_res["valid"]:
                    violations.append(s_res)
                    
        return {
            "text": text,
            "clause_order": clause_order,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
