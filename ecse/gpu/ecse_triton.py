"""
ecse_triton.py — Fused GPU Scoring for Emotional & Social Dynamics (ECSE GPU Layer)

Computes batch social resonance and affect valence embeddings in parallel.
"""
from __future__ import annotations
import torch

try:
    import triton
    import triton.language as tl
    HAS_TRITON = True
except ImportError:
    HAS_TRITON = False

if HAS_TRITON:
    @triton.jit
    def ecse_affect_fusion_kernel(
        pos_ptr, neg_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements
        p = tl.load(pos_ptr + offs, mask=mask, other=0.0)
        n = tl.load(neg_ptr + offs, mask=mask, other=0.0)
        valence = tl.math.clamp(p - n, -1.0, 1.0)
        composite = tl.math.clamp(0.5 + valence * 0.5, 0.0, 1.0)
        tl.store(out_ptr + offs, composite, mask=mask)


def run_ecse_affect_scoring(
    positive_signals: torch.Tensor,
    negative_signals: torch.Tensor
) -> torch.Tensor:
    """
    Returns [B] composite affect scores in [0, 1].
    """
    N = positive_signals.numel()
    device = positive_signals.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        ecse_affect_fusion_kernel[grid](
            positive_signals, negative_signals, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    valence = torch.clamp(positive_signals - negative_signals, -1.0, 1.0)
    return torch.clamp(0.5 + valence * 0.5, 0.0, 1.0)
