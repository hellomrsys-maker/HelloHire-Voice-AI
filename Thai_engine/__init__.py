"""
Thai Sovereign Language Engine (ภาษาไทย).
Autonomous world language engine operating under The Zero-Bridge Synchronous Memory Rule.
"""

from Thai_engine.thai_engine_orchestrator import ThaiEngineOrchestrator
from Thai_engine.six_language_matrix.thai_matrix_bridge import (
    ThaiMatrixBridge,
    THAI_MAGIC_BYTES,
    THAI_MAGIC_INT,
    AMSV_TOTAL_SIZE
)

__all__ = [
    "ThaiEngineOrchestrator",
    "ThaiMatrixBridge",
    "THAI_MAGIC_BYTES",
    "THAI_MAGIC_INT",
    "AMSV_TOTAL_SIZE"
]
