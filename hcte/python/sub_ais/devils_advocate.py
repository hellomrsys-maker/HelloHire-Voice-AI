"""
devils_advocate.py — Persona 4: The Devil's Advocate (HCTE)
Attacks the strongest-held assumptions. Challenges consensus.
Steelmans the opposing view.
"""
from __future__ import annotations
import re
from typing import Dict, Any, List

class DevilsAdvocate:
    CONSENSUS_MARKERS = [
        "everyone agrees","it's obvious","clearly","of course","definitely","certainly",
        "without doubt","as we all know","it's clear that","it goes without saying",
        "always","never","all","every","none","impossible"
    ]
    ASSUMPTION_PHRASES = [
        "assuming","we believe","we expect","our plan","the strategy","we will",
        "it will work","the approach","the solution","best practice","proven"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        consensus_hits = sum(1 for c in self.CONSENSUS_MARKERS if c in l)
        assumption_hits = sum(1 for a in self.ASSUMPTION_PHRASES if a in l)

        # Strength of devil's advocate position = how strongly consensus is stated
        challenge_urgency = min(1.0, 0.40 + consensus_hits * 0.18 + assumption_hits * 0.12)

        inversions = self._invert_assumptions(scenario)
        steelman   = self._build_steelman(scenario)

        return {
            "persona": "devils_advocate",
            "emotional_charge": -0.30,  # mildly negative — challenging
            "challenge_urgency": round(challenge_urgency, 3),
            "consensus_markers_found": consensus_hits,
            "assumption_markers_found": assumption_hits,
            "composite_score": round(challenge_urgency, 3),
            "assumption_inversions": inversions,
            "steelman_opposition": steelman,
            "core_insight": f"Found {consensus_hits} consensus markers and {assumption_hits} unverified assumptions.",
            "action": "Test each assumption explicitly. What if the opposite is true?"
        }

    def _invert_assumptions(self, scenario: str) -> List[str]:
        inversions = []
        l = scenario.lower()
        if "will work" in l or "proven" in l:
            inversions.append("What if this approach specifically fails in our context?")
        if "team" in l or "people" in l:
            inversions.append("What if the team is not capable or aligned as assumed?")
        if "customer" in l or "user" in l:
            inversions.append("What if users don't want what we're building?")
        if "time" in l or "schedule" in l:
            inversions.append("What if the timeline is fundamentally unrealistic?")
        if "cost" in l or "budget" in l:
            inversions.append("What if the actual cost is 3× the estimate?")
        if not inversions:
            inversions.append("What if the core premise of this entire scenario is wrong?")
            inversions.append("What if we're solving the wrong problem entirely?")
        return inversions

    def _build_steelman(self, scenario: str) -> str:
        return (
            "The strongest opposing argument: the evidence base for this approach "
            "may be cherry-picked or context-specific. Alternative frameworks could "
            "yield superior outcomes. The consensus view may be suppressing valid "
            "dissent that deserves a hearing."
        )
