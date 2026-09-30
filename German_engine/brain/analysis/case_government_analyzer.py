"""
German Engine — Case Government Analyzer
Validates prepositional and verbal case government throughout sentence tokens.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.case_engine import validate_prepositional_phrase, get_preposition_governed_case

class CaseGovernmentAnalyzer:
    """Cognitive analyzer for prepositional and verbal case government."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        preposition_checks = []
        violations = []
        
        for i, tag in enumerate(tags):
            if tag["upos"] == "ADP":
                prep = tag["token"].lower()
                governed = get_preposition_governed_case(prep)
                
                # Check following word if it's a determiner / article
                if i + 1 < len(tags):
                    next_tag = tags[i + 1]
                    if next_tag["upos"] in {"DET", "PRON"}:
                        article = next_tag["token"].lower()
                        result = validate_prepositional_phrase(prep, article)
                        preposition_checks.append(result)
                        if not result.get("valid", True):
                            violations.append({
                                "preposition": prep,
                                "article": article,
                                "governed_case": governed,
                                "message": f"Preposition '{prep}' governs {governed} case, but received '{article}'"
                            })
                            
        return {
            "preposition_count": len(preposition_checks),
            "preposition_checks": preposition_checks,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
