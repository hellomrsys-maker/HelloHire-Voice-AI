"""
pmce_orchestrator.py — Persuasion & Message Construction Engine Master Orchestrator

Coordinates 5 PMCE Sub-AIs:
  1. LogosAI          — logical argumentation, syllogism validity, data-backed evidence
  2. EthosAI          — credibility signaling, expertise anchoring, track record
  3. PathosAI         — emotional resonance, audience empathy, vision framing
  4. KairosAI         — timing and situational appropriateness of message delivery
  5. CallToActionAI   — decisive closing with clear proposal and directional momentum

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into into the 64-byte AMSV physical buffer at offset 0x28.
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from pmce.python.sub_ais.logos_argument_ai import LogosAI
from pmce.python.sub_ais.ethos_credibility_ai import EthosAI
from pmce.python.sub_ais.pathos_resonance_ai import PathosAI
from pmce.python.sub_ais.kairos_timing_ai import KairosAI
from pmce.python.sub_ais.cta_clarity_ai import CallToActionAI

# Backward-compatibility alias
CTAAI = CallToActionAI


class PersuasionMessageConstructionOrchestrator:
    """
    Evaluates argumentative and rhetorical architecture across the 5 classical dimensions:
    Logos, Ethos, Pathos, Kairos, and Call-to-Action.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None, amsv_offset: int = 0x10):
        self.logos_ai     = LogosAI()
        self.ethos_ai     = EthosAI()
        self.pathos_ai    = PathosAI()
        self.kairos_ai    = KairosAI()
        self.cta_ai       = CallToActionAI()
        self.amsv_buffer  = master_amsv_buffer
        self.amsv_offset  = amsv_offset

    def evaluate_turn(
        self,
        text: str,
        turn_number: int = 1
    ) -> Dict[str, Any]:
        logos   = self.logos_ai.evaluate(text)
        ethos   = self.ethos_ai.evaluate(text)
        pathos  = self.pathos_ai.evaluate(text)
        kairos  = self.kairos_ai.evaluate(text, turn_number)
        cta     = self.cta_ai.evaluate(text)

        gpi = (
            logos["composite_score"]  * 0.25 +
            ethos["composite_score"]  * 0.20 +
            pathos["composite_score"] * 0.18 +
            kairos["composite_score"] * 0.20 +
            cta["composite_score"]    * 0.17
        )
        gpi = min(1.0, max(0.0, gpi))

        if   gpi >= 0.82: grade, label = 1, "HIGHLY_PERSUASIVE"
        elif gpi >= 0.65: grade, label = 2, "PERSUASIVE"
        elif gpi >= 0.48: grade, label = 3, "ADEQUATE"
        else:             grade, label = 4, "WEAK"

        report = {
            "turn": turn_number,
            "global_persuasion_index": round(gpi, 3),
            "persuasion_grade": grade,
            "persuasion_label": label,
            "dimensions": {
                "logos": logos,
                "ethos": ethos,
                "pathos": pathos,
                "kairos": kairos,
                "cta": cta
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
        # PMCE partition is 0x28..0x2F (8 bytes)
        # Offset 0x28: [logos_q16 (2B) | ethos_q16 (2B) | pathos_q16 (2B) | kairos_q16 (2B)]
        struct.pack_into(
            "<HHHH",
            self.amsv_buffer,
            self.amsv_offset,
            q16(d["logos"]["composite_score"]),
            q16(d["ethos"]["composite_score"]),
            q16(d["pathos"]["composite_score"]),
            q16(d["kairos"]["composite_score"])
        )
