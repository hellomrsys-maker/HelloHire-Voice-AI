"""
cdie_orchestrator.py — Cross-Domain Idea Transfer Engine Master Orchestrator

Coordinates 4 CDIE Sub-AIs:
  1. CrossDomainAnalogiesAI    — detects cross-domain metaphorical structures
  2. InterdisciplinaryBridgeAI — evaluates structural and causal translation depth
  3. LateralConceptMapperAI    — identifies orthogonal, counter-intuitive solutions
  4. ConceptualDistanceAI      — measures semantic manifold distance between disparate fields

Zero-Bridge Synchronous Memory Rule:
  Direct in-place memory synchronization with zero serialization overhead.
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Optional

from cdie.python.sub_ais.cross_domain_analogies_ai import CrossDomainAnalogiesAI
from cdie.python.sub_ais.interdisciplinary_bridge_ai import InterdisciplinaryBridgeAI
from cdie.python.sub_ais.lateral_concept_mapper_ai import LateralConceptMapperAI
from cdie.python.sub_ais.conceptual_distance_ai import ConceptualDistanceAI


class CrossDomainIdeaTransferOrchestrator:
    """
    Evaluates lateral thinking, cross-domain analogy generation, and interdisciplinary
    first-principles translation in candidate responses.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None, amsv_offset: int = 0x38):
        self.analogies_ai = CrossDomainAnalogiesAI()
        self.bridge_ai    = InterdisciplinaryBridgeAI()
        self.lateral_ai   = LateralConceptMapperAI()
        self.distance_ai  = ConceptualDistanceAI()
        self.amsv_buffer  = master_amsv_buffer
        self.amsv_offset  = amsv_offset

    def evaluate(self, answer: str) -> Dict[str, Any]:
        analogies_res = self.analogies_ai.evaluate(answer)
        bridge_res    = self.bridge_ai.evaluate(answer)
        lateral_res   = self.lateral_ai.evaluate(answer)
        
        has_causal = bridge_res["causal_grounding_hits"] > 0
        distance_res  = self.distance_ai.evaluate(
            analogies_res["domains_detected"],
            has_causal_link=has_causal
        )

        # Cross-Domain Transfer Index (CDTI)
        cdti = (
            analogies_res["composite_score"] * 0.35 +
            bridge_res["composite_score"]    * 0.25 +
            lateral_res["composite_score"]   * 0.25 +
            distance_res["composite_score"]  * 0.15
        )
        cdti = min(1.0, max(0.0, cdti))

        if   cdti >= 0.75: grade, label = 1, "VISIONARY_SYNTHESIZER"
        elif cdti >= 0.55: grade, label = 2, "LATERAL_THINKER"
        elif cdti >= 0.35: grade, label = 3, "INCREMENTAL_THINKER"
        else:             grade, label = 4, "LINEAR_BRUTE_FORCE"

        report = {
            "cross_domain_transfer_index": round(cdti, 3),
            "transfer_grade": grade,
            "transfer_label": label,
            "has_cross_domain_bridge": analogies_res["has_cross_domain_bridge"],
            "dimensions": {
                "analogies": analogies_res,
                "interdisciplinary_bridge": bridge_res,
                "lateral_concept": lateral_res,
                "conceptual_distance": distance_res
            }
        }
        self._sync_amsv(report)
        return report

    def _sync_amsv(self, report: Dict[str, Any]) -> None:
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return
        def q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        d = report["dimensions"]
        # Sync to designated offset
        struct.pack_into(
            "<HH",
            self.amsv_buffer,
            self.amsv_offset,
            q16(report["cross_domain_transfer_index"]),
            report["transfer_grade"]
        )
