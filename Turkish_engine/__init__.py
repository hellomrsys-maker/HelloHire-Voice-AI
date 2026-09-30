"""Turkish Computational Cognitive Language Engine.

Implements the 9-layer cognitive architecture, 4 dedicated Sub-AIs,
six-language matrix, and Zero-Bridge Synchronous AMSV memory synchronization
for the Turkish language (Türkçe).
"""

from .turkish_engine_orchestrator import (
    TurkishEngineOrchestrator,
    TurkishEngineAnalysisResult
)
from .brain.sub_ais import (
    TurkishSyntaxSubAI,
    TurkishPhonologySubAI,
    TurkishPragmaticSubAI,
    TurkishEditorialSubAI
)
from .six_language_matrix import TurkishMatrixBridge

__all__ = [
    "TurkishEngineOrchestrator",
    "TurkishEngineAnalysisResult",
    "TurkishSyntaxSubAI",
    "TurkishPhonologySubAI",
    "TurkishPragmaticSubAI",
    "TurkishEditorialSubAI",
    "TurkishMatrixBridge"
]
