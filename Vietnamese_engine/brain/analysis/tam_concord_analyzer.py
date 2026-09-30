"""
Vietnamese TAM Concord Analyzer
Cognitive analysis module auditing preverbal Tense-Aspect-Mood particles and sequencing.
"""

from typing import Dict, Any, List
from Vietnamese_engine.brain.skills.pos_tagging import VietnamesePOSTagger

INVALID_TAM_SEQUENCES = {
    ("sẽ", "đã"): "Contradictory future and past particles (sẽ đã)",
    ("đã", "sẽ"): "Contradictory past and future particles (đã sẽ)",
    ("chưa", "đã"): "Contradictory not-yet and already particles (chưa đã)"
}

class TAMConcordAnalyzer:
    """
    Audits preverbal particle sequencing and temporal logic.
    """

    def __init__(self):
        self.tagger = VietnamesePOSTagger()

    def audit_tam_particles(self, text: str) -> Dict[str, Any]:
        """Audits preverbal TAM particle clusters for logical and syntactic validity."""
        words = text.lower().split()
        issues = []
        tam_count = 0
        
        for i in range(len(words) - 1):
            w1 = words[i].strip(",.?!")
            w2 = words[i + 1].strip(",.?!")
            
            pair = (w1, w2)
            if pair in INVALID_TAM_SEQUENCES:
                issues.append({
                    "sequence": f"{w1} {w2}",
                    "type": "invalid_tam_ordering",
                    "message": INVALID_TAM_SEQUENCES[pair]
                })
            elif w1 in {"đã", "đang", "sẽ", "vừa", "mới", "chưa"}:
                tam_count += 1

        return {
            "tam_particle_count": tam_count,
            "issues": issues,
            "is_valid": len(issues) == 0
        }
