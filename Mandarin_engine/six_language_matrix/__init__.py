"""
Mandarin Engine Six-Language Matrix Package
==========================================
Integrates Rust, Python, C++20, CUDA, Java 21, and Julia.
Strictly adheres to the Zero-Bridge Synchronous Memory Rule via 64-byte AMSV.
"""

from .python.mandarin_matrix_bridge import (
    MandarinSixLanguageMatrixBridge,
    MandarinSixLanguageExecutionResult,
)

__all__ = [
    "MandarinSixLanguageMatrixBridge",
    "MandarinSixLanguageExecutionResult",
]
