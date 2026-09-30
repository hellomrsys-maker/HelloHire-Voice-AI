"""
Thai Politeness Concord Cognitive Analyzer.
Audits sentence-final politeness particles for speaker gender and speech-act harmony.
"""

from typing import Dict
from Thai_engine.brain.skills.politeness_engine import audit_politeness_particles

class PolitenessConcordAnalyzer:
    """
    Evaluates politeness particles (ครับ / ค่ะ / คะ) for grammatical and pragmatic concord.
    """
    def __init__(self):
        self.name = "Thai Politeness Concord Analyzer"

    def analyze(self, text: str) -> Dict[str, any]:
        audit_res = audit_politeness_particles(text)
        
        return {
            "text": text,
            "is_concordant": audit_res["is_concordant"],
            "violations": audit_res["violations"],
            "corrected_text": audit_res["corrected_text"],
            "has_particles": audit_res["has_particles"],
            "speaker_gender": audit_res["speaker_gender_hint"],
            "politeness_score": 1.0 if audit_res["is_concordant"] else 0.6
        }
