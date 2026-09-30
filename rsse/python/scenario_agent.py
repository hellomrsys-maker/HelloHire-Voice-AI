"""
scenario_agent.py - Recruitment Scenario Simulation Engine (RSSE) Python Sub-Agent.

Coordinates dynamic scenario execution, STAR method structural parsing,
register compliance scoring, and zero-bridge AMSV synchronization.
"""

from __future__ import annotations
import re
import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .verbal_sub_ai_neural import RecruitmentVerbalSubAINeural

@dataclass
class StarEvaluation:
    situation_score: float = 0.0
    task_score: float = 0.0
    action_score: float = 0.0
    result_score: float = 0.0
    overall_star_coherence: float = 0.0
    identified_elements: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class TurnEvaluation:
    turn_id: int
    transcript: str
    wpm: float
    register_compliance: float
    star_eval: Optional[StarEvaluation]
    stress_multiplier: float
    next_prompt: str
    phase_name: str
    neural_eval: Optional[Dict[str, Any]] = None

class RecruitmentScenarioAgent:
    """
    Sub-Agent managing enterprise interview simulations across 8 formats.
    """

    FORMAT_NAMES = {
        1: "Technical Interview",
        2: "Behavioral Interview (STAR)",
        3: "Competency-Based Interview",
        4: "Case Study / Business Case",
        5: "Group Discussion",
        6: "HR Screening",
        7: "Executive Leadership",
        8: "Multi-Examiner Panel"
    }

    PHASES = [
        "WarmupIntroduction",
        "CoreExploration",
        "DepthProbing",
        "StressChallenge",
        "SynthesisDebrief",
        "Concluded"
    ]

    def __init__(self, amsv_state_vector: Optional[memoryview] = None):
        self.amsv_view = amsv_state_vector
        self.active_format: int = 1
        self.active_scenario_id: int = 101
        self.current_turn: int = 0
        self.current_phase_idx: int = 0
        self.stress_multiplier: float = 1.0
        self.history: List[TurnEvaluation] = []
        self.neural_verbal_sub_ai = RecruitmentVerbalSubAINeural()

        # Jargon lexicons by format
        self.jargon_lexicons: Dict[int, List[str]] = {
            1: ["raft", "paxos", "rdma", "kernel-bypass", "dpdk", "linearizability", "cache-coherency", "latency", "throughput", "consensus"],
            2: ["situation", "task", "action", "result", "incident", "triage", "post-mortem", "blast radius", "sla", "containment"],
            3: ["trade-off", "matrix", "opportunity cost", "debt", "arr", "prioritization", "stakeholder", "alignment", "governance"],
            4: ["mece", "unit economics", "tam", "capex", "opex", "ltv", "cac", "margin", "contribution", "depreciation"],
            5: ["consensus", "interoperability", "bridging", "alignment", "active listening", "buy-in", "friction", "synthesis"],
            6: ["culture", "values", "growth mindset", "ethics", "ambiguity", "mentorship", "work ethic", "resilience"],
            7: ["capital allocation", "sovereign", "governance", "roic", "asymmetric", "board", "defensive posture", "moat"],
            8: ["zero-trust", "multi-tenant", "carrier-grade", "reconciliation", "trade-off", "sla", "prudence", "canary"]
        }

    def start_scenario(self, format_code: int = 1, scenario_id: int = 101) -> str:
        self.active_format = format_code if 1 <= format_code <= 8 else 1
        self.active_scenario_id = scenario_id
        self.current_turn = 0
        self.current_phase_idx = 0
        self.stress_multiplier = 1.0
        self.history.clear()

        prompt = self._get_opening_prompt(self.active_format)
        self._sync_to_amsv(register_comp=1.0)
        return prompt

    def evaluate_turn(self, transcript: str, wpm: float = 135.0) -> TurnEvaluation:
        self.current_turn += 1
        
        # 1. Register compliance (heuristic)
        heuristic_comp = self._calculate_register_compliance(transcript, wpm)

        # 2. Neural verbal Transformer evaluation
        neural_res = self.neural_verbal_sub_ai.analyze_verbal_response(
            transcript, format_code=self.active_format, wpm=wpm
        )
        neural_comp = neural_res["register_compliance_score"]

        # 3. Fused register compliance (0.6 neural + 0.4 heuristic)
        reg_comp = float(min(1.0, max(0.0, 0.6 * neural_comp + 0.4 * heuristic_comp)))

        # 4. STAR evaluation if behavioral or competency
        star_eval = None
        if self.active_format in (2, 3):
            star_eval = self._evaluate_star_structure(transcript)
            # Blend neural STAR coherence
            star_eval.overall_star_coherence = float(
                min(1.0, max(0.0, 0.6 * neural_res["star_coherence_score"] + 0.4 * star_eval.overall_star_coherence))
            )

        # 5. Dynamic phase advancement
        self._advance_phase()

        # 6. Stress adaptation
        if reg_comp > 0.75:
            self.stress_multiplier = min(2.0, self.stress_multiplier * 1.1)
        elif reg_comp < 0.40:
            self.stress_multiplier = max(0.5, self.stress_multiplier * 0.9)

        # 7. Next prompt generation
        next_prompt = self._generate_next_probe(reg_comp)

        # 8. Synchronize with AMSV (Offset 0x20)
        self._sync_to_amsv(register_comp=reg_comp)

        turn_eval = TurnEvaluation(
            turn_id=self.current_turn,
            transcript=transcript,
            wpm=wpm,
            register_compliance=round(reg_comp, 4),
            star_eval=star_eval,
            stress_multiplier=self.stress_multiplier,
            next_prompt=next_prompt,
            phase_name=self.PHASES[self.current_phase_idx],
            neural_eval=neural_res
        )
        self.history.append(turn_eval)
        return turn_eval

    def _calculate_register_compliance(self, text: str, wpm: float) -> float:
        if not text or len(text.strip()) == 0:
            return 0.0

        words = text.lower().split()
        if len(words) < 5:
            return 0.2

        # Jargon match
        lexicon = self.jargon_lexicons.get(self.active_format, [])
        jargon_count = sum(1 for j in lexicon if j in text.lower())
        jargon_score = min(1.0, (jargon_count / max(1, len(lexicon) * 0.3)))

        # WPM penalty
        target_wpm = 135.0
        wpm_error = abs(wpm - target_wpm) / target_wpm
        wpm_score = max(0.0, 1.0 - wpm_error)

        # Hedging penalty
        hedges = ["maybe", "perhaps", "i think", "i guess", "sort of", "kind of", "um", "uh"]
        hedge_count = sum(1 for h in hedges if h in text.lower())
        hedge_penalty = min(0.5, hedge_count * 0.08)
        hedge_score = max(0.0, 1.0 - hedge_penalty)

        compliance = (jargon_score * 0.45) + (wpm_score * 0.35) + (hedge_score * 0.20)
        return float(min(1.0, max(0.0, compliance)))

    def _evaluate_star_structure(self, text: str) -> StarEvaluation:
        lower = text.lower()
        star = StarEvaluation()
        
        situation_markers = ["when", "during", "at", "while", "context", "background", "company", "system had"]
        task_markers = ["tasked with", "responsible for", "my goal", "objective", "needed to", "required to"]
        action_markers = ["i designed", "i implemented", "i led", "i decided", "i analyzed", "i resolved", "i initiated"]
        result_markers = ["resulted in", "achieved", "reduced by", "increased by", "saved", "delivered", "outcome was"]

        s_matches = [m for m in situation_markers if m in lower]
        t_matches = [m for m in task_markers if m in lower]
        a_matches = [m for m in action_markers if m in lower]
        r_matches = [m for m in result_markers if m in lower]

        star.situation_score = min(1.0, len(s_matches) * 0.7)
        star.task_score = min(1.0, len(t_matches) * 0.7)
        star.action_score = min(1.0, len(a_matches) * 0.6)
        star.result_score = min(1.0, len(r_matches) * 0.7)

        star.overall_star_coherence = (
            star.situation_score * 0.20 +
            star.task_score * 0.20 +
            star.action_score * 0.35 +
            star.result_score * 0.25
        )
        star.identified_elements = {
            "situation": s_matches,
            "task": t_matches,
            "action": a_matches,
            "result": r_matches
        }
        return star

    def _advance_phase(self) -> None:
        if self.current_turn >= 6:
            self.current_phase_idx = 5 # Concluded
        elif self.current_turn >= 5:
            self.current_phase_idx = 4 # SynthesisDebrief
        elif self.current_turn >= 3:
            self.current_phase_idx = 3 # StressChallenge
        elif self.current_turn >= 2:
            self.current_phase_idx = 2 # DepthProbing
        elif self.current_turn >= 1:
            self.current_phase_idx = 1 # CoreExploration
        else:
            self.current_phase_idx = 0 # WarmupIntroduction

    def _generate_next_probe(self, reg_comp: float) -> str:
        phase = self.PHASES[self.current_phase_idx]
        if phase == "DepthProbing":
            return f"Can you detail the exact quantitative trade-offs and architecture choices in your previous statement?"
        elif phase == "StressChallenge":
            return f"A severe catastrophic regression just occurred under that exact architecture. How do you defend your choice?"
        elif phase == "SynthesisDebrief":
            return f"Summarize your key insights and recommendations into a concise executive briefing."
        elif phase == "Concluded":
            return f"The simulation has concluded. Final evaluation is being generated."
        else:
            return f"Please proceed with the core details of your proposal."

    def _get_opening_prompt(self, format_code: int) -> str:
        prompts = {
            1: "Technical Architecture: Design an ultra-low-latency distributed consensus cluster handling 10M tx/sec with sub-50us p99 latency.",
            2: "Behavioral Incident: Walk me through a catastrophic production outage where key leaders were unavailable using STAR.",
            3: "Competency Alignment: How do you reconcile a sales demand for immediate feature delivery against critical tech debt refactoring?",
            4: "Case Study: Evaluate the market entry of 5,000 autonomous delivery vehicles into Germany, detailing unit economics.",
            5: "Group Consensus: Synthesize agreement across clinicians and vendor-backed executives on a 42-hospital health record system.",
            6: "HR Screening: Why our firm, why this practice, and what ethical philosophy guides you through intense ambiguity?",
            7: "Executive Leadership: Present your 5-year capital allocation and sovereign defense AI roadmap for our $250M fund.",
            8: "Panel Defense: Address conflicting mandates from the CFO, CSO, and COO regarding your $1.2B network modernization."
        }
        return prompts.get(format_code, prompts[1])

    def _sync_to_amsv(self, register_comp: float) -> None:
        if self.amsv_view is None:
            return

        # RSSE state is stored at byte offset 0x20 (32) in AMSV AtomicStateVector (8 bytes uint64)
        # [Bits 0-15: scenario_id | Bits 16-31: turn | Bits 32-47: comp Q16 | Bits 48-63: phase]
        comp_q16 = int(max(0.0, min(1.0, register_comp)) * 65535)
        phase_code = self.current_phase_idx + 1
        packed_u64 = (
            (self.active_scenario_id & 0xFFFF) |
            ((self.current_turn & 0xFFFF) << 16) |
            ((comp_q16 & 0xFFFF) << 32) |
            ((phase_code & 0xFFFF) << 48)
        )
        struct.pack_into("<Q", self.amsv_view, 32, packed_u64)
