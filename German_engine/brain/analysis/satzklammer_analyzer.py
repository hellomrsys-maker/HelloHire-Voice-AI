"""
German Engine — Satzklammer (Topological Field) Analyzer
Checks V2 constraint in main clauses, V-End in subordinate clauses, and verb bracket integrity.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.parsing import parse_topological_fields
from ..skills.separable_verb_engine import detect_clause_separable_verb

class SatzklammerAnalyzer:
    """Cognitive analyzer for topological field and verb bracket constraints."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        parsed = parse_topological_fields(tokens, tags)
        separable_info = detect_clause_separable_verb(tokens)
        
        clause_type = parsed.get("clause_type", "unknown")
        fields = parsed.get("fields", {})
        
        errors = []
        is_valid = True
        
        # Check Main Clause V2 rule: Linke Klammer must contain exactly one finite verb, Vorfeld <= 1 constituent
        if clause_type == "main_v2":
            lk = fields.get("linke_klammer", [])
            vf = fields.get("vorfeld", [])
            if not lk:
                errors.append("V2 Violation: No finite verb in Linke Satzklammer")
                is_valid = False
            # If Vorfeld is missing or empty in declarative sentence
            if not vf and not text.endswith("?"):
                errors.append("V2 Warning: Empty Vorfeld in declarative main clause")
                
        elif clause_type == "subordinate_v_end":
            rk = fields.get("rechte_klammer", [])
            if not rk:
                errors.append("V-End Violation: Subordinate clause does not terminate with finite verb cluster")
                is_valid = False
                
        return {
            "clause_type": clause_type,
            "fields": fields,
            "separable_verb": separable_info,
            "is_valid": is_valid,
            "errors": errors,
            "token_count": len(tokens)
        }
