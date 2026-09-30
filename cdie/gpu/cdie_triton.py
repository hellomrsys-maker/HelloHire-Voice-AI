"""
cdie_triton.py — Fused GPU Scoring for Cross-Domain Idea Transfer (CDIE GPU Layer)

Computes GPU-accelerated manifold distance and conceptual divergence between domain representations.
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
    def cdie_manifold_fusion_kernel(
        analogy_ptr, bridge_ptr, lateral_ptr, dist_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        a = tl.load(analogy_ptr + offs, mask=mask, other=0.0)
        b = tl.load(bridge_ptr + offs, mask=mask, other=0.0)
        l = tl.load(lateral_ptr + offs, mask=mask, other=0.0)
        d = tl.load(dist_ptr + offs, mask=mask, other=0.0)

        # Cross-Domain Transfer Formula: 0.35*a + 0.25*b + 0.25*l + 0.15*d
        comp = tl.math.clamp(0.35 * a + 0.25 * b + 0.25 * l + 0.15 * d, 0.0, 1.0)
        tl.store(out_ptr + offs, comp, mask=mask)


def run_cdie_manifold_scoring(
    analogy: torch.Tensor,
    bridge: torch.Tensor,
    lateral: torch.Tensor,
    distance: torch.Tensor
) -> torch.Tensor:
    N = analogy.numel()
    device = analogy.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        cdie_manifold_fusion_kernel[grid](
            analogy, bridge, lateral, distance, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    return torch.clamp(0.35 * analogy + 0.25 * bridge + 0.25 * lateral + 0.15 * distance, 0.0, 1.0)
