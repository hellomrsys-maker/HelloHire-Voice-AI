"""
Cantonese Sovereign Language Engine (粵語 / 廣東話).
Autonomous world language engine operating under The Zero-Bridge Synchronous Memory Rule.
"""

from Cantonese_engine.cantonese_engine_orchestrator import CantoneseEngineOrchestrator
from Cantonese_engine.six_language_matrix.cantonese_matrix_bridge import (
    CantoneseMatrixBridge,
    CANTONESE_MAGIC_BYTES,
    CANTONESE_MAGIC_INT,
    AMSV_TOTAL_SIZE
)

__all__ = [
    "CantoneseEngineOrchestrator",
    "CantoneseMatrixBridge",
    "CANTONESE_MAGIC_BYTES",
    "CANTONESE_MAGIC_INT",
    "AMSV_TOTAL_SIZE"
]
