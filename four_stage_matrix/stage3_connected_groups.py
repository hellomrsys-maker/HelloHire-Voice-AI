"""
stage3_connected_groups.py - Stage 3: Connected Internal Groups.

Stage 3 Architecture:
- Sub-group 3.1: 2x2 Matrix Network (4 x SixLanguageMatrixCell) for domain preprocessing & feature extraction.
- Sub-group 3.2: Central Hub Matrix (1 x SixLanguageMatrixCell) for state arbitration & AMSV lock-free coordination.
- Sub-group 3.3: 2x2 Matrix Network (4 x SixLanguageMatrixCell) for advanced cognitive modeling & scenario synthesis.
- Cyclic Refinement / Feedback Loop: Continuous backward feedback from 3.3 to 3.1 for iterative parameter refinement.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .matrix_cell import SixLanguageMatrixCell
from amsv.python.amsv_embedded import AMSVEmbeddedView


class TwoByTwoMatrixNetwork:
    """
    Represents a 2x2 network of 4 interconnected SixLanguageMatrixCells.
    """

    def __init__(self, prefix: str, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.prefix = prefix
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.m11 = SixLanguageMatrixCell(f"{prefix}_M11", self.amsv)
        self.m12 = SixLanguageMatrixCell(f"{prefix}_M12", self.amsv)
        self.m21 = SixLanguageMatrixCell(f"{prefix}_M21", self.amsv)
        self.m22 = SixLanguageMatrixCell(f"{prefix}_M22", self.amsv)

    def execute_network(
        self,
        input_payload: str,
        incoming_feedback: float = 0.0,
        base_slot: int = 2
    ) -> Dict[str, Any]:
        """
        Executes flow:
        M11 -> M12
         |      |
         v      v
        M21 -> M22
        Incorporating incoming feedback into parameter weights.
        """
        mod_val = min(1.0, max(0.1, 0.75 + (incoming_feedback * 0.2)))

        out11 = self.m11.process_step(input_payload, amsv_slot=base_slot, amsv_val=mod_val)
        out12 = self.m12.process_step(input_payload, amsv_slot=base_slot + 1, amsv_val=out11["composite_score"])
        out21 = self.m21.process_step(input_payload, amsv_slot=base_slot, amsv_val=out11["composite_score"])
        out22 = self.m22.process_step(input_payload, amsv_slot=base_slot + 1, amsv_val=(out12["composite_score"] + out21["composite_score"]) / 2.0)

        composite = round((
            out11["composite_score"] +
            out12["composite_score"] +
            out21["composite_score"] +
            out22["composite_score"]
        ) / 4.0, 4)

        return {
            "network_prefix": self.prefix,
            "m11": out11,
            "m12": out12,
            "m21": out21,
            "m22": out22,
            "network_composite": composite
        }


class ConnectedInternalGroups:
    """
    Stage 3: Group 3.1 (2x2) -> Group 3.2 (Hub) -> Group 3.3 (2x2) with Cyclic Refinement Loop.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.group_3_1 = TwoByTwoMatrixNetwork("Group3_1", self.amsv)
        self.central_hub = SixLanguageMatrixCell("Group3_2_CentralHub", self.amsv)
        self.group_3_3 = TwoByTwoMatrixNetwork("Group3_3", self.amsv)

    def execute_stage3(
        self,
        payload: str,
        iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Executes Stage 3 with active cyclic refinement loop (3.3 -> 3.1).
        """
        cyclic_feedback = 0.0
        iteration_history = []

        final_3_1 = None
        final_hub = None
        final_3_3 = None

        for it in range(1, iterations + 1):
            # 1. Execute Group 3.1 (2x2 Network) receiving cyclic feedback
            out_3_1 = self.group_3_1.execute_network(
                input_payload=payload,
                incoming_feedback=cyclic_feedback,
                base_slot=2 # Memory slot
            )

            # 2. Forward to Central Hub (3.2)
            hub_payload = f"Arbitrate intermediate state: composite={out_3_1['network_composite']}"
            out_hub = self.central_hub.process_step(
                payload=hub_payload,
                amsv_slot=4, # Imagination slot
                amsv_val=out_3_1["network_composite"]
            )

            # 3. Forward to Group 3.3 (2x2 Network)
            out_3_3 = self.group_3_3.execute_network(
                input_payload=payload,
                incoming_feedback=out_hub["composite_score"] - 0.5,
                base_slot=5 # Analytical slot
            )

            # 4. Compute cyclic feedback from 3.3 to be injected into 3.1 on next cycle
            cyclic_feedback = round(out_3_3["network_composite"] - out_3_1["network_composite"], 4)

            iteration_history.append({
                "iteration": it,
                "score_3_1": out_3_1["network_composite"],
                "score_hub": out_hub["composite_score"],
                "score_3_3": out_3_3["network_composite"],
                "cyclic_feedback": cyclic_feedback
            })

            final_3_1 = out_3_1
            final_hub = out_hub
            final_3_3 = out_3_3

        stage3_composite = round((
            final_3_1["network_composite"] * 0.30 +
            final_hub["composite_score"] * 0.30 +
            final_3_3["network_composite"] * 0.40
        ), 4)

        return {
            "stage": 3,
            "group_3_1": final_3_1,
            "central_hub_3_2": final_hub,
            "group_3_3": final_3_3,
            "cyclic_feedback_loop_history": iteration_history,
            "stage3_composite": stage3_composite,
            "cyclic_stability": abs(cyclic_feedback) < 0.20
        }
