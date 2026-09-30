"""
Dutch Sovereign Language Engine Package
Autonomous, zero-bridge cognitive linguistic engine for European Dutch.
"""

from .dutch_engine_orchestrator import DutchEngineOrchestrator
from .six_language_matrix.dutch_matrix_bridge import (
    DUTCH_AMSV_MAGIC,
    DUTCH_ENGINE_ID,
    DutchAtomicMemoryStateVector,
    DutchMatrixMemoryBridge
)

__all__ = [
    "DutchEngineOrchestrator",
    "DUTCH_AMSV_MAGIC",
    "DUTCH_ENGINE_ID",
    "DutchAtomicMemoryStateVector",
    "DutchMatrixMemoryBridge"
]
