"""
Swahili Engine — Autonomous Cognitive World Language Engine
9-Layer Bantu Linguistic Cognitive Architecture, 4 Dedicated Sub-AIs,
Six-Language Matrix, and Zero-Bridge Synchronous Memory State Vector (AMSV: 0x53574148).
"""

from .swahili_engine_orchestrator import SwahiliEngineOrchestrator
from .six_language_matrix.swahili_matrix_bridge import SwahiliMatrixBridge, SWAHILI_AMSV_MAGIC, SWAHILI_AMSV_SIZE

__version__ = "1.0.0"
__all__ = [
    "SwahiliEngineOrchestrator",
    "SwahiliMatrixBridge",
    "SWAHILI_AMSV_MAGIC",
    "SWAHILI_AMSV_SIZE"
]
