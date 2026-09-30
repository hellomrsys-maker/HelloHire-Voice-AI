"""
Vietnamese Kinship Deference Analyzer
Cognitive analysis module auditing kinship address consistency and politeness particles.
"""

from typing import Dict, Any, List
from Vietnamese_engine.brain.skills.kinship_engine import VietnameseKinshipEngine, RECIPROCAL_PAIRS
from Vietnamese_engine.brain.skills.pragmatics_engine import VietnamesePragmaticsEngine

class KinshipDeferenceAnalyzer:
    """
    Audits conversational deixis, ensuring:
    - Speaker-addressee kinship reciprocal terms match (e.g. em addresses anh, not bác)
    - Sentence-final politeness particle 'ạ' is present when addressing seniors
    """

    def __init__(self):
        self.kinship = VietnameseKinshipEngine()
        self.pragmatics = VietnamesePragmaticsEngine()

    def audit_dialogue_deixis(
        self,
        text: str,
        speaker_term: Optional[str] = None,
        listener_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Audits kinship symmetry and politeness particles."""
        extracted_terms = self.kinship.extract_kinship_terms(text)
        
        is_senior = False
        if listener_term in {"ông", "bà", "bác", "chú", "cô", "thầy"}:
            is_senior = True
            
        politeness = self.pragmatics.audit_politeness_particle(text, is_senior_addressee=is_senior)
        
        reciprocal_valid = True
        reciprocal_relation = "not_specified"
        if speaker_term and listener_term:
            reciprocal_valid = self.kinship.is_valid_reciprocal_pair(speaker_term, listener_term)
            reciprocal_relation = RECIPROCAL_PAIRS.get((speaker_term.lower(), listener_term.lower()), "invalid_symmetry")

        deference_score = 1.0
        if politeness["missing_mandatory_a"]:
            deference_score -= 0.3
        if not reciprocal_valid:
            deference_score -= 0.4

        return {
            "speaker_term": speaker_term,
            "listener_term": listener_term,
            "extracted_terms": extracted_terms,
            "reciprocal_valid": reciprocal_valid,
            "relationship": reciprocal_relation,
            "politeness_audit": politeness,
            "deference_score": round(max(0.0, deference_score), 2),
            "is_valid": reciprocal_valid and not politeness["missing_mandatory_a"]
        }
