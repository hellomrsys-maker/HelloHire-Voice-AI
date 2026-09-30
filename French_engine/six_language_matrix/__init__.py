"""
French Six-Language Matrix Package.
Exposes the FrenchMatrixBridge uniting Rust, C++20, CUDA, Java 21, Julia, and Python.
"""

from .python.french_matrix_bridge import FrenchMatrixBridge

__all__ = ["FrenchMatrixBridge"]
