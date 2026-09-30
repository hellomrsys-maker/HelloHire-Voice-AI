"""
Persian Language Engine Package (Farsi / Dari / Tajik)
Solo Rock Sovereign Cognitive Architecture.
"""

from Persian_engine.persian_engine_orchestrator import PersianEngineOrchestrator
from Persian_engine.six_language_matrix.persian_matrix_bridge import (
    PersianMatrixBridge,
    PERSIAN_MAGIC_BYTES,
    PERSIAN_MAGIC_INT,
    AMSV_TOTAL_SIZE
)

__all__ = [
    "PersianEngineOrchestrator",
    "PersianMatrixBridge",
    "PERSIAN_MAGIC_BYTES",
    "PERSIAN_MAGIC_INT",
    "AMSV_TOTAL_SIZE",
]
