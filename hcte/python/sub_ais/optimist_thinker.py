"""
optimist_thinker.py — Persona 1: The Optimist (HCTE)
Best-case trajectories, possibility density, strength amplification.
"""
from __future__ import annotations
import re
from typing import Dict, Any

class OptimistThinker:
    OPPORTUNITY_CUES = [
        "opportunity","potential","could","possible","achievable","growth",
        "leverage","strength","advantage","gain","win","succeed","capable",
        "innovative","promising","exciting","expand","improve","build","create"
    ]
    HOPE_AMPLIFIERS = [
        "absolutely","certainly","confident","believe we can","positive that",
        "great chance","strong position","well-placed","ready to","excited to"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        words = re.findall(r'\b[a-z]{3,}\b', l)
        total = max(1, len(words))

        opp_hits = sum(1 for c in self.OPPORTUNITY_CUES if c in l)
        hope_hits = sum(1 for h in self.HOPE_AMPLIFIERS if h in l)

        possibility_density = min(1.0, opp_hits / total * 20.0)
        hope_signal         = min(1.0, 0.40 + hope_hits * 0.18)
        strength_amp        = min(1.0, 0.35 + (opp_hits + hope_hits) * 0.08)

        composite = (possibility_density * 0.40 + hope_signal * 0.35 + strength_amp * 0.25)
        composite = min(1.0, max(0.0, composite))

        best_case = self._generate_best_case(scenario, opp_hits)

        return {
            "persona": "optimist",
            "emotional_charge": +composite,           # positive
            "possibility_density": round(possibility_density, 3),
            "hope_signal": round(hope_signal, 3),
            "strength_amplification": round(strength_amp, 3),
            "composite_score": round(composite, 3),
            "best_case_outcome": best_case,
            "core_insight": f"Maximum opportunity: {opp_hits} strength signals detected.",
            "action": "Amplify strengths, pursue highest-upside path aggressively."
        }

    def _generate_best_case(self, scenario: str, signal_count: int) -> str:
        if signal_count >= 5:
            return "Outstanding trajectory — conditions are ideal for breakthrough outcome."
        elif signal_count >= 3:
            return "Strong potential identified — focused execution yields excellent results."
        elif signal_count >= 1:
            return "Promising foundation — targeted effort can unlock significant upside."
        else:
            return "Limited signals currently — opportunity exists to create conditions for success."
