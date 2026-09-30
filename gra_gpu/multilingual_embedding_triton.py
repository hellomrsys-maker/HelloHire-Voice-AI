"""
multilingual_embedding_triton.py - Triton GPU Kernel for Parallel Cross-Lingual Semantic Space Alignment.

Computes parallel Procrustes orthogonal projection and cosine similarity
between source language sentence representations and target universal semantic space.
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
    def cross_lingual_projection_kernel(
        Source_ptr,       # [Batch, Dim]
        Orthogonal_ptr,   # [Dim, Dim]
        Target_ptr,       # [Batch, Dim]
        stride_sb, stride_sd,
        stride_om, stride_on,
        stride_tb, stride_td,
        DIM: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        batch_idx = tl.program_id(axis=0)
        col_idx = tl.program_id(axis=1)

        offsets = tl.arange(0, BLOCK_SIZE)
        mask = offsets < DIM

        s_offset = batch_idx * stride_sb + offsets * stride_sd
        o_offset = offsets * stride_om + col_idx * stride_on

        s_val = tl.load(Source_ptr + s_offset, mask=mask, other=0.0)
        o_val = tl.load(Orthogonal_ptr + o_offset, mask=mask, other=0.0)

        projected = tl.sum(s_val * o_val, axis=0)

        t_offset = batch_idx * stride_tb + col_idx * stride_td
        tl.store(Target_ptr + t_offset, projected)


def project_multilingual_space(
    source_embeddings: torch.Tensor,
    orthogonal_matrix: torch.Tensor
) -> torch.Tensor:
    """
    Projects source language embeddings into universal multilingual semantic space.
    Uses Triton JIT kernel if CUDA is available, otherwise PyTorch tensor math.
    """
    batch_size, dim = source_embeddings.shape
    device = source_embeddings.device

    if HAS_TRITON and source_embeddings.is_cuda and dim <= 256:
        out_projected = torch.empty((batch_size, dim), device=device, dtype=torch.float32)
        grid = (batch_size, dim)
        block_size = triton.next_power_of_2(dim)

        cross_lingual_projection_kernel[grid](
            source_embeddings,
            orthogonal_matrix,
            out_projected,
            source_embeddings.stride(0), source_embeddings.stride(1),
            orthogonal_matrix.stride(0), orthogonal_matrix.stride(1),
            out_projected.stride(0), out_projected.stride(1),
            DIM=dim,
            BLOCK_SIZE=block_size
        )
        return out_projected
    else:
        # High-performance PyTorch fallback
        return torch.matmul(source_embeddings, orthogonal_matrix)
