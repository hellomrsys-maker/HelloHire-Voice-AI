"""
Arabic Engine — Autonomous Cognitive World Language Engine
9-Layer Semitic Linguistic Cognitive Architecture, 4 Dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x41524142).
"""

from .arabic_engine_orchestrator import ArabicEngineOrchestrator
from .six_language_matrix.arabic_matrix_bridge import ArabicMatrixBridge, ARABIC_AMSV_MAGIC, ARABIC_AMSV_SIZE

__version__ = "1.0.0"
__all__ = [
    "ArabicEngineOrchestrator",
    "ArabicMatrixBridge",
    "ARABIC_AMSV_MAGIC",
    "ARABIC_AMSV_SIZE"
]
