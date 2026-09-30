"""
Cantonese Double Object Construction (DOC) Cognitive Analyzer.
Audits clauses for natural Cantonese ditransitive structure V + DO + IO vs Mandarin calques,
postverbal adverb placement, and comparative structures.
"""

from typing import Dict, List
from Cantonese_engine.brain.skills.doc_inversion_engine import (
    analyze_doc_structure,
    analyze_postverbal_adverb,
    invert_to_canonical_cantonese
)

class DocInversionAnalyzer:
    """
    Analyzes and validates Cantonese ditransitive alignment and word order constraints.
    """
    def __init__(self):
        self.doc_name = "Cantonese DOC Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        doc_eval = analyze_doc_structure(text)
        adv_eval = analyze_postverbal_adverb(text)
        
        is_fully_canonical = doc_eval["is_canonical"] and adv_eval["is_canonical"]
        violations = []
        if doc_eval["rule_violation"]:
            violations.append(doc_eval["rule_violation"])
        if adv_eval["rule_violation"]:
            violations.append(adv_eval["rule_violation"])
            
        suggested = invert_to_canonical_cantonese(text)
        
        return {
            "text": text,
            "is_canonical": is_fully_canonical,
            "doc_structure": doc_eval["detected_order"],
            "adverb_structure": adv_eval["detected_order"],
            "violations": violations,
            "normalized_canonical_text": suggested,
            "accuracy_score": 1.0 if is_fully_canonical else 0.5
        }
