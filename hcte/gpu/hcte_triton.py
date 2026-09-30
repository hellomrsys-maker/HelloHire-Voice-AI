"""
hcte_triton.py — Fused GPU Scoring for Cognitive Persona Synthesis (HCTE GPU Layer)

Computes the weighted consensus of 11 cognitive personas with 2x pre-mortem weighting
and cognitive tension variance across candidate responses.
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
    def hcte_persona_fusion_kernel(
        scores_ptr, out_gci_ptr, out_tension_ptr,
        n_personas: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = tl.arange(0, BLOCK_SIZE)
        mask = offs < n_personas
        vals = tl.load(scores_ptr + pid * n_personas + offs, mask=mask, other=0.0)

        # Persona weights: persona 4 (pre-mortem) has 2x weight
        # Weight sum: 10 * 1.0 + 1 * 2.0 = 12.0
        w = tl.where(offs == 4, 2.0, 1.0)
        weighted_sum = tl.sum(vals * w, axis=0)
        mean_val = weighted_sum / 12.0

        # Tension = variance
        diff = vals - mean_val
        var = tl.sum(diff * diff * w, axis=0) / 12.0
        tension = tl.sqrt(var + 1e-8)

        tl.store(out_gci_ptr + pid, mean_val)
        tl.store(out_tension_ptr + pid, tension)


def run_hcte_persona_scoring(persona_scores: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    persona_scores: [B, 11] tensor of persona scores.
    Returns: (global_cognitive_index [B], cognitive_tension [B])
    """
    B, N = persona_scores.shape
    device = persona_scores.device

    if HAS_TRITON and device.type == "cuda" and N == 11:
        out_gci = torch.empty(B, device=device, dtype=torch.float32)
        out_tension = torch.empty(B, device=device, dtype=torch.float32)
        grid = (B,)
        hcte_persona_fusion_kernel[grid](
            persona_scores, out_gci, out_tension,
            n_personas=11, BLOCK_SIZE=16
        )
        return out_gci, out_tension

    # PyTorch fallback
    weights = torch.ones(11, device=device)
    weights[4] = 2.0  # Pre-mortem analyst 2x weight
    weights = weights / weights.sum()

    gci = (persona_scores * weights).sum(dim=-1)
    diff = persona_scores - gci.unsqueeze(-1)
    tension = torch.sqrt((diff.pow(2) * weights).sum(dim=-1) + 1e-8)
    return gci, tension
