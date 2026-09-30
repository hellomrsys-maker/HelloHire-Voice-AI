"""
premortem_analyst.py — Persona 3: The Pre-Mortem Analyst (HCTE) ← Crown Jewel

The most powerful negative-thinking machine in the system.
Uses Failure Mode & Effects Analysis (FMEA) + Pre-Mortem Analysis.

Algorithm:
  Step 1: Generate worst-case failure modes from the scenario
  Step 2: Score each by Severity × Probability × (1 - Detectability) = RPN
  Step 3: Trace the causal chain leading to each failure
  Step 4: Generate early warning signals + prevention measures + recovery plans
  Step 5: Compute Pessimism Index and Solution Coverage
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class FailureMode:
    name: str
    severity: float          # 1-10 (10=catastrophic)
    probability: float       # 0.0-1.0
    detectability: float     # 0.0-1.0 (higher=easier to detect early)
    rpn: float = 0.0         # Risk Priority Number = severity * probability * (1-detectability)
    causal_chain: List[str] = field(default_factory=list)
    early_warnings: List[str] = field(default_factory=list)
    prevention_measures: List[str] = field(default_factory=list)
    recovery_plans: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.rpn = self.severity * self.probability * (1.0 - self.detectability)


class PreMortemAnalyst:
    """
    "Assume we already failed. Why did it happen? How do we prevent it next time?"
    This is how military generals, NASA engineers, and top investors think.
    """

    FAILURE_TRIGGERS = {
        "scope_creep":       ("Scope expanded beyond original plan", 7.0, 0.65, 0.40),
        "key_person_loss":   ("Critical team member or stakeholder exits", 8.5, 0.30, 0.35),
        "resource_shortage": ("Budget or resource constraints hit before completion", 7.5, 0.50, 0.55),
        "communication_failure": ("Misalignment between key stakeholders causes derailment", 6.5, 0.45, 0.40),
        "technical_debt":    ("Hidden complexity or technical debt surfaces at critical phase", 7.0, 0.55, 0.30),
        "market_shift":      ("External market or context changes invalidate the approach", 8.0, 0.25, 0.20),
        "assumption_failure":("Core underlying assumption turns out to be false", 9.0, 0.35, 0.25),
        "timeline_slip":     ("Delivery date slips causing downstream cascade failures", 6.0, 0.60, 0.60),
        "quality_collapse":  ("Rushed execution leads to critical quality failure", 7.5, 0.40, 0.45),
        "dependency_risk":   ("Third-party dependency fails or becomes unavailable", 7.0, 0.30, 0.35),
    }

    PREVENTION_MAP = {
        "scope_creep":       ["Define and lock requirements early", "Weekly scope review gates", "Change control board"],
        "key_person_loss":   ["Document all critical knowledge", "Cross-train backup roles", "Succession plan ready"],
        "resource_shortage": ["Buffer 20% contingency into all estimates", "Identify alternative resource pools", "Phased delivery to reduce commitment risk"],
        "communication_failure": ["Weekly aligned stakeholder sync", "RACI matrix defined upfront", "Written confirmations for all decisions"],
        "technical_debt":    ["Architecture review before build phase", "Spike to validate core assumptions", "Dedicated refactor sprints"],
        "market_shift":      ["Monthly market signal reviews", "Build modular pivotable architecture", "6-month horizon planning cycles"],
        "assumption_failure":["List all assumptions explicitly", "Test top 3 assumptions first", "Assumption invalidation kills decision tree"],
        "timeline_slip":     ["Identify critical path and protect it", "Buffer slack into milestones", "Early warning: >10% slip triggers escalation"],
        "quality_collapse":  ["Non-negotiable quality gates per milestone", "Automated testing from Day 1", "Zero-defect policy on critical path items"],
        "dependency_risk":   ["Map all 3rd-party dependencies", "Identify alternatives for each", "Build abstraction layer to swap dependencies"],
    }

    RECOVERY_MAP = {
        "scope_creep":       "Invoke formal change freeze; negotiate MVP reduction with stakeholders.",
        "key_person_loss":   "Activate backup role; reallocate timeline; consider specialist contractor.",
        "resource_shortage": "Ruthlessly prioritize core deliverables; negotiate phase delivery.",
        "communication_failure": "Immediate all-hands reset; appoint single decision-maker; restart RACI.",
        "technical_debt":    "Declare technical debt sprint; halt feature development until resolved.",
        "market_shift":      "Execute pivot protocol; validate new direction with fast experiments.",
        "assumption_failure":"Convene emergency assumption review; rebuild plan on validated foundation.",
        "timeline_slip":     "Activate parallel workstreams; negotiate scope reduction with sponsor.",
        "quality_collapse":  "Halt and fix; quality debt always costs more later than now.",
        "dependency_risk":   "Invoke pre-built alternative; negotiate SLA with dependency provider.",
    }

    def think(self, scenario: str) -> Dict[str, Any]:
        failure_modes = self._generate_failure_modes(scenario)

        # Score and rank by RPN (highest risk first)
        failure_modes.sort(key=lambda fm: -fm.rpn)

        # Populate causal chains and solutions
        for fm in failure_modes:
            fm.causal_chain     = self._trace_causation(fm)
            fm.early_warnings   = self._find_early_warnings(fm)
            fm.prevention_measures = self.PREVENTION_MAP.get(fm.name, ["Implement monitoring", "Build contingency plan"])
            fm.recovery_plans   = [self.RECOVERY_MAP.get(fm.name, "Escalate immediately and assess options.")]

        worst = failure_modes[0] if failure_modes else None
        pessimism_index = self._compute_pessimism_index(failure_modes)
        solution_coverage = self._compute_solution_coverage(failure_modes)

        return {
            "persona": "premortem_analyst",
            "emotional_charge": -pessimism_index,  # deeply negative
            "pessimism_index": round(pessimism_index, 3),
            "solution_coverage": round(solution_coverage, 3),
            "failure_mode_count": len(failure_modes),
            "worst_case": {
                "name": worst.name if worst else "none",
                "rpn": round(worst.rpn, 2) if worst else 0,
                "severity": worst.severity if worst else 0,
                "probability": worst.probability if worst else 0,
                "causal_chain": worst.causal_chain if worst else [],
                "early_warnings": worst.early_warnings if worst else [],
                "prevention": worst.prevention_measures if worst else [],
                "recovery": worst.recovery_plans if worst else [],
            },
            "all_failure_modes": [
                {"name": fm.name, "rpn": round(fm.rpn, 2),
                 "severity": fm.severity, "probability": fm.probability}
                for fm in failure_modes[:5]
            ],
            "core_insight": f"Pre-mortem: {len(failure_modes)} failure pathways. Worst: {worst.name if worst else 'N/A'} (RPN={round(worst.rpn,1) if worst else 0})",
            "action": "Address top-RPN failure mode before proceeding. Solution coverage: {:.0%}".format(solution_coverage)
        }

    def _generate_failure_modes(self, scenario: str) -> List[FailureMode]:
        """Select relevant failure modes based on scenario keywords."""
        l = scenario.lower()
        modes = []
        keyword_map = {
            "scope_creep": ["scope","feature","requirement","expand","add more"],
            "key_person_loss": ["team","person","leader","depend","solo","key"],
            "resource_shortage": ["budget","cost","resource","money","fund","time"],
            "communication_failure": ["stakeholder","align","meeting","decision","approval"],
            "technical_debt": ["code","system","architecture","technical","legacy"],
            "market_shift": ["market","customer","competitor","external","trend"],
            "assumption_failure": ["assume","believe","expect","plan","strategy"],
            "timeline_slip": ["deadline","schedule","date","delivery","sprint","launch"],
            "quality_collapse": ["quality","test","bug","defect","review","production"],
            "dependency_risk": ["third","vendor","api","library","dependency","external"],
        }
        for name, kws in keyword_map.items():
            if any(kw in l for kw in kws):
                sev, prob, det = self.FAILURE_TRIGGERS[name][1:]
                modes.append(FailureMode(name, sev, prob, det))

        # Always include the top 3 most universal failure modes as baseline
        universal = ["assumption_failure", "communication_failure", "timeline_slip"]
        existing = {m.name for m in modes}
        for u in universal:
            if u not in existing:
                sev, prob, det = self.FAILURE_TRIGGERS[u][1:]
                modes.append(FailureMode(u, sev, prob, det))

        return modes

    def _trace_causation(self, fm: FailureMode) -> List[str]:
        chains = {
            "scope_creep": ["New requests accepted informally", "No formal change process", "Scope expands silently", "Timeline and budget overrun"],
            "key_person_loss": ["Single-point-of-failure dependency", "No knowledge transfer", "Departure creates knowledge vacuum", "Project stalls or fails"],
            "assumption_failure": ["Core assumption stated but untested", "Plan built on assumed truth", "Assumption invalidated by reality", "Entire plan requires rebuild"],
            "communication_failure": ["Key decision made without all stakeholders", "Conflicting interpretations emerge", "Teams execute different visions", "Integration reveals misalignment"],
            "timeline_slip": ["Estimates not buffered for unknowns", "Early delays not escalated", "Critical path compromised", "Final delivery misses deadline with cascading effects"],
        }
        return chains.get(fm.name, [f"Root condition → {fm.name} trigger → Impact → Consequence"])

    def _find_early_warnings(self, fm: FailureMode) -> List[str]:
        warnings = {
            "scope_creep": ["Informal feature requests increasing", "Meeting notes showing expanding objectives"],
            "key_person_loss": ["Key person disengaged in meetings", "Reduced commit/contribution frequency"],
            "assumption_failure": ["Data contradicting core assumption appearing", "Stakeholders questioning the foundation"],
            "communication_failure": ["Repeated re-explanations needed", "Decisions being revisited frequently"],
            "timeline_slip": ["Milestone slip of >10%", "Task estimates consistently exceeded"],
        }
        return warnings.get(fm.name, ["Increase in unresolved issues", "Team morale indicators declining"])

    def _compute_pessimism_index(self, failure_modes: List[FailureMode]) -> float:
        if not failure_modes:
            return 0.10
        avg_rpn = sum(fm.rpn for fm in failure_modes) / len(failure_modes)
        # Normalise: RPN of 15 maps to 1.0 (adjusted from 50 — real-world RPNs average 2-8)
        return min(1.0, max(0.05, avg_rpn / 15.0))

    def _compute_solution_coverage(self, failure_modes: List[FailureMode]) -> float:
        if not failure_modes:
            return 1.0
        covered = sum(1 for fm in failure_modes if fm.prevention_measures and fm.recovery_plans)
        return covered / len(failure_modes)
