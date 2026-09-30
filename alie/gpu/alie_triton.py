"""
alie_triton.py — Fused GPU Scoring for Active Listening Metrics (ALIE GPU Layer)

Computes parallel Q-A embedding cosine similarity for batch candidate responses
and fuses 5 listening dimensions into composite scores.
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
    def alie_qa_similarity_kernel(
        q_ptr, a_ptr, out_ptr,
        d_model: tl.constexpr,
        BLOCK_SIZE: tl.constexpr
    ):
        pid = tl.program_id(0)
        offs = tl.arange(0, BLOCK_SIZE)
        mask = offs < d_model
        q_vals = tl.load(q_ptr + pid * d_model + offs, mask=mask, other=0.0)
        a_vals = tl.load(a_ptr + pid * d_model + offs, mask=mask, other=0.0)
        dot = tl.sum(q_vals * a_vals, axis=0)
        norm_q = tl.sqrt(tl.sum(q_vals * q_vals, axis=0) + 1e-8)
        norm_a = tl.sqrt(tl.sum(a_vals * a_vals, axis=0) + 1e-8)
        sim = tl.math.clamp(0.5 * (dot / (norm_q * norm_a) + 1.0), 0.0, 1.0)
        tl.store(out_ptr + pid, sim)


def run_alie_qa_scoring(
    question_embeddings: torch.Tensor,   # [B, d_model]
    answer_embeddings: torch.Tensor      # [B, d_model]
) -> torch.Tensor:
    """
    Returns [B] cosine similarity scores in [0, 1] between each Q-A pair.
    """
    B, d = question_embeddings.shape
    device = question_embeddings.device

    if HAS_TRITON and device.type == "cuda":
        out = torch.empty(B, device=device, dtype=torch.float32)
        grid = (B,)
        alie_qa_similarity_kernel[grid](
            question_embeddings, answer_embeddings, out,
            d_model=d, BLOCK_SIZE=triton.next_power_of_2(d)
        )
        return out

    # PyTorch fallback
    q_norm = torch.nn.functional.normalize(question_embeddings, p=2, dim=-1)
    a_norm = torch.nn.functional.normalize(answer_embeddings, p=2, dim=-1)
    sim = (q_norm * a_norm).sum(dim=-1)
    return torch.clamp(0.5 * (sim + 1.0), 0.0, 1.0)
