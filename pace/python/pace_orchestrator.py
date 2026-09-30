"""
pace_orchestrator.py — Pacing & Adaptation Calibration Engine Master Orchestrator

Coordinates 4 PACE sub-AIs:
  1. VocabularyAdaptationAI       — complexity adjustment based on prompt cues
  2. ResponseLengthCalibratorAI   — conciseness vs elaboration compliance
  3. RegisterShiftAI              — formal vs conversational register alignment
  4. InterruptionRecoveryAI       — composure and graceful redirection handling

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into at AMSV physical offset 0x3E (2 bytes):
  [adaptation_q16] (complements 0x3C LSCE stamina).
"""

from __future__ import annotations
import struct
from typing import Dict, Any, Optional

from pace.python.sub_ais.vocabulary_adaptation_ai import VocabularyAdaptationAI
from pace.python.sub_ais.response_length_calibrator_ai import ResponseLengthCalibratorAI
from pace.python.sub_ais.register_shift_ai import RegisterShiftAI
from pace.python.sub_ais.interruption_recovery_ai import InterruptionRecoveryAI


class PacingAdaptationOrchestrator:
    """
    Evaluates how effectively the candidate adapts to shifting interviewer signals,
    constraints, and conversational dynamics.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.vocab_ai      = VocabularyAdaptationAI()
        self.length_ai     = ResponseLengthCalibratorAI()
        self.register_ai   = RegisterShiftAI()
        self.interrupt_ai  = InterruptionRecoveryAI()
        self.amsv_buffer   = master_amsv_buffer

    def evaluate_turn(self, interviewer_prompt: str, candidate_response: str) -> Dict[str, Any]:
        vocab_res     = self.vocab_ai.evaluate(interviewer_prompt, candidate_response)
        length_res    = self.length_ai.evaluate(interviewer_prompt, candidate_response)
        reg_res       = self.register_ai.evaluate(interviewer_prompt, candidate_response)
        interrupt_res = self.interrupt_ai.evaluate(interviewer_prompt, candidate_response)

        # Adaptation Calibration Index (ACI)
        # Weights: Length compliance (0.30), Vocab complexity (0.30), Register match (0.20), Composure (0.20)
        aci = (
            length_res["compliance_score"]    * 0.30 +
            vocab_res["compliance_score"]     * 0.30 +
            reg_res["match_score"]            * 0.20 +
            interrupt_res["composure_score"]  * 0.20
        )
        aci = min(1.0, max(0.0, aci))

        if aci >= 0.80:
            tier = "SEAMLESS"
        elif aci >= 0.60:
            tier = "ADAPTIVE"
        elif aci >= 0.40:
            tier = "RIGID"
        else:
            tier = "OBLIVIOUS"

        report = {
            "adaptation_calibration_index": round(aci, 3),
            "adaptation_tier": tier,
            "length_compliance": length_res["compliance_score"],
            "vocab_compliance": vocab_res["compliance_score"],
            "register_match": reg_res["match_score"],
            "composure": interrupt_res["composure_score"],
            "is_adapted": aci >= 0.65,
            "details": {
                "vocabulary": vocab_res,
                "length": length_res,
                "register": reg_res,
                "interruption": interrupt_res
            }
        }

        if self.amsv_buffer is not None:
            self._sync_amsv(aci)

        return report

    def _sync_amsv(self, adaptation_score: float) -> None:
        """
        Direct Zero-Bridge physical write into AMSV buffer at offset 0x3E (2 bytes).
        Format: <H -> [adaptation_q16].
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        struct.pack_into("<H", self.amsv_buffer, 0x3E, to_q16(adaptation_score))
