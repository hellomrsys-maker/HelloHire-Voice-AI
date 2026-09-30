"""
systems_thinker.py — Persona 8: The Systems Thinker (HCTE)
Feedback loops, unintended consequences, second-order effects.
"""
from __future__ import annotations
import re
from typing import Dict, Any, List

class SystemsThinker:
    SYSTEM_CUES = [
        "feedback","loop","cascade","ripple","downstream","upstream","interdepend",
        "systemic","ecosystem","interconnect","chain","network","flow","cycle",
        "emerge","second order","unintended","side effect","consequence"
    ]
    COMPLEXITY_MARKERS = [
        "complex","complicated","nonlinear","exponential","chaotic","dynamic",
        "adaptive","emergent","distributed","multi-layered","entangled"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        system_hits = sum(1 for c in self.SYSTEM_CUES if c in l)
        complex_hits = sum(1 for c in self.COMPLEXITY_MARKERS if c in l)

        system_awareness   = min(1.0, 0.35 + system_hits * 0.14)
        complexity_depth   = min(1.0, 0.25 + complex_hits * 0.20)
        feedback_detection = min(1.0, 0.30 + (system_hits * 0.08))

        composite = (system_awareness * 0.40 + complexity_depth * 0.35 + feedback_detection * 0.25)

        second_order = self._project_second_order(scenario)

        return {
            "persona": "systems_thinker",
            "emotional_charge": 0.0,  # analytical, neutral
            "system_awareness": round(system_awareness, 3),
            "complexity_detected": round(complexity_depth, 3),
            "feedback_loop_score": round(feedback_detection, 3),
            "composite_score": round(composite, 3),
            "second_order_effects": second_order,
            "core_insight": f"Systems lens: {system_hits} feedback signals, {complex_hits} complexity markers.",
            "action": "Map all feedback loops before acting. Every action has 2nd and 3rd order effects."
        }

    def _project_second_order(self, scenario: str) -> List[str]:
        effects = []
        l = scenario.lower()
        if "cut" in l or "reduce" in l or "remove" in l:
            effects.append("2nd order: Removing X may reduce morale/capacity in adjacent systems")
        if "scale" in l or "grow" in l or "expand" in l:
            effects.append("2nd order: Scaling creates coordination overhead — complexity grows faster than team")
        if "automate" in l or "ai" in l or "tool" in l:
            effects.append("2nd order: Automation may eliminate skill development — creates fragility")
        if "incentive" in l or "bonus" in l or "reward" in l:
            effects.append("2nd order: Incentive structure may optimize one metric while degrading others")
        if not effects:
            effects.append("2nd order: Unintended systemic effects likely — map dependencies before commit")
        return effects


class VisionaryThinker:
    """Persona 9: Long-horizon projection, paradigm-shift detection."""
    FUTURE_CUES = [
        "future","long term","in 5 years","decade","horizon","trajectory","trend",
        "paradigm","disrupt","transform","shift","revolution","next generation",
        "emerging","frontier","breakthrough","vision","10x","100x"
    ]
    PARADIGM_SHIFTS = [
        "ai","automation","climate","regulation","demographic","platform","network effect",
        "open source","decentralized","remote","hybrid","generational shift"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        future_hits   = sum(1 for c in self.FUTURE_CUES if c in l)
        paradigm_hits = sum(1 for p in self.PARADIGM_SHIFTS if p in l)

        horizon_score     = min(1.0, 0.30 + future_hits * 0.18)
        paradigm_detected = min(1.0, paradigm_hits * 0.25)
        vision_composite  = (horizon_score * 0.60 + paradigm_detected * 0.40)

        return {
            "persona": "visionary",
            "emotional_charge": +0.30,  # inspired, excited
            "horizon_score": round(horizon_score, 3),
            "paradigm_shift_detected": round(paradigm_detected, 3),
            "composite_score": round(vision_composite, 3),
            "horizon_label": "LONG" if future_hits >= 3 else "MEDIUM" if future_hits >= 1 else "SHORT",
            "core_insight": f"Vision depth: {future_hits} future signals, {paradigm_hits} paradigm-shift signals.",
            "action": "Plan for the world 5 years from now, not the world today. Today is already obsolete."
        }


class AbsurdistThinker:
    """Persona 10: Lateral leap generation, problem reframing, wild-card ideation."""
    LATERAL_CUES = [
        "what if","imagine","suppose","could we","alternative","different approach",
        "flip","reverse","invert","opposite","random","wild","crazy idea","unconventional"
    ]

    def think(self, scenario: str) -> Dict[str, Any]:
        l = scenario.lower()
        lateral_hits = sum(1 for c in self.LATERAL_CUES if c in l)
        has_constraint = any(w in l for w in ["can't","cannot","impossible","never","must","required"])

        divergence_score = min(1.0, 0.25 + lateral_hits * 0.20)
        reframe_score    = min(1.0, 0.45 + (0.20 if has_constraint else 0.0))

        wild_ideas = self._generate_lateral_leaps(scenario)

        composite = (divergence_score * 0.45 + reframe_score * 0.55)

        return {
            "persona": "absurdist",
            "emotional_charge": +0.45,  # playful, energized
            "divergence_score": round(divergence_score, 3),
            "reframe_urgency": round(reframe_score, 3),
            "composite_score": round(composite, 3),
            "wild_ideas": wild_ideas,
            "core_insight": f"Lateral potential: {lateral_hits} divergent signals. Constraints present: {has_constraint}.",
            "action": "Generate 10 ridiculous ideas. At least 1 will be brilliant once stripped of the absurdity."
        }

    def _generate_lateral_leaps(self, scenario: str) -> List[str]:
        return [
            "What if we eliminated the problem entirely rather than solving it?",
            "What if the customer solved this themselves with minimal help from us?",
            "What if we inverted the entire process — start from the output and work backwards?",
            "What if the constraint that makes this 'impossible' is actually optional?",
            "What if we borrowed the solution from a completely unrelated industry?"
        ]


class MetacognitionMonitor:
    """Persona 11: Watches all other personas for cognitive bias, groupthink, and blind spots."""

    BIAS_THRESHOLDS = {
        "optimism_bias":      {"optimist_min": 0.85, "pessimist_max": 0.30},
        "catastrophising":    {"premortem_rpn_max_avg": 8.5},
        "groupthink":         {"tension_max": 0.15},
        "analysis_paralysis": {"analyst_confidence_max": 0.30},
        "sycophancy":         {"empath_min": 0.90, "analyst_max": 0.40},
    }

    def monitor(self, persona_outputs: Dict[str, Dict]) -> Dict[str, Any]:
        alerts = []
        corrections = []

        optimist_score  = persona_outputs.get("optimist", {}).get("composite_score", 0.5)
        pessimist_score = persona_outputs.get("pessimist", {}).get("composite_score", 0.5)
        analyst_score   = persona_outputs.get("analyst", {}).get("composite_score", 0.5)
        empath_score    = persona_outputs.get("empath", {}).get("composite_score", 0.5)

        # Collect all persona scores for tension calculation
        scores = [v.get("composite_score", 0.5) for v in persona_outputs.values() if isinstance(v, dict)]
        avg = sum(scores) / max(1, len(scores))
        variance = sum((s - avg) ** 2 for s in scores) / max(1, len(scores))
        cognitive_tension = min(1.0, variance * 8.0)  # High variance = high tension = creative pressure

        # Bias checks
        if optimist_score >= 0.85 and pessimist_score <= 0.30:
            alerts.append("OPTIMISM BIAS: Optimist dominant, pessimist suppressed — force risk review")
            corrections.append("Escalate pessimist and pre-mortem weight in synthesis")

        if analyst_score <= 0.30:
            alerts.append("ANALYSIS PARALYSIS RISK: Insufficient evidence — default to intuitive override")
            corrections.append("Activate intuitive thinker as primary decision signal")

        if empath_score >= 0.90 and analyst_score <= 0.40:
            alerts.append("SYCOPHANCY RISK: Empathy overriding analytical rigour")
            corrections.append("Balance human cost against evidence quality")

        if cognitive_tension <= 0.15:
            alerts.append("GROUPTHINK DETECTED: All personas agree too easily — activate absurdist")
            corrections.append("Force absurdist lateral leap; reject premature consensus")

        metacog_alert_level = min(1.0, len(alerts) * 0.30)

        return {
            "persona": "metacognition_monitor",
            "emotional_charge": -metacog_alert_level * 0.50,
            "cognitive_tension": round(cognitive_tension, 3),
            "metacognition_alert_level": round(metacog_alert_level, 3),
            "bias_alerts": alerts,
            "corrections_applied": corrections,
            "tension_label": "CREATIVE_PRESSURE" if cognitive_tension >= 0.40 else "PRODUCTIVE" if cognitive_tension >= 0.15 else "GROUPTHINK_RISK",
            "composite_score": round(1.0 - metacog_alert_level, 3),
            "core_insight": f"{len(alerts)} bias alerts. Cognitive tension: {cognitive_tension:.2f} ({('HIGH=CREATIVE' if cognitive_tension>=0.4 else 'LOW=RISK')}).",
            "action": "Apply corrections above. High tension is healthy — it means personas are thinking independently."
        }
