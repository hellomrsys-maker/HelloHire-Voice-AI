"""
Thai Classifier Syntax Cognitive Analyzer.
Audits post-nominal classifier order and flags foreign pre-nominal calques.
"""

from typing import Dict, List
from Thai_engine.brain.skills.classifier_engine import audit_classifier_syntax
from Thai_engine.brain.skills.tokenization import tokenize_thai

class ClassifierSyntaxAnalyzer:
    """
    Evaluates numeral classifier placement in Thai sentences.
    """
    def __init__(self):
        self.name = "Thai Classifier Syntax Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        tokens = tokenize_thai(text)
        audit_res = audit_classifier_syntax(tokens)
        
        return {
            "text": text,
            "is_valid": audit_res["is_valid"],
            "violations": audit_res["violations"],
            "structures": audit_res["structures"],
            "classifier_score": 1.0 if audit_res["is_valid"] else 0.5
        }
