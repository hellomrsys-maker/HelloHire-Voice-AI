"""
contradiction_detector_ai.py — Detects narrative and factual contradictions across interview turns.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Tuple

class ContradictionDetectorAI:
    """
    Extracts key claims (numbers, team sizes, project lengths, roles) across turns
    and checks for direct inconsistencies.
    """

    def __init__(self):
        self.claim_history: List[Dict[str, Any]] = []

    def evaluate(self, current_turn: int, current_text: str, prior_turns: Optional[List[str]] = None) -> Dict[str, Any]:
        cleaned = current_text.lower()
        claims = self._extract_claims(cleaned)

        contradictions: List[str] = []
        severity = 0.0

        for past in self.claim_history:
            past_turn = past["turn"]
            past_claims = past["claims"]

            # 1. Team size contradiction
            if "team_size" in claims and "team_size" in past_claims:
                curr_size = claims["team_size"]
                prev_size = past_claims["team_size"]
                # If sizes differ by more than 2x without qualification
                if max(curr_size, prev_size) / max(min(curr_size, prev_size), 1) >= 2.5:
                    contradictions.append(
                        f"Team size conflict: Turn {past_turn} claimed {prev_size} people, but Turn {current_turn} claimed {curr_size} people."
                    )
                    severity += 0.35

            # 2. Years of experience / tenure contradiction
            if "years" in claims and "years" in past_claims:
                curr_yr = claims["years"]
                prev_yr = past_claims["years"]
                if abs(curr_yr - prev_yr) >= 3:
                    contradictions.append(
                        f"Tenure conflict: Turn {past_turn} mentioned {prev_yr} years, but Turn {current_turn} mentioned {curr_yr} years."
                    )
                    severity += 0.30

            # 3. Direct role contradiction (e.g. sole contributor vs managed a team)
            if claims.get("solo_worker") and past_claims.get("managed_team"):
                contradictions.append(
                    f"Role conflict: Turn {past_turn} claimed managing a team, but Turn {current_turn} claimed being a solo individual contributor."
                )
                severity += 0.40

            # 4. Direct technology stance / reliability contradiction
            curr_stances = claims.get("tech_stances", {})
            past_stances = past_claims.get("tech_stances", {})
            for tech, stance in curr_stances.items():
                if tech in past_stances:
                    past_st = past_stances[tech]
                    if (stance == "flawless" and past_st == "broken") or (stance == "broken" and past_st == "flawless"):
                        contradictions.append(
                            f"Factual contradiction: Turn {past_turn} claimed {tech} was {past_st}, but Turn {current_turn} claimed it was {stance}."
                        )
                        severity += 0.50

        # Save current claims
        self.claim_history.append({"turn": current_turn, "claims": claims, "text": current_text})

        penalty = min(1.0, severity)
        coherence_score = max(0.0, 1.0 - penalty)

        return {
            "coherence_score": round(coherence_score, 3),
            "contradiction_penalty": round(penalty, 3),
            "contradictions_found": contradictions,
            "has_contradictions": len(contradictions) > 0,
            "claims_extracted": claims
        }

    def _extract_claims(self, text: str) -> Dict[str, Any]:
        claims: Dict[str, Any] = {}

        # Team size: "team of 5", "managed 20 engineers"
        m_team = re.search(r"\b(?:team\s+of|managed|led)\s+(\d+)\b", text)
        if m_team:
            claims["team_size"] = int(m_team.group(1))

        # Years: "5 years", "3+ years"
        m_years = re.search(r"\b(\d+)\+?\s+years\b", text)
        if m_years:
            claims["years"] = int(m_years.group(1))

        if any(w in text for w in ["solely built", "solo developer", "did it all myself", "only person"]):
            claims["solo_worker"] = True
        if any(w in text for w in ["my direct reports", "managed a team", "led 5 engineers", "engineering manager"]):
            claims["managed_team"] = True

        # Tech stance tracking (e.g., "Redis never fails" vs "Redis always fails")
        tech_stances = {}
        for tech in ["redis", "kafka", "postgres", "kubernetes", "docker", "dynamodb"]:
            if tech in text:
                if any(pos in text for pos in ["never fails", "100% reliable", "always reliable", "never broken"]):
                    tech_stances[tech] = "flawless"
                elif any(neg in text for neg in ["always fails", "refuse to work with", "fails immediately", "totally broken", "never use"]):
                    tech_stances[tech] = "broken"
        if tech_stances:
            claims["tech_stances"] = tech_stances

        return claims
