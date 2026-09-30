"""
test_multilingual_acoustic_prosody_model.py - Validation test for genuine acoustic multilingual model.
"""

import os
import torch
from training.train_multilingual_acoustic_prosody import AcousticProsodyNeuralNet
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_multilingual_acoustic_checkpoint_integrity():
    ckpt_path = "checkpoints/multilingual_acoustic_prosody_model.pt"
    assert os.path.exists(ckpt_path), f"Checkpoint missing: {ckpt_path}"

    ckpt = torch.load(ckpt_path, weights_only=True)
    assert "model_state_dict" in ckpt
    count = ckpt.get("trained_samples_count", ckpt.get("trained_videos_count", 0))
    assert count == 16

    model = AcousticProsodyNeuralNet(input_dim=4, hidden_dim=64, num_layers=2)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    dummy_input = torch.randn(1, 100, 4)
    with torch.no_grad():
        texture_logits, f0_pred, amsv_proj = model(dummy_input)

    assert texture_logits.shape == (1, 4)
    assert f0_pred.shape == (1, 100, 1)
    assert amsv_proj.shape == (1, 16)


def test_amsv_zero_bridge_memory_state():
    amsv = AMSVEmbeddedView()
    assert amsv._view.nbytes == 64
    fluency = amsv.get_prosody_fluency()
    assert 0.0 <= fluency <= 1.0
