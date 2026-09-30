"""
Cantonese Grammar Checking Task Pipeline.
Proofreads Cantonese sentences for DOC word order (V + DO + IO),
postverbal adverbs (行先), aspect markers, and SFP naturalness.
"""

from typing import Dict, List
from Cantonese_engine.brain.analysis.doc_inversion_analyzer import DocInversionAnalyzer
from Cantonese_engine.brain.analysis.sfp_cluster_analyzer import SfpClusterAnalyzer
from Cantonese_engine.brain.analysis.diglossic_drift_analyzer import DiglossicDriftAnalyzer
from Cantonese_engine.brain.skills.aspect_engine import extract_aspect_markers

class CantoneseGrammarChecker:
    """
    Automated proofreading pipeline for Cantonese text.
    """
    def __init__(self):
        self.doc_analyzer = DocInversionAnalyzer()
        self.sfp_analyzer = SfpClusterAnalyzer()
        self.drift_analyzer = DiglossicDriftAnalyzer()

    def check(self, text: str) -> Dict[str, any]:
        doc_res = self.doc_analyzer.analyze(text)
        sfp_res = self.sfp_analyzer.analyze(text)
        drift_res = self.drift_analyzer.analyze(text, target_register="colloquial")
        aspects = extract_aspect_markers(text)
        
        all_errors = []
        all_errors.extend(doc_res["violations"])
        all_errors.extend(drift_res["drift_warnings"])
        
        is_valid = len(all_errors) == 0
        overall_score = (doc_res["accuracy_score"] + drift_res["register_score"] + sfp_res["pragmatic_score"]) / 3.0
        
        return {
            "input_text": text,
            "is_grammatically_sound": is_valid,
            "overall_score": round(overall_score, 4),
            "errors": all_errors,
            "suggested_text": doc_res["normalized_canonical_text"],
            "aspects_found": [a["marker"] for a in aspects],
            "sfps_found": sfp_res["particles"]
        }
