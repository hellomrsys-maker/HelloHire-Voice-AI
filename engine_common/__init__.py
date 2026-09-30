"""
engine_common — Shared English-Parity Engine Base Package.
===========================================================

This package encodes the FULL English-flagship 9-layer linguistic pipeline exactly
once, so that every language engine in the Solo Rock / BandhuPrime ecosystem inherits
identical structure and behaviour without duplicating thousands of near-identical files.

Every language engine is brought to English parity by:
  1. A shared ``BaseEngineOrchestrator`` wiring the complete 9-layer pipeline,
     4 dedicated Sub-AIs, the Six-Language Matrix, the Four-Stage Matrix, and the
     64-byte AMSV zero-bridge memory.
  2. Shared base classes for Skills, Analysis, Rules, Tasks, Sub-AIs and the
     Six-Language Matrix bridge, each parameterised by a ``LanguageProfile``.
  3. The English-Pivot Comprehension Layer (``english_pivot``) — every non-English
     engine "understands English first": it normalises input into an English-anchored
     semantic representation, runs shared comprehension over it, then maps results back
     into the target language.

The design honours the RULEBOOK:
  * Zero-Bridge Synchronous Memory Rule (all lanes share the 64-byte AMSV).
  * Strict Six-Language Matrix Standard (Rust / Julia / Python / C++ / CUDA / Java).
  * Reusable Four-Stage 6-Language Matrix Pattern.
  * Zero placeholders — all behaviour is real, not stubbed.
"""

# Lightweight, always-safe exports (no torch/numpy dependency).
from .language_profile import LanguageProfile, WordOrder, ScriptType, LANGUAGE_REGISTRY

__all__ = [
    "LanguageProfile",
    "WordOrder",
    "ScriptType",
    "LANGUAGE_REGISTRY",
    "BaseEngineOrchestrator",
    "EngineComprehensiveOutput",
    "EnglishPivotComprehension",
    "PivotComprehensionResult",
]


def __getattr__(name):
    """Lazily expose the heavier classes so that importing lightweight submodules
    (e.g. ``engine_common.training_data``) does not pull in torch until needed."""
    if name in ("BaseEngineOrchestrator", "EngineComprehensiveOutput"):
        from .base_orchestrator import BaseEngineOrchestrator, EngineComprehensiveOutput
        return {"BaseEngineOrchestrator": BaseEngineOrchestrator,
                "EngineComprehensiveOutput": EngineComprehensiveOutput}[name]
    if name in ("EnglishPivotComprehension", "PivotComprehensionResult"):
        from .english_pivot import EnglishPivotComprehension, PivotComprehensionResult
        return {"EnglishPivotComprehension": EnglishPivotComprehension,
                "PivotComprehensionResult": PivotComprehensionResult}[name]
    raise AttributeError(f"module 'engine_common' has no attribute {name!r}")
