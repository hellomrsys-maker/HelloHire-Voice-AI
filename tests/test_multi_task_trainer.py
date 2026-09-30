"""
test_multi_task_trainer.py — Unit and integration tests for the unified 17-head MultiTaskModel & MultiTaskTrainer.
"""

import torch
import pytest
from training.multi_task_trainer import (
    MultiTaskModel,
    MultiTaskTrainer,
    PCGradOptimizer
)


def _generate_dummy_batch(batch_size: int = 2, time_steps: int = 16, mel_dim: int = 80):
    x = torch.randn(batch_size, time_steps, mel_dim)
    targets = {
        # Task 1: VCE
        "phonemes": torch.randint(0, 128, (batch_size, time_steps)),
        "prosody": torch.randn(batch_size, time_steps, 3),
        # Task 2: CCTE
        "cognitive": torch.rand(batch_size, 8),
        # Task 3: RSSE
        "format": torch.randint(0, 8, (batch_size,)),
        "compliance": torch.rand(batch_size, 1),
        # Task 4: AEEE
        "irt": torch.randn(batch_size, 2),
        # Task 5: MAIO
        "maio_trajectory": torch.rand(batch_size, 4),
        "maio_alert": torch.rand(batch_size, 1),
        # Task 6: Universal Grammar
        "grammar_validity": torch.rand(batch_size, 1),
        "grammar_depth": torch.rand(batch_size, 1),
        # Task 7: Creativity
        "creativity_tension": torch.rand(batch_size, 1),
        "creativity_rhetoric": torch.randint(0, 5, (batch_size,)),
        # Task 8: Error Diagnostics
        "error_labels": torch.rand(batch_size, 16),
        "error_span": torch.rand(batch_size, 2),
        # Task 9: Writing Skills
        "writing_cohesion": torch.rand(batch_size, 1),
        "writing_readability": torch.rand(batch_size, 1),
        "writing_register": torch.randint(0, 5, (batch_size,)),
        # Task 10: Pragmatics
        "speech_act": torch.randint(0, 6, (batch_size,)),
        "gricean_maxims": torch.rand(batch_size, 4),
        # Task 11: Checklist
        "checklist_scores": torch.rand(batch_size, 7),
        # Task 12: Typology
        "typology_family": torch.randint(0, 11, (batch_size,)),
        "typology_morph": torch.randint(0, 4, (batch_size,)),
        "typology_align": torch.randint(0, 4, (batch_size,)),
        "typology_dir": torch.randint(0, 2, (batch_size,)),
        "typology_pillars": torch.rand(batch_size, 8),
        # Task 13: Bandhu
        "bandhu_skill": torch.randint(0, 6, (batch_size,)),
        "bandhu_era": torch.randint(0, 4, (batch_size,)),
        "bandhu_stage": torch.randint(0, 5, (batch_size,)),
        "bandhu_scores": torch.rand(batch_size, 3),
        # Task 14: ALIE
        "alie_scores": torch.rand(batch_size, 5),
        # Task 15: ECSE
        "ecse_scores": torch.rand(batch_size, 5),
        # Task 16: PMCE
        "pmce_scores": torch.rand(batch_size, 5),
        # Task 17: HCTE
        "hcte_scores": torch.rand(batch_size, 3),
    }
    return x, targets


def test_multitask_model_forward_all_17_heads():
    model = MultiTaskModel(d_model=64)
    x, _ = _generate_dummy_batch(batch_size=2, time_steps=8)
    preds = model(x)

    assert "alie_scores" in preds
    assert preds["alie_scores"].shape == (2, 5)

    assert "ecse_scores" in preds
    assert preds["ecse_scores"].shape == (2, 5)

    assert "pmce_scores" in preds
    assert preds["pmce_scores"].shape == (2, 5)

    assert "hcte_scores" in preds
    assert preds["hcte_scores"].shape == (2, 3)

    assert len(model.log_vars) == 17


def test_multitask_trainer_train_and_validate_steps():
    model = MultiTaskModel(d_model=64)
    trainer = MultiTaskTrainer(model=model, lr=1e-3, use_pcgrad=False)
    x, targets = _generate_dummy_batch(batch_size=2, time_steps=8)

    # Train step
    train_metrics = trainer.train_step(x, targets)
    assert "loss_alie" in train_metrics
    assert "loss_ecse" in train_metrics
    assert "loss_pmce" in train_metrics
    assert "loss_hcte" in train_metrics
    assert "total_weighted_loss" in train_metrics
    assert train_metrics["total_weighted_loss"] > 0

    # Validation step (Gap 4 Overfitting Guard)
    val_metrics = trainer.validate_step(x, targets)
    assert "val_loss_alie" in val_metrics
    assert "val_loss_ecse" in val_metrics
    assert "val_loss_pmce" in val_metrics
    assert "val_loss_hcte" in val_metrics
    assert "val_total_weighted_loss" in val_metrics
    assert val_metrics["val_total_weighted_loss"] > 0
