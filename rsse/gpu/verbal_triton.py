"""
verbal_triton.py - Triton Block-Level Parallel Kernel for Recruitment Verbal Communication.

Computes parallel STAR method alignment scores and jargon density matrix across
batched candidate response embeddings and golden interview response archetypes.
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
    def star_alignment_kernel(
        cand_ptr,
        golden_ptr,
        out_ptr,
        batch_size: tl.constexpr,
        d_model: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        """
        Computes cosine similarity between candidate response embeddings and
        golden STAR rubric reference vectors along block dimension.
        """
        pid = tl.program_id(0)
        offsets = tl.arange(0, BLOCK_SIZE)
        mask = offsets < d_model

        c_vals = tl.load(cand_ptr + pid * d_model + offsets, mask=mask, other=0.0)
        g_vals = tl.load(golden_ptr + pid * d_model + offsets, mask=mask, other=0.0)

        dot = tl.sum(c_vals * g_vals, axis=0)
        norm_c = tl.sqrt(tl.sum(c_vals * c_vals, axis=0) + 1e-8)
        norm_g = tl.sqrt(tl.sum(g_vals * g_vals, axis=0) + 1e-8)

        sim = dot / (norm_c * norm_g)
        tl.store(out_ptr + pid, sim)


def run_star_triton_match(cand_embeddings: torch.Tensor, golden_archetypes: torch.Tensor) -> torch.Tensor:
    """
    High-level dispatch function for STAR alignment matching.
    Falls back to optimized PyTorch tensordot when running on non-CUDA / CPU environments.
    """
    batch_size, d_model = cand_embeddings.shape
    device = cand_embeddings.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(batch_size, device=device, dtype=torch.float32)
        grid = (batch_size,)
        star_alignment_kernel[grid](
            cand_embeddings,
            golden_archetypes,
            out,
            batch_size=batch_size,
            d_model=d_model,
            BLOCK_SIZE=triton.next_power_of_2(d_model)
        )
        return out
    else:
        # Fallback to PyTorch vector cosine similarity
        return torch.cosine_similarity(cand_embeddings, golden_archetypes, dim=-1)
