"""
pmce_triton.py — Fused GPU Scoring for Rhetorical & Persuasion Dimensions (PMCE GPU Layer)

Fused GPU kernel for parallel calculation of the 5 rhetorical vectors:
  [Logos, Ethos, Pathos, Kairos, CTA] -> Composite Persuasion Score
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
    def pmce_rhetorical_fusion_kernel(
        logos_ptr, ethos_ptr, pathos_ptr, kairos_ptr, cta_ptr, out_ptr,
        n_elements: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        l = tl.load(logos_ptr + offs, mask=mask, other=0.0)
        e = tl.load(ethos_ptr + offs, mask=mask, other=0.0)
        p = tl.load(pathos_ptr + offs, mask=mask, other=0.0)
        k = tl.load(kairos_ptr + offs, mask=mask, other=0.0)
        c = tl.load(cta_ptr + offs, mask=mask, other=0.0)

        # Classical rhetorical weighting: Logos (30%), Ethos (25%), Pathos (20%), Kairos (10%), CTA (15%)
        comp = 0.30 * l + 0.25 * e + 0.20 * p + 0.10 * k + 0.15 * c
        tl.store(out_ptr + offs, comp, mask=mask)


def run_pmce_rhetorical_scoring(
    logos: torch.Tensor,
    ethos: torch.Tensor,
    pathos: torch.Tensor,
    kairos: torch.Tensor,
    cta: torch.Tensor
) -> torch.Tensor:
    """
    Returns [B] composite persuasion scores in [0, 1].
    """
    N = logos.numel()
    device = logos.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(N, device=device, dtype=torch.float32)
        BLOCK_SIZE = 128
        grid = (triton.cdiv(N, BLOCK_SIZE),)
        pmce_rhetorical_fusion_kernel[grid](
            logos, ethos, pathos, kairos, cta, out,
            n_elements=N, BLOCK_SIZE=BLOCK_SIZE
        )
        return out

    # PyTorch fallback
    return 0.30 * logos + 0.25 * ethos + 0.20 * pathos + 0.10 * kairos + 0.15 * cta
