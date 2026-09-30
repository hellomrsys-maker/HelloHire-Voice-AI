"""
Six-Language Matrix Package for English Engine.
Combines Rust (data processing), Julia (math/simulations), Python (high-level training API),
C++20 (engine core), CUDA/Triton (GPU kernels), and Java 21 (virtual threads)
under the Zero-Bridge Synchronous Memory Rule.
"""

from English_engine.six_language_matrix.python.english_matrix_bridge import (
    EnglishSixLanguageMatrixBridge,
    SixLanguageExecutionResult,
)

__all__ = [
    "EnglishSixLanguageMatrixBridge",
    "SixLanguageExecutionResult",
]
