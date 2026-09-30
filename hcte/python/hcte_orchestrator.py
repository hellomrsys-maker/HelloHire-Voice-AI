"""
hcte_orchestrator.py — Human Cognitive Thinking Engine Master Orchestrator

Fires all 11 cognitive personas in parallel, synthesizes their outputs
via dynamic weighted voting, and writes the result to the AMSV buffer.

Zero-Bridge Synchronous Memory:
  AMSV offset 0x38: [optimism_charge | pessimism_index | cognitive_tension | solution_density]
"""
from __future__ import annotations
import struct
import concurrent.futures
from typing import Dict, Any, Optional

from hcte.python.sub_ais.optimist_thinker import OptimistThinker
from hcte.python.sub_ais.pessimist_thinker import PessimistThinker
from hcte.python.sub_ais.premortem_analyst import PreMortemAnalyst
from hcte.python.sub_ais.devils_advocate import DevilsAdvocate
from hcte.python.sub_ais.analyst_thinker import AnalystThinker, IntuitiveThinker, EmpathThinker
from hcte.python.sub_ais.systems_thinker import (
    SystemsThinker, VisionaryThinker, AbsurdistThinker, MetacognitionMonitor
)

# Dynamic synthesis weights (sum = 1.0)
# Pre-Mortem gets 2× base weight — negative thinking is the most valuable
PERSONA_WEIGHTS = {
    "optimist":          0.08,
    "pessimist":         0.10,
    "premortem_analyst": 0.18,  # 2× boost
    "devils_advocate":   0.10,
    "analyst":           0.12,
    "intuitive":         0.08,
    "empath":            0.08,
    "systems_thinker":   0.10,
    "visionary":         0.07,
    "absurdist":         0.05,
    "metacognition_monitor": 0.04,  # monitor adjusts weights, not synthesis score
}

LABEL_THRESHOLDS = {
    (0.75, 1.00): "HIGHLY_INSIGHTFUL",
    (0.55, 0.75): "INSIGHTFUL",
    (0.35, 0.55): "ADEQUATE",
    (0.00, 0.35): "SHALLOW",
}

def _label(score: float) -> str:
    for (lo, hi), label in LABEL_THRESHOLDS.items():
        if lo <= score < hi:
            return label
    return "ADEQUATE"


class HumanCognitiveThinkingOrchestrator:
    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.optimist   = OptimistThinker()
        self.pessimist  = PessimistThinker()
        self.premortem  = PreMortemAnalyst()
        self.devil      = DevilsAdvocate()
        self.analyst    = AnalystThinker()
        self.intuitive  = IntuitiveThinker()
        self.empath     = EmpathThinker()
        self.systems    = SystemsThinker()
        self.visionary  = VisionaryThinker()
        self.absurdist  = AbsurdistThinker()
        self.metacog    = MetacognitionMonitor()
        self.amsv_buffer = master_amsv_buffer

    def think(self, scenario: str) -> Dict[str, Any]:
        """
        Fire all 11 personas in parallel, synthesize, and write to AMSV.
        Returns the full master cognitive output.
        """
        # ── Parallel persona execution ─────────────────────────────────────
        with concurrent.futures.ThreadPoolExecutor(max_workers=11) as pool:
            futures = {
                "optimist":          pool.submit(self.optimist.think,  scenario),
                "pessimist":         pool.submit(self.pessimist.think, scenario),
                "premortem_analyst": pool.submit(self.premortem.think, scenario),
                "devils_advocate":   pool.submit(self.devil.think,     scenario),
                "analyst":           pool.submit(self.analyst.think,   scenario),
                "intuitive":         pool.submit(self.intuitive.think, scenario),
                "empath":            pool.submit(self.empath.think,    scenario),
                "systems_thinker":   pool.submit(self.systems.think,   scenario),
                "visionary":         pool.submit(self.visionary.think, scenario),
                "absurdist":         pool.submit(self.absurdist.think, scenario),
            }
            persona_outputs = {name: fut.result() for name, fut in futures.items()}

        # ── Metacognition runs AFTER all others (needs their outputs) ──────
        metacog_output = self.metacog.monitor(persona_outputs)
        persona_outputs["metacognition_monitor"] = metacog_output

        # ── Dynamic synthesis ──────────────────────────────────────────────
        cognitive_tension = metacog_output.get("cognitive_tension", 0.30)

        # If groupthink detected, boost absurdist weight
        weights = dict(PERSONA_WEIGHTS)
        if cognitive_tension < 0.15:
            weights["absurdist"]    = weights.get("absurdist", 0.05) + 0.10
            weights["devils_advocate"] += 0.05

        total_w = sum(weights[k] for k in persona_outputs if k in weights)
        gci = sum(
            persona_outputs[name].get("composite_score", 0.5) * weights.get(name, 0.05)
            for name in persona_outputs
            if name in weights
        ) / max(total_w, 0.01)

        # Pessimism index (from pessimist + premortem combined)
        pessimism_index = (
            persona_outputs["pessimist"].get("composite_score", 0.3) * 0.40 +
            persona_outputs["premortem_analyst"].get("pessimism_index", 0.3) * 0.60
        )

        # Solution coverage from pre-mortem
        solution_density = persona_outputs["premortem_analyst"].get("solution_coverage", 0.5)

        # Optimism charge
        optimism_charge = persona_outputs["optimist"].get("composite_score", 0.5)

        master = {
            "global_cognitive_index": round(gci, 3),
            "cognitive_label": _label(gci),
            "pessimism_index": round(pessimism_index, 3),
            "optimism_charge": round(optimism_charge, 3),
            "cognitive_tension": round(cognitive_tension, 3),
            "solution_density": round(solution_density, 3),
            "tension_label": metacog_output.get("tension_label", "PRODUCTIVE"),
            "bias_alerts": metacog_output.get("bias_alerts", []),
            "worst_case": persona_outputs["premortem_analyst"].get("worst_case", {}),
            "personas": persona_outputs,
        }

        if self.amsv_buffer is not None:
            self._sync_amsv(optimism_charge, pessimism_index, cognitive_tension, solution_density)

        return master

    def _sync_amsv(self, optimism: float, pessimism: float,
                   tension: float, solution_density: float) -> None:
        """Zero-Bridge write to AMSV offset 0x38 (HCTE region)."""
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        # Offset 0x38: [optimism_charge | pessimism_index | cognitive_tension | solution_density]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x38,
                         to_q16(optimism), to_q16(pessimism),
                         to_q16(tension), to_q16(solution_density))
