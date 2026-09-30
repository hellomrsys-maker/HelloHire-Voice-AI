"""
pace_triton.py — Fused GPU Scoring for Pacing & Adaptation Calibration (PACE GPU Layer)

Computes GPU-accelerated vocabulary adaptation, register shift, and length compliance.
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
    def pace_adaptation_fusion_kernel(
        vocab_ptr, length_ptr, register_ptr, recovery_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        v = tl.load(vocab_ptr + offs, mask=mask, other=0.0)
        l = tl.load(length_ptr + offs, mask=mask, other=0.0)
        r = tl.load(register_ptr + offs, mask=mask, other=0.0)
        rec = tl.load(recovery_ptr + offs, mask=mask, other=0.0)

        # Formula: 0.30 * vocab + 0.30 * length + 0.25 * register + 0.15 * recovery
        comp = tl.math.clamp(0.30 * v + 0.30 * l + 0.25 * r + 0.15 * rec, 0.0, 1.0)
        tl.store(out_ptr + offs, comp, mask=mask)


def run_pace_adaptation_scoring(
    vocab_adaptation: torch.Tensor,
    length_compliance: torch.Tensor,
    register_shift: torch.Tensor,
    recovery_composure: torch.Tensor
) -> torch.Tensor:
    N = vocab_adaptation.numel()
    device = vocab_adaptation.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        pace_adaptation_fusion_kernel[grid](
            vocab_adaptation, length_compliance, register_shift, recovery_composure, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    return torch.clamp(0.30 * vocab_adaptation + 0.30 * length_compliance + 0.25 * register_shift + 0.15 * recovery_composure, 0.0, 1.0)
