"""
nace_orchestrator.py — Narrative Arc & Coherence Engine Master Orchestrator

Coordinates 4 NACE sub-AIs:
  1. ContradictionDetectorAI — cross-turn contradiction analysis & factual consistency
  2. ThemeConsistencyAI      — professional identity stability across turns
  3. NarrativeClimaxAI       — signature stories, STAR structure, quantifiable impact
  4. ArcMomentumAI           — narrative velocity and forward drive

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into at AMSV physical offset 0x34 (4 bytes):
  [coherence_q16 | climax_q16]
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from nace.python.sub_ais.contradiction_detector_ai import ContradictionDetectorAI
from nace.python.sub_ais.theme_consistency_ai import ThemeConsistencyAI
from nace.python.sub_ais.narrative_climax_ai import NarrativeClimaxAI
from nace.python.sub_ais.arc_momentum_ai import ArcMomentumAI


class NarrativeArcCoherenceOrchestrator:
    """
    Evaluates whether the candidate's responses tell a coherent, consistent,
    and compelling narrative across multiple turns.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.contradiction_ai = ContradictionDetectorAI()
        self.theme_ai         = ThemeConsistencyAI()
        self.climax_ai        = NarrativeClimaxAI()
        self.momentum_ai      = ArcMomentumAI()
        self.amsv_buffer      = master_amsv_buffer
        self.turn_history: List[Dict[str, Any]] = []

    def evaluate_turn(self, turn_number: int, answer: str) -> Dict[str, Any]:
        """
        Evaluates a single conversation turn in the context of the running narrative.
        """
        contra_res = self.contradiction_ai.evaluate(turn_number, answer)
        theme_res  = self.theme_ai.evaluate(answer)
        climax_res = self.climax_ai.evaluate(answer)
        moment_res = self.momentum_ai.evaluate(answer)

        # Narrative Coherence Index (NCI)
        # Weights: Contradiction consistency (0.40), Theme stability (0.25), Climax structure (0.20), Momentum (0.15)
        nci = (
            contra_res["coherence_score"]    * 0.40 +
            theme_res["theme_stability_score"] * 0.25 +
            climax_res["climax_score"]        * 0.20 +
            moment_res["momentum_score"]      * 0.15
        )
        nci = min(1.0, max(0.0, nci))

        if nci >= 0.80:
            tier = "EXEMPLARY"
        elif nci >= 0.60:
            tier = "COHERENT"
        elif nci >= 0.40:
            tier = "FRAGMENTED"
        else:
            tier = "CONTRADICTORY"

        report = {
            "turn": turn_number,
            "narrative_coherence_index": round(nci, 3),
            "coherence_tier": tier,
            "coherence_score": contra_res["coherence_score"],
            "theme_stability": theme_res["theme_stability_score"],
            "climax_score": climax_res["climax_score"],
            "momentum_score": moment_res["momentum_score"],
            "has_contradictions": contra_res["has_contradictions"],
            "has_star_structure": climax_res["has_star_structure"],
            "details": {
                "contradictions": contra_res,
                "theme": theme_res,
                "climax": climax_res,
                "momentum": moment_res
            }
        }

        self.turn_history.append(report)

        if self.amsv_buffer is not None:
            self._sync_amsv(coherence=contra_res["coherence_score"], climax=climax_res["climax_score"])

        return report

    def _sync_amsv(self, coherence: float, climax: float) -> None:
        """
        Direct Zero-Bridge physical write into AMSV buffer at offset 0x34 (4 bytes).
        Format: <HH -> [coherence_q16, climax_q16].
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        struct.pack_into("<HH", self.amsv_buffer, 0x34,
                         to_q16(coherence),
                         to_q16(climax))
