"""
German Engine Package
An autonomous cognitive language engine for German (Deutsch).
"""

from .german_engine_orchestrator import GermanEngineOrchestrator
from .six_language_matrix.german_matrix_bridge import GermanMatrixBridge, GERMAN_AMSV_MAGIC, GERMAN_AMSV_SIZE

__all__ = [
    "GermanEngineOrchestrator",
    "GermanMatrixBridge",
    "GERMAN_AMSV_MAGIC",
    "GERMAN_AMSV_SIZE"
]
