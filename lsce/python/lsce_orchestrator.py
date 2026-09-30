"""
lsce_orchestrator.py — Long-Short Cognitive Endurance Engine Master Orchestrator

Coordinates 4 LSCE sub-AIs:
  1. FatigueTrajectoryAI      — monitors trajectory slope and answer volume degradation
  2. LexicalDiversityDriftAI  — tracks Type-Token Ratio (TTR) and vocabulary narrowing
  3. ConcentrationResilienceAI— evaluates focus on complex multi-part questions
  4. EnduranceRecoveryAI      — tracks rebound velocity after challenging turns

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into at AMSV physical offset 0x3C (2 bytes):
  [stamina_q16] (leaves 0x3E for PACE adaptation).
"""

from __future__ import annotations
import struct
from typing import Dict, Any, Optional

from lsce.python.sub_ais.fatigue_trajectory_ai import FatigueTrajectoryAI
from lsce.python.sub_ais.lexical_diversity_drift_ai import LexicalDiversityDriftAI
from lsce.python.sub_ais.concentration_resilience_ai import ConcentrationResilienceAI
from lsce.python.sub_ais.endurance_recovery_ai import EnduranceRecoveryAI


class CognitiveEnduranceOrchestrator:
    """
    Evaluates candidate stamina, focus retention, and resilience across prolonged interview sessions.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.trajectory_ai   = FatigueTrajectoryAI()
        self.diversity_ai    = LexicalDiversityDriftAI()
        self.resilience_ai   = ConcentrationResilienceAI()
        self.recovery_ai     = EnduranceRecoveryAI()
        self.amsv_buffer     = master_amsv_buffer

    def evaluate_turn(self, question: str, answer: str, turn_quality_hint: float = 0.70) -> Dict[str, Any]:
        traj_res    = self.trajectory_ai.evaluate(answer)
        div_res     = self.diversity_ai.evaluate(answer)
        resil_res   = self.resilience_ai.evaluate(question, answer)
        recov_res   = self.recovery_ai.evaluate(turn_quality_hint)

        # Endurance Index (EI)
        # Weights: Stamina from trajectory (0.35), Lexical Richness (0.25), Concentration Resilience (0.25), Recovery (0.15)
        ei = (
            traj_res["stamina_score"]         * 0.35 +
            div_res["lexical_richness"]       * 0.25 +
            resil_res["resilience_score"]     * 0.25 +
            recov_res["recovery_score"]       * 0.15
        )
        ei = min(1.0, max(0.0, ei))

        if ei >= 0.80:
            tier = "IRONCLAD"
        elif ei >= 0.60:
            tier = "RESILIENT"
        elif ei >= 0.40:
            tier = "MILD_FATIGUE"
        else:
            tier = "EXHAUSTED"

        report = {
            "endurance_index": round(ei, 3),
            "stamina_tier": tier,
            "stamina_score": traj_res["stamina_score"],
            "fatigue_index": traj_res["fatigue_index"],
            "lexical_richness": div_res["lexical_richness"],
            "resilience_score": resil_res["resilience_score"],
            "recovery_score": recov_res["recovery_score"],
            "is_fatiguing": traj_res["is_fatiguing"],
            "details": {
                "trajectory": traj_res,
                "diversity": div_res,
                "concentration": resil_res,
                "recovery": recov_res
            }
        }

        if self.amsv_buffer is not None:
            self._sync_amsv(traj_res["stamina_score"])

        return report

    def _sync_amsv(self, stamina: float) -> None:
        """
        Direct Zero-Bridge physical write into AMSV buffer at offset 0x3C (2 bytes).
        Format: <H -> [stamina_q16].
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        struct.pack_into("<H", self.amsv_buffer, 0x3C, to_q16(stamina))
