"""
Vietnamese Language Engine Package (Tiếng Việt)
Solo Rock Sovereign Cognitive Architecture.
"""

from Vietnamese_engine.vietnamese_engine_orchestrator import VietnameseEngineOrchestrator
from Vietnamese_engine.six_language_matrix.vietnamese_matrix_bridge import (
    VietnameseMatrixBridge,
    VIETNAMESE_MAGIC_BYTES,
    VIETNAMESE_MAGIC_INT,
    AMSV_TOTAL_SIZE
)

__all__ = [
    "VietnameseEngineOrchestrator",
    "VietnameseMatrixBridge",
    "VIETNAMESE_MAGIC_BYTES",
    "VIETNAMESE_MAGIC_INT",
    "AMSV_TOTAL_SIZE",
]
