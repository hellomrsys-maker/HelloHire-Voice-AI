"""
analyst_thinker.py — Persona 5: The Analyst (HCTE)
Evidence weighting, logical chain validation, statistical reasoning.
"""
from __future__ import annotations
import re
from typing import Dict, Any

class AnalystThinker:
    EVIDENCE_CUES = [
        "data","evidence","study","research","metric","statistic","analysis",
        "finding","result","experiment","test","measure","benchmark","survey",
        "report","figure","percentage","%","rate","ratio","coefficient"
    ]
    LOGIC_CONNECTORS = [
        "therefore","because","consequently","hence","it follows","given that",
        "evidence shows","data indicates","analysis reveals","due to","results in"
    ]
    FALLACIES = [
        "everyone knows","it's obvious","always","never","trust me","just believe",
        "it's common sense","you can't deny"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        evidence_hits = sum(1 for c in self.EVIDENCE_CUES if c in l)
        logic_hits    = sum(1 for c in self.LOGIC_CONNECTORS if c in l)
        fallacy_hits  = sum(1 for f in self.FALLACIES if f in l)
        has_numbers   = bool(re.search(r'\d+\.?\d*\s*%|\d+x\b|\$\d+|\bp[<=>]\s*\d', scenario))

        evidence_score = min(1.0, 0.20 + evidence_hits * 0.12 + (0.20 if has_numbers else 0.0))
        logic_score    = min(1.0, 0.25 + logic_hits * 0.15)
        fallacy_penalty = min(0.45, fallacy_hits * 0.15)

        confidence = max(0.0, min(1.0, (evidence_score + logic_score) * 0.5 - fallacy_penalty))

        return {
            "persona": "analyst",
            "emotional_charge": 0.0,  # neutral
            "evidence_score": round(evidence_score, 3),
            "logic_chain_score": round(logic_score, 3),
            "fallacy_count": fallacy_hits,
            "data_backed": has_numbers,
            "analytical_confidence": round(confidence, 3),
            "composite_score": round(confidence, 3),
            "core_insight": f"Evidence depth: {evidence_hits} data signals, {logic_hits} logic connectors, {fallacy_hits} fallacies.",
            "action": "Demand data for top 3 claims. Reject any claim without quantifiable support."
        }


class IntuitiveThinker:
    """Persona 6: Fast-path heuristic pattern recognition (System 1)."""
    EXPERT_PATTERNS = [
        "i've seen this before","classic case","textbook","pattern here","reminds me of",
        "gut feeling","instinctively","experienced this","this feels like","similar to"
    ]
    FAMILIAR_DOMAINS = [
        "startup","enterprise","engineering","product","finance","marketing",
        "operations","hr","legal","medical","technical"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        pattern_hits = sum(1 for p in self.EXPERT_PATTERNS if p in l)
        domain_hits  = sum(1 for d in self.FAMILIAR_DOMAINS if d in l)

        pattern_match = min(1.0, 0.45 + pattern_hits * 0.20)
        domain_familiarity = min(1.0, 0.35 + domain_hits * 0.15)
        heuristic_confidence = (pattern_match * 0.55 + domain_familiarity * 0.45)

        return {
            "persona": "intuitive",
            "emotional_charge": +0.15,
            "pattern_match_score": round(pattern_match, 3),
            "domain_familiarity": round(domain_familiarity, 3),
            "composite_score": round(heuristic_confidence, 3),
            "fast_path_verdict": "PROCEED" if heuristic_confidence >= 0.65 else "PAUSE_AND_VERIFY",
            "core_insight": f"Pattern recognition: {domain_hits} domain signals, confidence {heuristic_confidence:.0%}.",
            "action": "Trust the pattern — but verify the top 2 deviations from the familiar template."
        }


class EmpathThinker:
    """Persona 7: Social intelligence — how does this affect people?"""
    HUMAN_CUES = [
        "team","people","customer","user","employee","stakeholder","family",
        "community","individual","person","human","colleague","client","partner"
    ]
    IMPACT_CUES = [
        "affect","impact","experience","feel","suffer","benefit","hurt","help",
        "empower","harm","wellbeing","morale","stress","burnout","trust"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        human_hits  = sum(1 for c in self.HUMAN_CUES if c in l)
        impact_hits = sum(1 for c in self.IMPACT_CUES if c in l)

        human_salience    = min(1.0, 0.30 + human_hits * 0.12)
        impact_awareness  = min(1.0, 0.25 + impact_hits * 0.14)
        empathy_composite = (human_salience * 0.55 + impact_awareness * 0.45)

        affected_groups = self._identify_affected_groups(scenario)

        return {
            "persona": "empath",
            "emotional_charge": +0.10,  # warm, humanistic
            "human_salience": round(human_salience, 3),
            "impact_awareness": round(impact_awareness, 3),
            "composite_score": round(empathy_composite, 3),
            "affected_groups": affected_groups,
            "core_insight": f"Human impact detected: {human_hits} people-signals, {impact_hits} impact signals.",
            "action": "Consult all affected groups before deciding. Their experience IS the outcome."
        }

    def _identify_affected_groups(self, scenario: str) -> list:
        groups = []
        l = scenario.lower()
        if "team" in l or "employee" in l: groups.append("Internal team members")
        if "customer" in l or "user" in l: groups.append("End customers/users")
        if "stakeholder" in l: groups.append("Executive stakeholders")
        if "community" in l: groups.append("External community")
        if not groups: groups.append("Implicit stakeholders — map before proceeding")
        return groups
