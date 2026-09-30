"""
ecse_orchestrator.py — Emotional Communication & Social Calibration Engine Master Orchestrator

Coordinates 5 ECSE Sub-AIs:
  1. AffectValenceAI       — positive/negative/neutral emotional tone detection
  2. RapportBuildingAI     — warmth, collective identity, bonding language
  3. MirrorMatchingAI      — vocabulary & rhythm mirroring of interviewer
  4. MicroDisagreementAI   — hedges, face-saving, silent resistance signals
  5. PolitenessRegisterAI  — formal/informal calibration, courtesy markers

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into into the 64-byte AMSV physical buffer at offset 0x20.
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from ecse.python.sub_ais.affect_valence_ai import AffectValenceAI
from ecse.python.sub_ais.rapport_building_ai import RapportBuildingAI
from ecse.python.sub_ais.mirror_matching_ai import MirrorMatchingAI
from ecse.python.sub_ais.micro_disagreement_ai import MicroDisagreementAI
from ecse.python.sub_ais.politeness_register_ai import PolitenessRegisterAI


class EmotionalCommunicationSocialOrchestrator:
    """
    Coordinates real-time social intelligence, affect valence, rapport formation,
    conversational mirroring, diplomatic tact, and polite register calibration.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None, amsv_offset: int = 0x10):
        self.affect_ai     = AffectValenceAI()
        self.rapport_ai    = RapportBuildingAI()
        self.mirror_ai     = MirrorMatchingAI()
        self.disagree_ai   = MicroDisagreementAI()
        self.politeness_ai = PolitenessRegisterAI()
        self.amsv_buffer   = master_amsv_buffer
        self.amsv_offset   = amsv_offset
        self.history: List[str] = []

    def evaluate_turn(
        self,
        answer: str,
        interviewer_last_turn: str = "",
        turn_number: int = 1,
        candidate_wpm: float = 145.0,
        interviewer_wpm: float = 140.0
    ) -> Dict[str, Any]:
        affect     = self.affect_ai.evaluate(answer)
        rapport    = self.rapport_ai.evaluate(answer)
        mirror     = self.mirror_ai.evaluate(answer, interviewer_last_turn, candidate_wpm, interviewer_wpm)
        disagree   = self.disagree_ai.evaluate(answer)
        politeness = self.politeness_ai.evaluate(answer)

        gsi = (
            affect["composite_score"]     * 0.22 +
            rapport["composite_score"]    * 0.25 +
            mirror["composite_score"]     * 0.20 +
            disagree["composite_score"]   * 0.15 +
            politeness["composite_score"] * 0.18
        )
        gsi = min(1.0, max(0.0, gsi))

        if   gsi >= 0.80: grade, label = 1, "HIGHLY_ATTUNED"
        elif gsi >= 0.63: grade, label = 2, "CALIBRATED"
        elif gsi >= 0.45: grade, label = 3, "ADEQUATE"
        else:             grade, label = 4, "MISALIGNED"

        self.history.append(answer)

        report = {
            "turn": turn_number,
            "global_social_intelligence": round(gsi, 3),
            "social_grade": grade,
            "social_label": label,
            "dimensions": {
                "affect": affect,
                "rapport": rapport,
                "mirror": mirror,
                "micro_disagreement": disagree,
                "politeness": politeness
            }
        }
        self._sync_amsv(report, turn_number)
        return report

    def _sync_amsv(self, report: Dict[str, Any], turn: int) -> None:
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return
        def q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        d = report["dimensions"]
        # ECSE partition is 0x20..0x27 (8 bytes)
        # Offset 0x20: [affect_q16 (2B) | rapport_q16 (2B) | mirror_q16 (2B) | politeness_q16 (2B)]
        struct.pack_into(
            "<HHHH",
            self.amsv_buffer,
            self.amsv_offset,
            q16(d["affect"]["composite_score"]),
            q16(d["rapport"]["composite_score"]),
            q16(d["mirror"]["composite_score"]),
            q16(d["politeness"]["composite_score"])
        )
