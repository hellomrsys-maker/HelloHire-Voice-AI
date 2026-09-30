"""
Spanish Engine Six-Language Matrix Package
=========================================
Integrates Rust, Python, C++20, CUDA, Java 21, and Julia.
Strictly adheres to the Zero-Bridge Synchronous Memory Rule via 64-byte AMSV.
"""

from .python.spanish_matrix_bridge import (
    SpanishSixLanguageMatrixBridge,
    SpanishSixLanguageExecutionResult,
)

__all__ = [
    "SpanishSixLanguageMatrixBridge",
    "SpanishSixLanguageExecutionResult",
]
