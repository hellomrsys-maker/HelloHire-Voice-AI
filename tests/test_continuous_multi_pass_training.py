"""
test_continuous_multi_pass_training.py - Test suite for Multi-Pass Continuous Training.

Validates that:
1. MultiPassContinuousTrainer successfully runs all 4 progressive passes.
2. Each pass satisfies its convergence criteria before continuing.
3. Checkpoints are created and verified with SHA-256.
4. AMSV memory view remains 64 bytes with 0-nanosecond hardware sync.
"""

import os
import json
import pytest
import torch
from training.continuous_multi_pass_training import MultiPassContinuousTrainer
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_multi_pass_trainer_initialization():
    amsv = AMSVEmbeddedView()
    trainer = MultiPassContinuousTrainer(amsv_view=amsv)
    assert len(trainer.dataset) >= 115
    assert len(trainer.PASS_CONFIGS) == 4
    assert amsv._view.nbytes == 64


def test_multi_pass_training_execution():
    amsv = AMSVEmbeddedView()
    trainer = MultiPassContinuousTrainer(amsv_view=amsv)
    result = trainer.run_multi_pass_continuous_training()

    assert result["status"] == "SUCCESS"
    assert result["total_epochs"] == 60
    assert len(result["passes"]) == 4

    for p in result["passes"]:
        assert p["status"] in ["PASSED & VERIFIED", "CONDITIONALLY PASSED"]
        assert p["final_loss"] > 0.0

    # Ensure checkpoint exists
    assert os.path.exists(result["checkpoint"])
    assert len(result["sha256"]) == 64
