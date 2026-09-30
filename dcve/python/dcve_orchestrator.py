"""
dcve_orchestrator.py — Domain Competence Verbal Engine Master Orchestrator

Coordinates 4 DCVE sub-AIs:
  1. JargonVsDepthAI          — distinguishes shallow buzzwords vs deep technical markers
  2. ConceptualPrecisionAI    — quantifiers, concrete units, and causal mechanics
  3. DomainTrackClassifierAI  — domain taxonomy classification (Engineering, Finance, Medical, Legal, Executive)
  4. OntologyGroundingAI      — semantic relationship integrity & hallucination filtering

Zero-Bridge Synchronous Memory Rule:
  Direct in-place struct.pack_into at AMSV physical offset 0x30:
  [domain_depth_q16 | precision_q16 | track_id_q16 | grounding_q16]
"""

from __future__ import annotations
import struct
from typing import Dict, Any, Optional

from dcve.python.sub_ais.jargon_vs_depth_ai import JargonVsDepthAI
from dcve.python.sub_ais.conceptual_precision_ai import ConceptualPrecisionAI
from dcve.python.sub_ais.domain_track_classifier_ai import DomainTrackClassifierAI
from dcve.python.sub_ais.ontology_grounding_ai import OntologyGroundingAI


class DomainCompetenceVerbalOrchestrator:
    """
    Evaluates candidate verbal answers for authentic domain competence vs shallow hand-waving.
    """

    def __init__(self, master_amsv_buffer: Optional[bytearray] = None):
        self.jargon_ai    = JargonVsDepthAI()
        self.precision_ai = ConceptualPrecisionAI()
        self.track_ai     = DomainTrackClassifierAI()
        self.grounding_ai = OntologyGroundingAI()
        self.amsv_buffer  = master_amsv_buffer

    def evaluate(self, answer: str) -> Dict[str, Any]:
        """
        Runs all 4 sub-AIs, synthesizes the Domain Competence Index (DCI),
        and updates the 64-byte AMSV physical buffer in-place.
        """
        jargon_res    = self.jargon_ai.evaluate(answer)
        precision_res = self.precision_ai.evaluate(answer)
        track_res     = self.track_ai.evaluate(answer)
        grounding_res = self.grounding_ai.evaluate(answer)

        # Composite Domain Competence Index (DCI)
        # Weights: Depth (0.35), Precision (0.30), Grounding (0.25), Track confidence (0.10)
        dci = (
            jargon_res["depth_score"] * 0.35 +
            precision_res["precision_score"] * 0.30 +
            grounding_res["ontology_grounding_score"] * 0.25 +
            track_res["confidence"] * 0.10
        )
        dci = min(1.0, max(0.0, dci))

        if dci >= 0.78:
            tier = "EXPERT"
        elif dci >= 0.58:
            tier = "PROFICIENT"
        elif dci >= 0.38:
            tier = "SURFACE_LEVEL"
        else:
            tier = "NOVICE"

        report = {
            "domain_competence_index": round(dci, 3),
            "competence_tier": tier,
            "primary_track": track_res["primary_track"],
            "track_id": track_res["track_id"],
            "depth_score": jargon_res["depth_score"],
            "precision_score": precision_res["precision_score"],
            "grounding_score": grounding_res["ontology_grounding_score"],
            "is_substantive": jargon_res["is_substantive"],
            "is_quantitatively_grounded": precision_res["is_quantitatively_grounded"],
            "details": {
                "jargon_vs_depth": jargon_res,
                "conceptual_precision": precision_res,
                "domain_track": track_res,
                "ontology_grounding": grounding_res
            }
        }

        if self.amsv_buffer is not None:
            self._sync_amsv(
                depth=jargon_res["depth_score"],
                precision=precision_res["precision_score"],
                track_id=track_res["track_id"],
                grounding=grounding_res["ontology_grounding_score"]
            )

        return report

    def _sync_amsv(self, depth: float, precision: float, track_id: int, grounding: float) -> None:
        """
        Direct Zero-Bridge physical write into AMSV buffer at offset 0x30 (4 bytes).
        Format: <HH -> [depth_q16, precision_q16] (leaves 0x34..0x37 for NACE).
        """
        if self.amsv_buffer is None or len(self.amsv_buffer) < 64:
            return

        def to_q16(v: float) -> int:
            return int(min(1.0, max(0.0, v)) * 65535)

        struct.pack_into("<HH", self.amsv_buffer, 0x30,
                         to_q16(depth),
                         to_q16(precision))
