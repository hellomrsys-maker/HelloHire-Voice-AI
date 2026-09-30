"""
scenario_triton_match.py - Triton GPU Kernel for Candidate-Scenario Competency Vector Alignment.

Computes high-throughput parallel inner products and scaled Softmax projections
between candidate utterance representations and 8-scenario competency rubrics.
"""

import triton
import triton.language as tl
import torch

@triton.jit
def scenario_vector_align_kernel(
    Cand_ptr,        # [Batch, Dim] candidate representation vectors
    Archetype_ptr,   # [NumArchetypes, Dim] target benchmark vectors
    Out_Scores_ptr,  # [Batch, NumArchetypes] alignment scores
    stride_cb,
    stride_cd,
    stride_ad,
    stride_ob,
    stride_oa,
    DIM: tl.constexpr,
    NUM_ARCHETYPES: tl.constexpr,
    BLOCK_SIZE: tl.constexpr
):
    batch_idx = tl.program_id(axis=0)
    arch_idx = tl.program_id(axis=1)

    # Accumulate dot product across DIM
    offsets = tl.arange(0, BLOCK_SIZE)
    cand_offset = batch_idx * stride_cb + offsets * stride_cd
    arch_offset = arch_idx * stride_ad + offsets

    c_vals = tl.load(Cand_ptr + cand_offset, mask=offsets < DIM, other=0.0)
    a_vals = tl.load(Archetype_ptr + arch_offset, mask=offsets < DIM, other=0.0)

    dot = tl.sum(c_vals * a_vals, axis=0)

    # Store scaled cosine score
    out_offset = batch_idx * stride_ob + arch_idx * stride_oa
    tl.store(Out_Scores_ptr + out_offset, dot * (1.0 / 16.0))


def launch_scenario_vector_align(
    candidates: torch.Tensor,
    archetypes: torch.Tensor
) -> torch.Tensor:
    """
    Host wrapper for launching scenario_vector_align_kernel.
    """
    assert candidates.is_cuda and archetypes.is_cuda
    batch_size, dim = candidates.shape
    num_archetypes, _ = archetypes.shape

    out_scores = torch.empty((batch_size, num_archetypes), device=candidates.device, dtype=torch.float32)

    grid = (batch_size, num_archetypes)
    scenario_vector_align_kernel[grid](
        candidates,
        archetypes,
        out_scores,
        stride_cb=candidates.stride(0),
        stride_cd=candidates.stride(1),
        stride_ad=archetypes.stride(0),
        stride_ob=out_scores.stride(0),
        stride_oa=out_scores.stride(1),
        DIM=dim,
        NUM_ARCHETYPES=num_archetypes,
        BLOCK_SIZE=triton.next_power_of_2(dim)
    )
    return out_scores
