# =============================================================================
# training/python/src/polyglot_training/experiment_tracker.py
# MLflow-based experiment tracking for training runs.
# =============================================================================

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RunMetrics:
    """Snapshot of metrics for a training run."""
    run_id:       str
    step:         int
    loss:         float
    eval_loss:    Optional[float]
    learning_rate: float
    gradient_norm: float
    tokens_per_sec: float


class ExperimentTracker:
    """
    MLflow-based experiment tracker for training runs.

    Falls back to a file-based tracker if MLflow is not available.
    """

    def __init__(self, tracking_dir: str = "experiments/"):
        self._tracking_dir = Path(tracking_dir)
        self._tracking_dir.mkdir(parents=True, exist_ok=True)
        self._active_run = None
        self._use_mlflow = self._try_import_mlflow()
        self._step_log: list[dict] = []

    def _try_import_mlflow(self) -> bool:
        try:
            import mlflow
            mlflow.set_tracking_uri(f"file://{self._tracking_dir.absolute()}")
            return True
        except ImportError:
            logger.info("MLflow not available — using file-based tracking")
            return False

    def start_run(self, run_name: str, params: dict[str, Any]) -> None:
        """Starts a new tracking run."""
        if self._use_mlflow:
            import mlflow
            self._active_run = mlflow.start_run(run_name=run_name)
            mlflow.log_params({
                k: str(v)[:250] for k, v in params.items()
            })
        else:
            self._run_name = run_name
            self._step_log.clear()
            logger.info("Tracking run started: %s", run_name)

    def log_metrics(self, metrics: dict[str, float], step: int) -> None:
        """Logs a dictionary of metrics at a given step."""
        if self._use_mlflow:
            import mlflow
            mlflow.log_metrics(metrics, step=step)
        else:
            self._step_log.append({"step": step, **metrics})
            # Write to CSV file every 100 entries
            if len(self._step_log) % 100 == 0:
                self._flush_to_file()

    def log_artifact(self, local_path: str) -> None:
        """Logs a file as an artifact."""
        if self._use_mlflow:
            import mlflow
            mlflow.log_artifact(local_path)
        else:
            logger.info("Artifact logged: %s", local_path)

    def end_run(self) -> None:
        """Ends the active tracking run."""
        if self._use_mlflow:
            import mlflow
            if self._active_run is not None:
                mlflow.end_run()
                self._active_run = None
        else:
            self._flush_to_file()
            logger.info("Tracking run ended")

    def _flush_to_file(self) -> None:
        """Writes accumulated metrics to a CSV file."""
        if not self._step_log:
            return
        run_name = getattr(self, "_run_name", "run")
        csv_path = self._tracking_dir / f"{run_name}_metrics.csv"
        try:
            with open(csv_path, "a", encoding="utf-8") as f:
                if csv_path.stat().st_size == 0:
                    headers = ",".join(self._step_log[0].keys())
                    f.write(headers + "\n")
                for entry in self._step_log:
                    f.write(",".join(str(v) for v in entry.values()) + "\n")
            self._step_log.clear()
        except Exception as e:
            logger.warning("Failed to write metrics to CSV: %s", e)
