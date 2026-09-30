"""
Tamil Sandhi Cognitive Analyzer.
Audits external sandhi and plosive doubling between words.
"""

from typing import Dict
from Tamil_engine.brain.skills.sandhi_engine import audit_sandhi, apply_sandhi

class SandhiAnalyzer:
    """
    Evaluates Tamil text for euphonic sandhi rules.
    """
    def __init__(self):
        self.name = "Tamil Sandhi Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        audit_res = audit_sandhi(text)
        corrected_text = apply_sandhi(text)
        
        return {
            "text": text,
            "is_sandhi_valid": audit_res["is_sandhi_valid"],
            "violations": audit_res["violations"],
            "corrected_text": corrected_text,
            "sandhi_score": 1.0 if audit_res["is_sandhi_valid"] else 0.7
        }
