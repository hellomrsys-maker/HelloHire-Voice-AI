"""
Tamil Grammar Checking Task Pipeline.
Proofreads Tamil text for SOV order, 8-case agglutination, PNG agreement, and sandhi.
"""

from typing import Dict, List
from Tamil_engine.brain.analysis.sov_word_order_analyzer import SovWordOrderAnalyzer
from Tamil_engine.brain.analysis.case_png_analyzer import CasePngAnalyzer
from Tamil_engine.brain.analysis.sandhi_analyzer import SandhiAnalyzer

class TamilGrammarChecker:
    """
    Automated proofreading pipeline for Tamil sentences.
    """
    def __init__(self):
        self.sov_analyzer = SovWordOrderAnalyzer()
        self.case_png_analyzer = CasePngAnalyzer()
        self.sandhi_analyzer = SandhiAnalyzer()

    def check(self, text: str) -> Dict[str, any]:
        sov_res = self.sov_analyzer.analyze(text)
        cp_res = self.case_png_analyzer.analyze(text)
        sandhi_res = self.sandhi_analyzer.analyze(text)
        
        errors = []
        if not cp_res["is_grammatically_sound"] and cp_res["png_concord"]["error"]:
            errors.append(cp_res["png_concord"]["error"])
        if not sandhi_res["is_sandhi_valid"]:
            errors.extend(sandhi_res["violations"])
            
        overall_score = (sov_res["score"] + cp_res["score"] + sandhi_res["sandhi_score"]) / 3.0
        
        return {
            "input_text": text,
            "is_grammatically_sound": len(errors) == 0,
            "overall_score": round(overall_score, 4),
            "errors": errors,
            "corrected_text": sandhi_res["corrected_text"],
            "cases_detected": [c["case_name"] for c in cp_res["cases_found"]]
        }
