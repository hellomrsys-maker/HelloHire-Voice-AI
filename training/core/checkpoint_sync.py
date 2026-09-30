"""
checkpoint_sync.py - Cross-Language Checkpoint Synchronization & Model Export.

Provides checkpoint saving, metadata versioning, and export mechanisms (TorchScript / ONNX)
for real-time zero-overhead inference in the C++ engine core.
"""

from __future__ import annotations
import os
import json
import hashlib
from typing import Dict, Any, Optional
import torch

class CheckpointManager:
    """
    Manages versioned checkpoints and exports for C++ engine integration.
    """

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save_checkpoint(
        self,
        model: torch.nn.Module,
        epoch: int,
        step: int,
        metrics: Dict[str, float],
        filename: str = "multitask_checkpoint.pt"
    ) -> str:
        filepath = os.path.join(self.checkpoint_dir, filename)
        state_dict = model.state_dict()

        # Compute SHA-256 fingerprint of weights
        hasher = hashlib.sha256()
        for key in sorted(state_dict.keys()):
            hasher.update(key.encode("utf-8"))
            hasher.update(state_dict[key].cpu().numpy().tobytes())
        weight_hash = hasher.hexdigest()

        checkpoint_data = {
            "epoch": epoch,
            "step": step,
            "metrics": metrics,
            "weight_hash": weight_hash,
            "state_dict": state_dict
        }

        torch.save(checkpoint_data, filepath)

        # Write sidecar JSON metadata
        meta_path = filepath + ".json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "epoch": epoch,
                "step": step,
                "metrics": metrics,
                "weight_hash": weight_hash,
                "model_class": model.__class__.__name__
            }, f, indent=2)

        return filepath

    def load_checkpoint(
        self,
        model: torch.nn.Module,
        filepath: str
    ) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Checkpoint file not found: {filepath}")

        checkpoint_data = torch.load(filepath, map_location="cpu")
        model.load_state_dict(checkpoint_data["state_dict"])
        return {
            "epoch": checkpoint_data.get("epoch", 0),
            "step": checkpoint_data.get("step", 0),
            "metrics": checkpoint_data.get("metrics", {}),
            "weight_hash": checkpoint_data.get("weight_hash", "")
        }

    def export_torchscript(
        self,
        model: torch.nn.Module,
        sample_input: torch.Tensor,
        export_filename: str = "multitask_model.ts"
    ) -> str:
        """
        Exports PyTorch model to TorchScript for direct C++ Torch runtime execution.
        """
        model.eval()
        export_path = os.path.join(self.checkpoint_dir, export_filename)
        with torch.no_grad():
            traced_model = torch.jit.trace(model, sample_input)
            traced_model.save(export_path)
        return export_path

    def save_amsv_state(self, buffer: bytearray, filename: str = "amsv_state.bin") -> str:
        """
        Saves the raw 64-byte AMSV memory state vector to a binary file with SHA-256 fingerprint.
        """
        filepath = os.path.join(self.checkpoint_dir, filename)
        if len(buffer) < 64:
            raise ValueError(f"AMSV buffer must be at least 64 bytes, got {len(buffer)}")
        raw = bytes(buffer[:64])
        with open(filepath, "wb") as f:
            f.write(raw)

        hasher = hashlib.sha256(raw)
        meta_path = filepath + ".json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "size_bytes": 64,
                "sha256": hasher.hexdigest(),
                "hex": raw.hex()
            }, f, indent=2)
        return filepath

    def load_amsv_state(self, buffer: bytearray, filepath: str) -> None:
        """
        Restores raw 64-byte AMSV state into the in-memory buffer in-place.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"AMSV state file not found: {filepath}")
        with open(filepath, "rb") as f:
            data = f.read(64)
        if len(data) < 64:
            raise ValueError(f"AMSV state file {filepath} corrupt (expected 64 bytes, got {len(data)})")
        buffer[:64] = data
