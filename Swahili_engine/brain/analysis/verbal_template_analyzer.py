"""
Swahili Engine — Verbal Template Analyzer
Audits Swahili agglutinative verb structure, TAM compatibility, and monosyllabic ku- retention.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.verbal_template_engine import parse_verb_structure
from ..skills.monosyllabic_verb_engine import is_monosyllabic_verb

class VerbalTemplateAnalyzer:
    """Cognitive analyzer for Swahili finite verbal agglutination chains."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        parsed_verbs = []
        violations = []
        
        for t in tags:
            if t["upos"] == "VERB":
                v_str = t["token"]
                res = parse_verb_structure(v_str)
                parsed_verbs.append(res)
                
                # Check monosyllabic verb constraint
                # If verb is affirmative, lacks OP, has monosyllabic root (e.g. -la), but omitted ku- (e.g. *anala)
                v_lower = v_str.lower()
                for root in ["la", "nywa", "ja", "fa"]:
                    if v_lower.endswith(root) and not res["negative"] and not res.get("monosyllabic_ku") and not any(op in v_lower for op in ["ki", "vi", "m", "wa"]):
                        if any(v_lower.startswith(sp + tam + root) for sp in ["a", "wa", "ni", "u", "tu"] for tam in ["na", "li", "ta", "me"]):
                            violations.append({
                                "verb": v_str,
                                "error": f"Monosyllabic verb stem '-{root}' must retain dummy 'ku-' in affirmative tense"
                            })
                            
        return {
            "verb_count": len(parsed_verbs),
            "parsed_verbs": parsed_verbs,
            "violations": violations,
            "is_valid": len(violations) == 0
        }
