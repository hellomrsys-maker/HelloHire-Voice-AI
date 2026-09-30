"""
train_all_cognitive_engines.py — Master Cognitive Neural Training Orchestrator.

Sequentially trains and validates all cognitive neural systems:
  1. RVCE Cognitive AI (Thinking, Concentration, Recall, Creativity, Imagination, Verbal)
  2. HCTE Human Cognitive Thinking Engine (11 cognitive personas + pre-mortem 2× loss)
  3. Phase 1 Engines (ALIE Active Listening, ECSE Social Calibration, PMCE Persuasion)
  4. Phase 2 Engines (DCVE Domain Competence, NACE Narrative Arc, LSCE Endurance, PACE Adaptation)

Zero-Bridge Synchronous Memory Rule:
  Embeds live inference state into the physical 64-byte AMSV vector,
  verifies layout integrity with AMSVIntegrityChecker, and checkpoints both
  model weights and AMSV memory snapshots with SHA-256 verification.
"""

from __future__ import annotations
import os
import sys
import torch
from typing import Dict, Any

from amsv.python.amsv_integrity_checker import AMSVIntegrityChecker
from training.checkpoint_sync import CheckpointManager
from training.train_rvce_cognitive_ai import (
    RVCECognitiveNetwork,
    RVCETrainer,
    generate_structured_rvce_batch
)
from training.train_hcte_cognitive_ai import (
    HCTECognitiveNetwork,
    HCTETrainer,
    generate_hcte_curriculum_batch
)
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


