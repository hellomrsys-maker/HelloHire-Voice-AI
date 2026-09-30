"""
conceptual_distance_ai.py — Conceptual Manifold Distance Calculation Sub-AI (CDIE)

Measures the semantic distance between the domains bridged. Higher distance with coherent
causal link indicates superior lateral genius.
"""
from __future__ import annotations
import math
from typing import Dict, Any, List

class ConceptualDistanceAI:
    # Co-occurrence distance table between core knowledge domains
    DOMAIN_DISTANCES = {
        ("biology", "software"): 0.85,
        ("physics", "software"): 0.65,
        ("military", "software"): 0.70,
        ("architecture", "software"): 0.40,
        ("biology", "physics"): 0.60,
        ("economics", "physics"): 0.55
    }

    def evaluate(self, active_domains: List[str], has_causal_link: bool = True) -> Dict[str, Any]:
        if len(active_domains) < 2:
            return {
                "sub_ai": "conceptual_distance",
                "domain_pair": None,
                "manifold_distance": 0.20,
                "composite_score": 0.25
            }

        d1, d2 = active_domains[0], active_domains[1]
        pair = (min(d1, d2), max(d1, d2))
        dist = self.DOMAIN_DISTANCES.get(pair, 0.75)

        # Distance is rewarded when accompanied by coherent causal grounding
        rewarded_score = dist if has_causal_link else dist * 0.50

        return {
            "sub_ai": "conceptual_distance",
            "domain_pair": list(pair),
            "manifold_distance": round(dist, 3),
            "composite_score": round(rewarded_score, 3)
        }
