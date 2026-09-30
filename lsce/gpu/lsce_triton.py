"""
lsce_triton.py — Fused GPU Scoring for Long-Span Cognitive Endurance (LSCE GPU Layer)

Computes GPU-accelerated stamina slopes and fatigue trajectories across interview turns.
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
    def lsce_endurance_fusion_kernel(
        slope_ptr, ttr_ptr, resilience_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        s = tl.load(slope_ptr + offs, mask=mask, other=0.0)
        t = tl.load(ttr_ptr + offs, mask=mask, other=0.0)
        r = tl.load(resilience_ptr + offs, mask=mask, other=0.0)

        # Formula: 0.40 * slope + 0.30 * ttr + 0.30 * resilience
        comp = tl.math.clamp(0.40 * s + 0.30 * t + 0.30 * r, 0.0, 1.0)
        tl.store(out_ptr + offs, comp, mask=mask)


def run_lsce_endurance_scoring(
    stamina_slope: torch.Tensor,
    ttr_diversity: torch.Tensor,
    concentration_resilience: torch.Tensor
) -> torch.Tensor:
    N = stamina_slope.numel()
    device = stamina_slope.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        lsce_endurance_fusion_kernel[grid](
            stamina_slope, ttr_diversity, concentration_resilience, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    return torch.clamp(0.40 * stamina_slope + 0.30 * ttr_diversity + 0.30 * concentration_resilience, 0.0, 1.0)
