"""
Thai Grammar Checking Task Pipeline.
Proofreads Thai clauses for classifier word order, politeness particle concord,
and scriptio continua segmentability.
"""

from typing import Dict, List
from Thai_engine.brain.analysis.classifier_syntax_analyzer import ClassifierSyntaxAnalyzer
from Thai_engine.brain.analysis.politeness_concord_analyzer import PolitenessConcordAnalyzer
from Thai_engine.brain.analysis.tone_consistency_analyzer import ToneConsistencyAnalyzer

class ThaiGrammarChecker:
    """
    Automated proofreading pipeline for Thai text.
    """
    def __init__(self):
        self.clf_analyzer = ClassifierSyntaxAnalyzer()
        self.polite_analyzer = PolitenessConcordAnalyzer()
        self.tone_analyzer = ToneConsistencyAnalyzer()

    def check(self, text: str) -> Dict[str, any]:
        clf_res = self.clf_analyzer.analyze(text)
        polite_res = self.polite_analyzer.analyze(text)
        tone_res = self.tone_analyzer.analyze(text)
        
        all_errors = []
        all_errors.extend(clf_res["violations"])
        all_errors.extend(polite_res["violations"])
        
        is_valid = len(all_errors) == 0
        overall_score = (clf_res["classifier_score"] + polite_res["politeness_score"] + tone_res["tone_score"]) / 3.0
        
        return {
            "input_text": text,
            "is_grammatically_sound": is_valid,
            "overall_score": round(overall_score, 4),
            "errors": all_errors,
            "corrected_text": polite_res["corrected_text"]
        }
