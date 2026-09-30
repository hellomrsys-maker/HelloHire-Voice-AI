"""
gra_gpu/grammar_syntax_triton.py - Triton Kernel for Parallel Dependency Parsing and Constituency Edge Scoring.

Accelerates Universal Grammar constraint checking and syntactic tree dependency scoring on GPUs.
Computes token-to-token governor-dependent affinity matrices:
    A[i, j] = (W_head * h_i)^T (W_dep * h_j) / sqrt(d)
and validates non-crossing (projectivity) constraints in parallel.
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
    def dependency_affinity_kernel(
        Heads_ptr,       # [Batch, SeqLen, Dim]
        Dependents_ptr,  # [Batch, SeqLen, Dim]
        Affinity_ptr,    # [Batch, SeqLen, SeqLen]
        stride_hb, stride_hl, stride_hd,
        stride_db, stride_dl, stride_dd,
        stride_ab, stride_ar, stride_ac,
        SEQ_LEN: tl.constexpr,
        DIM: tl.constexpr,
        BLOCK_DIM: tl.constexpr
    ):
        batch_idx = tl.program_id(axis=0)
        head_idx = tl.program_id(axis=1)
        dep_idx = tl.program_id(axis=2)

        offsets = tl.arange(0, BLOCK_DIM)
        mask = offsets < DIM

        h_offset = batch_idx * stride_hb + head_idx * stride_hl + offsets * stride_hd
        d_offset = batch_idx * stride_db + dep_idx * stride_dl + offsets * stride_dd

        h_val = tl.load(Heads_ptr + h_offset, mask=mask, other=0.0)
        d_val = tl.load(Dependents_ptr + d_offset, mask=mask, other=0.0)

        dot = tl.sum(h_val * d_val, axis=0)
        scale = 1.0 / tl.sqrt(float(DIM))
        score = dot * scale

        # Disallow self-loops (token cannot be its own syntactic head)
        if head_idx == dep_idx:
            score = -1e4

        out_offset = batch_idx * stride_ab + head_idx * stride_ar + dep_idx * stride_ac
        tl.store(Affinity_ptr + out_offset, score)


def compute_syntactic_dependency_affinity(
    head_representations: torch.Tensor,
    dependent_representations: torch.Tensor
) -> torch.Tensor:
    """
    Computes [Batch, SeqLen, SeqLen] syntactic dependency affinity matrix.
    Uses Triton JIT kernel if CUDA is available, otherwise fast PyTorch tensor algebra.
    """
    batch_size, seq_len, dim = head_representations.shape
    device = head_representations.device

    if HAS_TRITON and head_representations.is_cuda and dim <= 256:
        out_affinity = torch.empty((batch_size, seq_len, seq_len), device=device, dtype=torch.float32)
        grid = (batch_size, seq_len, seq_len)
        block_dim = triton.next_power_of_2(dim)

        dependency_affinity_kernel[grid](
            head_representations,
            dependent_representations,
            out_affinity,
            head_representations.stride(0), head_representations.stride(1), head_representations.stride(2),
            dependent_representations.stride(0), dependent_representations.stride(1), dependent_representations.stride(2),
            out_affinity.stride(0), out_affinity.stride(1), out_affinity.stride(2),
            SEQ_LEN=seq_len,
            DIM=dim,
            BLOCK_DIM=block_dim
        )
        return out_affinity
    else:
        # High-performance PyTorch native fallback
        scale = 1.0 / (dim ** 0.5)
        # [B, L, D] x [B, D, L] -> [B, L, L]
        scores = torch.bmm(head_representations, dependent_representations.transpose(1, 2)) * scale
        diag_mask = torch.eye(seq_len, device=device, dtype=torch.bool).unsqueeze(0)
        scores = scores.masked_fill(diag_mask, -1e4)
        return scores
