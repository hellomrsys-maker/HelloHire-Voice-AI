"""Russian Computational Cognitive Language Engine.

Implements the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
six-language matrix, and Zero-Bridge Synchronous AMSV memory synchronization
for the Russian language (Русский язык).
"""

from .russian_engine_orchestrator import (
    RussianEngineOrchestrator,
    RussianEngineAnalysisResult
)
from .brain.sub_ais import (
    RussianSyntaxSubAI,
    RussianPhonologySubAI,
    RussianPragmaticSubAI,
    RussianEditorialSubAI
)
from .six_language_matrix import RussianMatrixBridge

__all__ = [
    "RussianEngineOrchestrator",
    "RussianEngineAnalysisResult",
    "RussianSyntaxSubAI",
    "RussianPhonologySubAI",
    "RussianPragmaticSubAI",
    "RussianEditorialSubAI",
    "RussianMatrixBridge"
]
