"""
Persian Ta'arof & Deference Analyzer
Cognitive analysis module auditing politeness levels, register consistency,
and detecting colloquial leaks in formal communication.
"""

from typing import Dict, Any, List
from Persian_engine.brain.skills.pragmatics_engine import PersianPragmaticsEngine

# Colloquial Tehrani vowel shifts and contractions
COLLOQUIAL_LEAKS = {
    "تهرون": "تهران",
    "نون": "نان",
    "خونه": "خانه",
    "دندون": "دندان",
    "میدونه": "می‌داند",
    "میتونه": "می‌تواند",
    "میره": "می‌رود",
    "میگه": "می‌گوید",
    "اومد": "آمد",
    "کتابا": "کتاب‌ها",
    "بچه‌ها": "کودکان / فرزندان",
    "فدات": "با احترام",
    "قربانت": "با احترام"
}

class TaarofDeferenceAnalyzer:
    """
    Audits communicative deference, calculates politeness indices,
    and detects inappropriate register mixing.
    """

    def __init__(self):
        self.pragmatics = PersianPragmaticsEngine()

    def audit_deference_and_register(self, text: str, target_register: str = "formal") -> Dict[str, Any]:
        """
        Audits text against a target register (high_taarof, formal, informal).
        Detects colloquialisms and computes politeness score.
        """
        detection = self.pragmatics.detect_register(text)
        detected_tier = detection["dominant_register"]
        
        colloquial_findings = []
        words = text.split()
        for w in words:
            clean = w.strip("،؛.؟!«»")
            if clean in COLLOQUIAL_LEAKS:
                colloquial_findings.append({
                    "colloquial_form": clean,
                    "standard_written": COLLOQUIAL_LEAKS[clean],
                    "message": f"Colloquial spoken form '{clean}' detected in written text; replace with standard '{COLLOQUIAL_LEAKS[clean]}'."
                })

        # Calculate alignment
        register_aligned = (detected_tier == target_register) or (target_register == "formal" and detected_tier == "high_taarof")
        if target_register in {"formal", "high_taarof"} and colloquial_findings:
            register_aligned = False

        deference_score = 1.0
        if colloquial_findings:
            deference_score -= min(0.6, len(colloquial_findings) * 0.15)
        if not register_aligned:
            deference_score -= 0.2

        return {
            "detected_register": detected_tier,
            "target_register": target_register,
            "is_aligned": register_aligned,
            "colloquial_findings": colloquial_findings,
            "deference_score": round(max(0.0, deference_score), 2),
            "tier_level": detection["tier_level"]
        }