def run_cognitive_training(
    epochs_per_engine: int = 5,
    steps_per_epoch: int = 8,
    batch_size: int = 8,
    checkpoint_dir: str = "checkpoints"
) -> Dict[str, Any]:
    os.makedirs(checkpoint_dir, exist_ok=True)
    amsv_buffer = bytearray(64)
    ckpt_mgr = CheckpointManager(checkpoint_dir=checkpoint_dir)

    print("=" * 70)
    print("SOLO ROCK CENTRAL COMMAND — MASTER COGNITIVE NEURAL TRAINING")
    print("=" * 70)

    # 0. Pre-flight AMSV Layout Verification
    print("\n[PRE-FLIGHT] Auditing AMSV 64-byte Physical Memory Layout...")
    layout_errors = AMSVIntegrityChecker.audit_layout()
    if layout_errors:
        raise RuntimeError(f"AMSV Layout Audit Failed: {layout_errors}")
    print("  -> AMSV 64-Byte Tile Audit PASSED: 0 collisions, 0 gaps.")

    results: Dict[str, Any] = {}

    # 1. Train RVCE Cognitive AI
    print("\n[TRAINING 1/4] RVCE Cognitive AI (6 Core Faculties)...")
    rvce_model = RVCECognitiveNetwork(vocab_size=1000, d_model=128, nhead=4, num_layers=2)
    rvce_trainer = RVCETrainer(model=rvce_model, amsv_buffer=amsv_buffer)

    for epoch in range(1, epochs_per_engine + 1):
        for step in range(steps_per_epoch):
            tokens, targets = generate_structured_rvce_batch(batch_size=batch_size, seq_len=32)
            metrics = rvce_trainer.train_step(tokens, targets)
        print(f"  Epoch {epoch}/{epochs_per_engine} — Total Loss: {metrics.get('total_loss', 0.0):.4f}")

    rvce_ckpt = ckpt_mgr.save_checkpoint(
        rvce_model, epoch=epochs_per_engine, step=epochs_per_engine * steps_per_epoch,
        metrics=metrics, filename="rvce_cognitive_trained.pt"
    )
    results["rvce"] = {"checkpoint": rvce_ckpt, "final_loss": metrics.get("total_loss", 0.0)}

    # 2. Train HCTE (Human Cognitive Thinking Engine)
    print("\n[TRAINING 2/4] HCTE (11 Cognitive Personas + Pre-Mortem 2x)...")
    hcte_model = HCTECognitiveNetwork(vocab_size=1000, d_model=128, nhead=4, num_layers=2)
    hcte_trainer = HCTETrainer(model=hcte_model, amsv_buffer=amsv_buffer)

    for epoch in range(1, epochs_per_engine + 1):
        for step in range(steps_per_epoch):
            tokens, targets = generate_hcte_curriculum_batch(batch_size=batch_size, seq_len=32)
            metrics = hcte_trainer.train_step(tokens, targets)
        print(f"  Epoch {epoch}/{epochs_per_engine} — Total Loss: {metrics.get('total_loss', 0.0):.4f}")

    hcte_ckpt = ckpt_mgr.save_checkpoint(
        hcte_model, epoch=epochs_per_engine, step=epochs_per_engine * steps_per_epoch,
        metrics=metrics, filename="hcte_cognitive_trained.pt"
    )
    results["hcte"] = {"checkpoint": hcte_ckpt, "final_loss": metrics.get("total_loss", 0.0)}

    # 3. Train Phase 1 Engines (ALIE + ECSE + PMCE)
    print("\n[TRAINING 3/4] Phase 1 Engines (ALIE Listening, ECSE Social, PMCE Persuasion)...")
    p1_model = Phase1CognitiveNetwork(vocab_size=1000, d_model=128, nhead=4, num_layers=2)
    p1_trainer = Phase1CognitiveTrainer(model=p1_model, amsv_buffer=amsv_buffer, checkpoint_dir=checkpoint_dir)

    for epoch in range(1, epochs_per_engine + 1):
        for step in range(steps_per_epoch):
            tokens, targets = generate_phase1_curriculum_batch(batch_size=batch_size, seq_len=32)
            metrics = p1_trainer.train_step(tokens, targets)
        # Validation on held-out split
        val_tokens, val_targets = generate_phase1_curriculum_batch(batch_size=batch_size, seq_len=32)
        val_metrics = p1_trainer.validate_step(val_tokens, val_targets)
        print(f"  Epoch {epoch}/{epochs_per_engine} — Train Loss: {metrics.get('total_weighted_loss', 0.0):.4f} | Val Loss: {val_metrics.get('val_total_weighted_loss', 0.0):.4f}")

    p1_ckpt = ckpt_mgr.save_checkpoint(
        p1_model, epoch=epochs_per_engine, step=epochs_per_engine * steps_per_epoch,
        metrics=metrics, filename="phase1_engines_trained.pt"
    )
    results["phase1"] = {"checkpoint": p1_ckpt, "final_loss": metrics.get("total_weighted_loss", 0.0)}

    # 4. Train Phase 2 Engines (DCVE + NACE + LSCE + PACE)
    print("\n[TRAINING 4/4] Phase 2 Engines (DCVE Competence, NACE Narrative, LSCE Endurance, PACE Adaptation)...")
    p2_model = Phase2CognitiveNetwork(vocab_size=1000, d_model=128, nhead=4, num_layers=2)
    p2_trainer = Phase2CognitiveTrainer(model=p2_model, amsv_buffer=amsv_buffer, checkpoint_dir=checkpoint_dir)

    for epoch in range(1, epochs_per_engine + 1):
        for step in range(steps_per_epoch):
            tokens, targets = generate_phase2_curriculum_batch(batch_size=batch_size, seq_len=32)
            metrics = p2_trainer.train_step(tokens, targets)
        # Validation on held-out split
        val_tokens, val_targets = generate_phase2_curriculum_batch(batch_size=batch_size, seq_len=32)
        val_metrics = p2_trainer.validate_step(val_tokens, val_targets)
        print(f"  Epoch {epoch}/{epochs_per_engine} — Train Loss: {metrics.get('total_weighted_loss', 0.0):.4f} | Val Loss: {val_metrics.get('val_total_weighted_loss', 0.0):.4f}")

    p2_ckpt = ckpt_mgr.save_checkpoint(
        p2_model, epoch=epochs_per_engine, step=epochs_per_engine * steps_per_epoch,
        metrics=metrics, filename="phase2_engines_trained.pt"
    )
    results["phase2"] = {"checkpoint": p2_ckpt, "final_loss": metrics.get("total_weighted_loss", 0.0)}

    # 5. AMSV Buffer Snapshot & Validation
    print("\n[AMSV CHECKPOINT] Validating & Serializing Active AMSV State Vector...")
    is_valid, issues = AMSVIntegrityChecker.validate_buffer(amsv_buffer)
    if not is_valid:
        raise RuntimeError(f"AMSV buffer validation failed: {issues}")

    amsv_ckpt = ckpt_mgr.save_amsv_state(amsv_buffer, filename="master_cognitive_amsv.bin")
    results["amsv_snapshot"] = amsv_ckpt
    print(f"  -> AMSV 64-Byte Snapshot saved: {amsv_ckpt} (SHA-256 verified)")

    print("\n" + "=" * 70)
    print("ALL 4 COGNITIVE NEURAL SYSTEMS SUCCESSFULLY TRAINED & CHECKPOINTED")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_cognitive_training()
