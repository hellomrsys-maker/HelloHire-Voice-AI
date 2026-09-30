"""
test_cognitive_training.py — Comprehensive Unit & Integration Tests for Cognitive Neural Training Pipelines.
"""

import os
import struct
import pytest
import torch

from training.train_phase1_engines import (
    Phase1CognitiveNetwork,
    Phase1CognitiveTrainer,
    generate_phase1_curriculum_batch
)
from training.train_phase2_engines import (
    Phase2CognitiveNetwork,
    Phase2CognitiveTrainer,
    generate_phase2_curriculum_batch
)
from training.train_all_cognitive_engines import run_cognitive_training


def test_phase1_cognitive_network_forward_and_loss():
    model = Phase1CognitiveNetwork(vocab_size=1000, d_model=64, nhead=2, num_layers=1)
    tokens, targets = generate_phase1_curriculum_batch(batch_size=2, seq_len=16)

    preds = model(tokens)
    assert "alie_alignment" in preds
    assert "ecse_affect" in preds
    assert "pmce_logos" in preds
    assert "synthesis_cmi" in preds
    assert preds["alie_gli"].shape == (2, 1)

    trainer = Phase1CognitiveTrainer(model=model, lr=1e-3)
    loss, breakdown = trainer.compute_loss(preds, targets)
    assert loss.item() > 0.0
    assert "loss_alie_alignment" in breakdown
    assert "loss_ecse_affect" in breakdown
    assert "loss_pmce_logos" in breakdown


def test_phase1_train_validate_and_amsv_sync():
    amsv_buf = bytearray(64)
    model = Phase1CognitiveNetwork(vocab_size=1000, d_model=64, nhead=2, num_layers=1)
    trainer = Phase1CognitiveTrainer(model=model, lr=1e-3, amsv_buffer=amsv_buf)

    tokens, targets = generate_phase1_curriculum_batch(batch_size=2, seq_len=16)
    train_metrics = trainer.train_step(tokens, targets)
    assert "total_weighted_loss" in train_metrics

    val_metrics = trainer.validate_step(tokens, targets)
    assert "val_total_weighted_loss" in val_metrics

    # Check Zero-Bridge AMSV sync at 0x10, 0x18, 0x20, 0x28
    q_align, q_relev, q_repair, q_coref = struct.unpack_from("<HHHH", amsv_buf, 0x10)
    assert q_align > 0
    assert q_relev > 0

    q_affect, q_rapp, q_mirr, q_polit = struct.unpack_from("<HHHH", amsv_buf, 0x20)
    assert q_affect > 0
    assert q_rapp > 0

    q_logos, q_ethos, q_pathos, q_cta = struct.unpack_from("<HHHH", amsv_buf, 0x28)
    assert q_logos > 0
    assert q_ethos > 0


def test_phase2_cognitive_network_forward_and_loss():
    model = Phase2CognitiveNetwork(vocab_size=1000, d_model=64, nhead=2, num_layers=1)
    tokens, targets = generate_phase2_curriculum_batch(batch_size=2, seq_len=16)

    preds = model(tokens)
    assert "dcve_depth" in preds
    assert "nace_coherence" in preds
    assert "lsce_stamina" in preds
    assert "pace_vocab" in preds
    assert preds["dcve_track"].shape == (2, 5)

    trainer = Phase2CognitiveTrainer(model=model, lr=1e-3)
    loss, breakdown = trainer.compute_loss(preds, targets)
    assert loss.item() > 0.0
    assert "loss_dcve_depth" in breakdown
    assert "loss_nace_coherence" in breakdown
    assert "loss_lsce_stamina" in breakdown
    assert "loss_pace_vocab" in breakdown


def test_phase2_train_validate_and_amsv_sync():
    amsv_buf = bytearray(64)
    model = Phase2CognitiveNetwork(vocab_size=1000, d_model=64, nhead=2, num_layers=1)
    trainer = Phase2CognitiveTrainer(model=model, lr=1e-3, amsv_buffer=amsv_buf)

    tokens, targets = generate_phase2_curriculum_batch(batch_size=2, seq_len=16)
    train_metrics = trainer.train_step(tokens, targets)
    assert "total_weighted_loss" in train_metrics

    val_metrics = trainer.validate_step(tokens, targets)
    assert "val_total_weighted_loss" in val_metrics

    # Check Zero-Bridge AMSV sync at 0x30, 0x34, 0x3C, 0x3E
    q_depth, q_prec = struct.unpack_from("<HH", amsv_buf, 0x30)
    assert q_depth > 0
    assert q_prec > 0

    q_cohere, q_climax = struct.unpack_from("<HH", amsv_buf, 0x34)
    assert q_cohere > 0
    assert q_climax > 0

    q_stamina = struct.unpack_from("<H", amsv_buf, 0x3C)[0]
    assert q_stamina > 0

    q_adapt = struct.unpack_from("<H", amsv_buf, 0x3E)[0]
    assert q_adapt > 0


def test_run_cognitive_training_pipeline(tmp_path):
    res = run_cognitive_training(
        epochs_per_engine=1,
        steps_per_epoch=2,
        batch_size=4,
        checkpoint_dir=str(tmp_path)
    )

    assert "rvce" in res
    assert "hcte" in res
    assert "phase1" in res
    assert "phase2" in res
    assert "amsv_snapshot" in res

    assert os.path.exists(res["rvce"]["checkpoint"])
    assert os.path.exists(res["hcte"]["checkpoint"])
    assert os.path.exists(res["phase1"]["checkpoint"])
    assert os.path.exists(res["phase2"]["checkpoint"])
    assert os.path.exists(res["amsv_snapshot"])
