"""
alie_orchestrator.py — Active Listening Intelligence Engine Master Orchestrator

Coordinates all 4 ALIE sub-AIs:
  1. ReferenceAlignmentAI   — pronoun echo + topic frame retention
  2. QARelevanceAI          — on-topic ratio, specificity, completeness
  3. DiscourseRepairAI      — repair signals + comprehension acknowledgements
  4. CoreferenceTrackingAI  — entity persistence across turns

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into into the 64-byte AMSV physical buffer.
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from alie.python.sub_ais.reference_alignment_ai import ReferenceAlignmentAI
from alie.python.sub_ais.qa_relevance_ai import QARelevanceAI
from alie.python.sub_ais.discourse_repair_ai import DiscourseRepairAI
from alie.python.sub_ais.coreference_tracking_ai import CoreferenceTrackingAI

_LATENCY_OPT_LO = 800.0
_LATENCY_OPT_HI = 2200.0

def _latency_score(latency_ms: float) -> float:
    if _LATENCY_OPT_LO <= latency_ms <= _LATENCY_OPT_HI:
        return 1.0
    if latency_ms < 300.0:
        return 0.40
    if latency_ms < _LATENCY_OPT_LO:
        return max(0.40, 0.40 + (latency_ms / _LATENCY_OPT_LO) * 0.60)
    import math
    return max(0.10, math.exp(-0.00045 * (latency_ms - _LATENCY_OPT_HI)))


class ActiveListeningIntelligenceOrchestrator:
    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.alignment_ai   = ReferenceAlignmentAI()
        self.relevance_ai   = QARelevanceAI()
        self.repair_ai      = DiscourseRepairAI()
        self.coref_ai       = CoreferenceTrackingAI()
        self.amsv_buffer    = master_amsv_buffer
        self.history: List[str] = []

    def evaluate_turn(
        self,
        question: str,
        answer: str,
        turn_number: int,
        latency_ms: float = 1200.0,
        question_was_ambiguous: bool = False
    ) -> Dict[str, Any]:
        alignment = self.alignment_ai.evaluate(question, answer)
        relevance = self.relevance_ai.evaluate(question, answer)
        repair    = self.repair_ai.evaluate(answer, question_was_ambiguous)
        coref     = self.coref_ai.evaluate(answer, self.history)
        lat_score = _latency_score(latency_ms)

        # Global Listening Index
        gli = (
            alignment["composite_score"] * 0.25 +
            relevance["composite_score"] * 0.30 +
            lat_score                    * 0.15 +
            repair["composite_score"]    * 0.15 +
            coref["composite_score"]     * 0.15
        )
        gli = min(1.0, max(0.0, gli))

        if   gli >= 0.80: grade, label = 1, "ACTIVE"
        elif gli >= 0.62: grade, label = 2, "ADEQUATE"
        elif gli >= 0.44: grade, label = 3, "PASSIVE"
        else:             grade, label = 4, "DISENGAGED"

        self.history.append(answer)

        report = {
            "turn": turn_number,
            "global_listening_index": round(gli, 3),
            "listening_grade": grade,
            "listening_label": label,
            "latency_ms": latency_ms,
            "latency_score": round(lat_score, 3),
            "dimensions": {
                "alignment": alignment,
                "qa_relevance": relevance,
                "discourse_repair": repair,
                "coreference": coref,
            }
        }
        self._sync_amsv(report, turn_number)
        return report

    def _sync_amsv(self, report: Dict, turn: int) -> None:
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        d = report["dimensions"]
        q_align = q16(d["alignment"]["composite_score"])
        q_relev = q16(d["qa_relevance"]["composite_score"])
        q_laten = q16(report["latency_score"])
        q_repai = q16(d["discourse_repair"]["composite_score"])

        # Offset 0x10: ccte_cog_bank_alpha: [align | relevance | latency | repair]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x10,
                         q_align, q_relev, q_laten, q_repai)

        q_coref = q16(d["coreference"]["composite_score"])
        q_gli   = q16(report["global_listening_index"])

        # Offset 0x18: ccte_cog_bank_beta bits [0-15]: coreference, [16-31]: GLI
        struct.pack_into("<HHHH", self.amsv_buffer, 0x18,
                         q_coref, q_gli, 0, 0)

        # Offset 0x28: AEEE repurposed for ALIE session state: [turn | grade | GLI_q16 | 0]
        struct.pack_into("<HHHH", self.amsv_buffer, 0x28,
                         turn, report["listening_grade"], q_gli, 0)
