# =============================================================================
# engine/python/src/polyglot_engine/__init__.py
# Polyglot AI Verbal Communication Engine — Python High-Level API
# =============================================================================

"""
polyglot_engine: Python high-level API and orchestration for the
Polyglot AI Verbal Communication Engine.

This package provides:
  - EngineClient: High-level Python interface to the C++ engine core
  - TrainingOrchestrator: Orchestration for training pipelines
  - ExperimentTracker: MLflow-based experiment tracking
  - LanguageEngineLoader: Loads canonical training YAML files
  - VerbalEngineServer: FastAPI REST server for the engine
"""

from .engine_client import EngineClient, EngineClientConfig
from .language_engine import LanguageEngineLoader, CanonicalEngineFile
from .training_api import TrainingOrchestrator, TrainingConfig
from .experiment_tracker import ExperimentTracker
from .server import VerbalEngineServer
from .verify import run_verification

__version__ = "1.0.0"
__all__ = [
    "EngineClient",
    "EngineClientConfig",
    "LanguageEngineLoader",
    "CanonicalEngineFile",
    "TrainingOrchestrator",
    "TrainingConfig",
    "ExperimentTracker",
    "VerbalEngineServer",
    "run_verification",
]
