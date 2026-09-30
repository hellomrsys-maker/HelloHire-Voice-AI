"""
four_stage_matrix - Reusable Four-Stage 6-Language Matrix Pattern.

Exports:
- SixLanguageMatrixCell (M): Complete 6-language execution box
- ReservedEntryBoundary, RequirementContract (Stage 1)
- BaseMatrixAIPair (Stage 2)
- TwoByTwoMatrixNetwork, ConnectedInternalGroups (Stage 3)
- VerifyLearnAnalyzePipeline (Stage 4)
- FourStageMatrixEngine, RecruitmentVerbalFourStageEngine
"""

from .matrix_cell import SixLanguageMatrixCell
from .stage1_entry import ReservedEntryBoundary, RequirementContract, Stage1EntryResult
from .stage2_base_ai import BaseMatrixAIPair
from .stage3_connected_groups import TwoByTwoMatrixNetwork, ConnectedInternalGroups
from .stage4_execution_pipeline import VerifyLearnAnalyzePipeline
from .four_stage_engine import FourStageMatrixEngine, RecruitmentVerbalFourStageEngine

__all__ = [
    "SixLanguageMatrixCell",
    "ReservedEntryBoundary",
    "RequirementContract",
    "Stage1EntryResult",
    "BaseMatrixAIPair",
    "TwoByTwoMatrixNetwork",
    "ConnectedInternalGroups",
    "VerifyLearnAnalyzePipeline",
    "FourStageMatrixEngine",
    "RecruitmentVerbalFourStageEngine"
]
