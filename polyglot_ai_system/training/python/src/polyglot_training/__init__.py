# =============================================================================
# training/python/src/polyglot_training/__init__.py
# AI Training System — Python high-level training API
# =============================================================================

"""
polyglot_training: Python training orchestration API for the Polyglot AI system.

Provides:
  - TrainingOrchestrator: Coordinates the full training pipeline
  - CognitiveTrainer: Per-faculty cognitive training manager
  - ExperimentTracker: MLflow-based experiment tracking
  - TrainingDataLoader: Dataset loading and preprocessing
  - TrainingConfig: Complete training configuration
"""

from .training_orchestrator import TrainingOrchestrator, TrainingConfig, TrainingState
from .cognitive_trainer import (
    CognitiveTrainer,
    ThinkingTrainer,
    AttentionTrainer,
    MemoryRecallTrainer,
    CreativityTrainer,
    ImaginationTrainer,
    MetacognitionTrainer,
)
from .experiment_tracker import ExperimentTracker, RunMetrics
from .data_loader import TrainingDataLoader, TrainingDataset, DataBatch

__version__ = "1.0.0"
__all__ = [
    "TrainingOrchestrator",
    "TrainingConfig",
    "TrainingState",
    "CognitiveTrainer",
    "ThinkingTrainer",
    "AttentionTrainer",
    "MemoryRecallTrainer",
    "CreativityTrainer",
    "ImaginationTrainer",
    "MetacognitionTrainer",
    "ExperimentTracker",
    "RunMetrics",
    "TrainingDataLoader",
    "TrainingDataset",
    "DataBatch",
]
