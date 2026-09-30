"""
rvce_triton.py - Fused Block-Level GPU Kernel for RVCE Cognitive Scoring

Computes parallel scoring across all 6 cognitive faculties:
Thinking, Concentration, Recall, Creativity, Imagination, Verbal
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
    def fused_cognitive_trait_scoring_kernel(
        cand_ptr,       # [batch_size, d_model]
        rubric_ptr,     # [6, d_model]
        out_ptr,        # [batch_size, 6]
        batch_size: tl.constexpr,
        d_model: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid_m = tl.program_id(0) # candidate batch index
        pid_k = tl.program_id(1) # cognitive faculty index (0 to 5)

        offsets = tl.arange(0, BLOCK_SIZE)
        mask = offsets < d_model

        c_vals = tl.load(cand_ptr + pid_m * d_model + offsets, mask=mask, other=0.0)
        r_vals = tl.load(rubric_ptr + pid_k * d_model + offsets, mask=mask, other=0.0)

        dot = tl.sum(c_vals * r_vals, axis=0)
        norm_c = tl.sqrt(tl.sum(c_vals * c_vals, axis=0) + 1e-8)
        norm_r = tl.sqrt(tl.sum(r_vals * r_vals, axis=0) + 1e-8)

        sim = dot / (norm_c * norm_r)
        sim_norm = tl.math.clamp(0.5 * (sim + 1.0), 0.0, 1.0)
        tl.store(out_ptr + pid_m * 6 + pid_k, sim_norm)


def run_rvce_gpu_scoring(
    cand_embeddings: torch.Tensor,
    rubric_embeddings: torch.Tensor
) -> torch.Tensor:
    """
    Computes [batch_size, 6] cognitive faculty matrix.
    Uses fused Triton kernel if CUDA and Triton available, otherwise optimized PyTorch.
    """
    batch_size, d_model = cand_embeddings.shape
    device = cand_embeddings.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty((batch_size, 6), device=device, dtype=torch.float32)
        grid = (batch_size, 6)
        block_size = triton.next_power_of_2(d_model)
        fused_cognitive_trait_scoring_kernel[grid](
            cand_embeddings,
            rubric_embeddings,
            out,
            batch_size=batch_size,
            d_model=d_model,
            BLOCK_SIZE=block_size
        )
        return out

    # High-performance PyTorch fallback
    cand_norm = torch.nn.functional.normalize(cand_embeddings, p=2, dim=-1)
    rubric_norm = torch.nn.functional.normalize(rubric_embeddings, p=2, dim=-1)
    # [batch_size, d_model] @ [d_model, 6] -> [batch_size, 6]
    sim = torch.matmul(cand_norm, rubric_norm.t())
    sim_clamped = torch.clamp(0.5 * (sim + 1.0), 0.0, 1.0)
    return sim_clamped
