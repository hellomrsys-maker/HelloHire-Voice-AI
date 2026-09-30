"""
Hindustani Pragmatics & Honorific Skill.
Evaluates the 3-tier social address hierarchy (aap vs. tum vs. tu), honorific particle ji,
verbal honorific agreement, and politeness scoring.
"""

from typing import Dict, Any, List, Optional, Set


class HindustaniPragmaticsEngine:
    """
    Evaluates sociolinguistic registers, honorific deference, and politeness in Hindustani.
    """

    AAP_MARKERS: Set[str] = {"aap", "aapne", "aapka", "aapke", "aapki", "aapko", "आप", "आपने", "आपका", "आपके", "आपकी", "आपको"}
    TUM_MARKERS: Set[str] = {"tum", "tumne", "tumhara", "tumhare", "tumhari", "tumhein", "तुम", "तुमने", "तुम्हारा", "तुम्हारे", "तुम्हारी", "तुम्हें"}
    TU_MARKERS: Set[str] = {"tu", "tune", "tera", "tere", "teri", "tujhe", "तू", "तूने", "तेरा", "तेरे", "तेरी", "तुझे"}

    HONORIFIC_PARTICLES: List[str] = ["ji", "saab", "sahib", "shri", "shrimati", "जी", "साहब", "श्री", "श्रीमती"]
    COURTESY_WORDS: List[str] = ["kripya", "dhanyavaad", "shukriya", "namaste", "namaskar", "adaab", "कृपया", "धन्यवाद", "शुक्रिया", "नमस्ते", "नमस्कार", "आदाब"]

    def evaluate_pragmatics(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the text for address tier, honorific particles, and calculates politeness score.
        """
        low = text.lower()
        tokens = low.replace("|", " ").replace("।", " ").replace(",", " ").replace(".", " ").replace("?", " ").split()

        has_aap = any(t in self.AAP_MARKERS for t in tokens) or any(t in self.AAP_MARKERS for t in text.split())
        has_tum = any(t in self.TUM_MARKERS for t in tokens) or any(t in self.TUM_MARKERS for t in text.split())
        has_tu = any(t in self.TU_MARKERS for t in tokens) or any(t in self.TU_MARKERS for t in text.split())

        has_ji = any(p in low or p in text for p in self.HONORIFIC_PARTICLES)
        has_courtesy = any(c in low or c in text for c in self.COURTESY_WORDS)

        # Detect address clash
        tier_count = sum([has_aap, has_tum, has_tu])
        has_clash = tier_count > 1

        # Tier assignment
        if has_aap or (has_ji and not has_tum and not has_tu):
            tier = "tier_3_aap"
            base_score = 0.85
        elif has_tum:
            tier = "tier_2_tum"
            base_score = 0.55
        elif has_tu:
            tier = "tier_1_tu"
            base_score = 0.25
        else:
            tier = "tier_neutral"
            base_score = 0.60

        if has_ji:
            base_score += 0.10
        if has_courtesy:
            base_score += 0.05

        score = min(1.0, round(base_score, 2))

        return {
            "address_tier": tier,
            "is_formal": tier == "tier_3_aap",
            "is_familiar": tier == "tier_2_tum",
            "is_intimate": tier == "tier_1_tu",
            "has_honorific_particle_ji": has_ji,
            "has_courtesy_words": has_courtesy,
            "has_address_clash": has_clash,
            "politeness_score": score,
            "message": (
                "Conflit de niveaux d'adresse détecté !"
                if has_clash
                else f"Registre conforme ({tier})."
            )
        }
