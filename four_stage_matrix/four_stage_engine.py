"""
four_stage_engine.py - Master Orchestrator for the Reusable Four-Stage 6-Language Matrix Pattern.

Coordinates all 4 stages:
Stage 1: Reserved Entry Boundary (Requirement / Input)
Stage 2: Base Matrix <--> AI Model + Training (with bidirectional shared state + feedback)
Stage 3: Connected Internal Groups (3.1 [2x2] -> 3.2 [Hub] -> 3.3 [2x2] with cyclic refinement loop)
Stage 4: Verify, Learn, Analyze, Result (4.1 -> 4.2 -> 4.3 -> 4.4 -> out, with recursive feedback)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from .stage1_entry import ReservedEntryBoundary, RequirementContract, Stage1EntryResult
from .stage2_base_ai import BaseMatrixAIPair
from .stage3_connected_groups import ConnectedInternalGroups
from .stage4_execution_pipeline import VerifyLearnAnalyzePipeline
from amsv.python.amsv_embedded import AMSVEmbeddedView


class FourStageMatrixEngine:
    """
    Domain-neutral master orchestrator executing the complete Reusable Four-Stage Pattern.
    """

    def __init__(
        self,
        engine_name: str = "DomainNeutralEngine",
        contract: Optional[RequirementContract] = None,
        amsv_view: Optional[AMSVEmbeddedView] = None
    ):
        self.engine_name = engine_name
        self.amsv = amsv_view or AMSVEmbeddedView()
        self.stage1 = ReservedEntryBoundary(contract)
        self.stage2 = BaseMatrixAIPair(self.amsv)
        self.stage3 = ConnectedInternalGroups(self.amsv)
        self.stage4 = VerifyLearnAnalyzePipeline(self.amsv)

    def execute(
        self,
        raw_input: str,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes all four stages sequentially with bidirectional and cyclic feedback loops.
        """
        # ====================================================================
        # STAGE 1: RESERVED ENTRY BOUNDARY
        # ====================================================================
        entry_result: Stage1EntryResult = self.stage1.validate_and_bind(raw_input, custom_context)
        if not entry_result.is_valid:
            return {
                "engine": self.engine_name,
                "status": "REJECTED_AT_STAGE_1",
                "rejection_reasons": entry_result.rejection_reasons,
                "quality_checks": entry_result.quality_checks
            }

        sanitized = entry_result.sanitized_input
        contract_meta = entry_result.contract.context_metadata

        # ====================================================================
        # STAGE 2: BASE MATRIX <--> AI MODEL + TRAINING
        # ====================================================================
        stage2_res = self.stage2.execute_stage2(sanitized, contract_meta)

        # ====================================================================
        # STAGE 3: CONNECTED INTERNAL GROUPS (3.1 [2x2] -> 3.2 [Hub] -> 3.3 [2x2])
        # ====================================================================
        stage3_res = self.stage3.execute_stage3(sanitized, iterations=2)

        # ====================================================================
        # STAGE 4: VERIFY, LEARN, ANALYZE, RESULT (4.1 -> 4.2 -> 4.3 -> 4.4 -> OUT)
        # ====================================================================
        stage4_res = self.stage4.execute_stage4(
            payload=sanitized,
            stage3_summary=stage3_res,
            max_feedback_passes=2
        )

        # Final Holistic Engine Score
        final_score = round((
            stage2_res["stage2_composite"] * 0.25 +
            stage3_res["stage3_composite"] * 0.35 +
            stage4_res["out_result"]["final_composite_score"] * 0.40
        ), 4)

        return {
            "engine": self.engine_name,
            "status": "COMPLETED",
            "stage1_entry": entry_result,
            "stage2_base_ai_pair": stage2_res,
            "stage3_connected_groups": stage3_res,
            "stage4_execution_pipeline": stage4_res,
            "out_result": stage4_res["out_result"],
            "global_four_stage_score": final_score,
            "amsv_synchronized": True
        }


# ============================================================================
# CONCRETE SPECIALIZED DOMAIN ENGINES IMPLEMENTING THE FOUR-STAGE PATTERN
# ============================================================================

class RecruitmentVerbalFourStageEngine(FourStageMatrixEngine):
    """
    Dedicated Recruitment Verbal Communication Engine (RVCE) implementing
    the Reusable Four-Stage 6-Language Matrix Pattern across 8 interview formats.
    """

    def __init__(self, amsv_view: Optional[AMSVEmbeddedView] = None):
        contract = RequirementContract(
            requirement_name="RecruitmentVerbalCommunication",
            target_format_code=2, # Behavioral STAR default
            min_word_count=5,
            max_word_count=500,
            target_wpm=140.0,
            min_composite_threshold=0.70,
            context_metadata={"domain": "Recruitment", "rubric": "STAR"}
        )
        super().__init__("RecruitmentVerbalFourStageEngine", contract, amsv_view)

    def evaluate_interview_turn(
        self,
        transcript: str,
        format_code: int = 2,
        turn_number: int = 1,
        speech_wpm: float = 140.0
    ) -> Dict[str, Any]:
        self.stage1.contract.target_format_code = format_code
        self.stage1.contract.target_wpm = speech_wpm

        exec_res = self.execute(
            transcript,
            custom_context={"format_code": format_code, "turn": turn_number, "wpm": speech_wpm}
        )

        if exec_res.get("status") == "COMPLETED":
            # Synchronize to AMSV Offset 0x20
            # [Bits 0-15: format | Bits 16-31: turn | Bits 32-47: comp Q16 | Bits 48-63: phase]
            comp = max(0.0, min(1.0, float(exec_res["global_four_stage_score"])))
            comp_q16 = int(comp * 65535) & 0xFFFF

            packed = (
                (format_code & 0xFFFF) |
                ((turn_number & 0xFFFF) << 16) |
                ((comp_q16 & 0xFFFF) << 32) |
                (2 << 48) # Active evaluation phase
            )
            self.amsv.set_scenario_state(packed)

        return exec_res
