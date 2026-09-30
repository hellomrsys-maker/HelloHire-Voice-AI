"""
nace_triton.py — Fused GPU Scoring for Narrative Arc & Coherence (NACE GPU Layer)

Computes GPU-accelerated STAR structure alignment and cross-turn contradiction penalty.
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
    def nace_narrative_fusion_kernel(
        theme_ptr, climax_ptr, momentum_ptr, contra_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        th = tl.load(theme_ptr + offs, mask=mask, other=0.0)
        cl = tl.load(climax_ptr + offs, mask=mask, other=0.0)
        mo = tl.load(momentum_ptr + offs, mask=mask, other=0.0)
        co = tl.load(contra_ptr + offs, mask=mask, other=0.0)

        # Formula: 0.35 * theme + 0.35 * climax + 0.30 * momentum - 0.50 * contradiction
        comp = tl.math.clamp(0.35 * th + 0.35 * cl + 0.30 * mo - 0.50 * co, 0.0, 1.0)
        tl.store(out_ptr + offs, comp, mask=mask)


def run_nace_narrative_scoring(
    theme: torch.Tensor,
    climax: torch.Tensor,
    momentum: torch.Tensor,
    contradiction: torch.Tensor
) -> torch.Tensor:
    N = theme.numel()
    device = theme.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        nace_narrative_fusion_kernel[grid](
            theme, climax, momentum, contradiction, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    return torch.clamp(0.35 * theme + 0.35 * climax + 0.30 * momentum - 0.50 * contradiction, 0.0, 1.0)
