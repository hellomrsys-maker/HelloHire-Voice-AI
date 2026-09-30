"""
pessimist_thinker.py — Persona 2: The Pessimist (HCTE)
Risk enumeration, vulnerability cataloguing, threat prioritization.
"""
from __future__ import annotations
import re
from typing import Dict, Any, List

class PessimistThinker:
    RISK_CUES = [
        "risk","fail","problem","issue","concern","danger","threat","weakness",
        "uncertain","unclear","missing","lack","gap","barrier","obstacle","difficult",
        "impossible","wrong","error","mistake","loss","cost","harm","delay","conflict"
    ]
    CATASTROPHE_AMPLIFIERS = [
        "catastrophic","fatal","irreversible","devastating","collapse","breakdown",
        "critical failure","worst case","unrecoverable","systemic"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        words = re.findall(r'\b[a-z]{3,}\b', l)
        total = max(1, len(words))

        risk_hits  = sum(1 for c in self.RISK_CUES if c in l)
        cat_hits   = sum(1 for c in self.CATASTROPHE_AMPLIFIERS if c in l)

        risk_density     = min(1.0, risk_hits / total * 15.0)
        catastrophe_flag = min(1.0, cat_hits * 0.35)
        vulnerability    = min(1.0, 0.30 + risk_hits * 0.10)

        # Higher risk = higher pessimism score (pessimist is more activated)
        composite = (risk_density * 0.45 + catastrophe_flag * 0.30 + vulnerability * 0.25)
        composite = min(1.0, max(0.1, composite + 0.20))  # baseline pessimism always present

        risks = self._enumerate_risks(scenario, risk_hits, cat_hits)

        return {
            "persona": "pessimist",
            "emotional_charge": -(composite),  # negative charge
            "risk_density": round(risk_density, 3),
            "catastrophe_signal": round(catastrophe_flag, 3),
            "vulnerability_score": round(vulnerability, 3),
            "composite_score": round(composite, 3),
            "enumerated_risks": risks,
            "core_insight": f"Risks detected: {risk_hits} warning signals, {cat_hits} catastrophe markers.",
            "action": "Map all vulnerabilities before committing. Do not proceed blind."
        }

    def _enumerate_risks(self, scenario: str, risk_count: int, cat_count: int) -> List[str]:
        risks = []
        if "deadline" in scenario.lower() or "time" in scenario.lower():
            risks.append("Timeline risk: schedule may be unrealistic")
        if "resource" in scenario.lower() or "budget" in scenario.lower():
            risks.append("Resource risk: funding or capacity constraints likely")
        if "team" in scenario.lower() or "people" in scenario.lower():
            risks.append("Human risk: key person dependency or team misalignment")
        if cat_count > 0:
            risks.append("Catastrophic failure pathway identified — requires immediate mitigation")
        if not risks:
            risks.append("Latent risk: insufficient information to fully assess downside")
        return risks
