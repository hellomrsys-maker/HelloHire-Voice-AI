"""
prosody_attention.py — Triton GPU Kernel for Parallel Multi-Head Prosody Attention.
Computes multi-head attention weights over acoustic prosodic temporal frames.
"""

import torch
try:
    import triton
    import triton.language as tl
    HAS_TRITON = True
except ImportError:
    HAS_TRITON = False


if HAS_TRITON:
    @triton.jit
    def _prosody_attention_fwd_kernel(
        Q, K, V, Out,
        stride_qz, stride_qh, stride_qm, stride_qk,
        stride_kz, stride_kh, stride_kn, stride_kk,
        stride_vz, stride_vh, stride_vn, stride_vk,
        stride_oz, stride_oh, stride_om, stride_ok,
        Z, H, N_CTX,
        BLOCK_M: tl.constexpr, BLOCK_DMODEL: tl.constexpr,
        BLOCK_N: tl.constexpr,
    ):
        start_m = tl.program_id(0)
        off_hz = tl.program_id(1)
        off_z = off_hz // H
        off_h = off_hz % H

        # Initialize offsets
        offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
        offs_n = tl.arange(0, BLOCK_N)
        offs_d = tl.arange(0, BLOCK_DMODEL)

        q_ptrs = Q + off_z * stride_qz + off_h * stride_qh + (offs_m[:, None] * stride_qm + offs_d[None, :] * stride_qk)
        k_ptrs = K + off_z * stride_kz + off_h * stride_kh + (offs_n[:, None] * stride_kn + offs_d[None, :] * stride_kk)
        v_ptrs = V + off_z * stride_vz + off_h * stride_vh + (offs_n[:, None] * stride_vn + offs_d[None, :] * stride_vk)
        out_ptrs = Out + off_z * stride_oz + off_h * stride_oh + (offs_m[:, None] * stride_om + offs_d[None, :] * stride_ok)

        # Load Q
        q = tl.load(q_ptrs, mask=offs_m[:, None] < N_CTX, other=0.0)

        # Compute Attention
        m_i = tl.zeros([BLOCK_M], dtype=tl.float32) - float("inf")
        l_i = tl.zeros([BLOCK_M], dtype=tl.float32)
        acc = tl.zeros([BLOCK_M, BLOCK_DMODEL], dtype=tl.float32)

        scale = 1.0 / (BLOCK_DMODEL ** 0.5)

        for start_n in range(0, N_CTX, BLOCK_N):
            start_n = tl.multiple_of(start_n, BLOCK_N)
            k = tl.load(k_ptrs + start_n * stride_kn, mask=(start_n + offs_n[:, None]) < N_CTX, other=0.0)
            v = tl.load(v_ptrs + start_n * stride_vn, mask=(start_n + offs_n[:, None]) < N_CTX, other=0.0)

            # Dot product QK^T
            qk = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)
            qk += tl.dot(q, tl.trans(k)) * scale

            # Online Softmax update
            m_curr = tl.maximum(m_i, tl.max(qk, 1))
            alpha = tl.exp(m_i - m_curr)
            p = tl.exp(qk - m_curr[:, None])

            l_i = l_i * alpha + tl.sum(p, 1)
            acc = acc * alpha[:, None] + tl.dot(p.to(tl.float16), v)
            m_i = m_curr

        acc = acc / l_i[:, None]
        tl.store(out_ptrs, acc, mask=offs_m[:, None] < N_CTX)


def run_prosody_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """
    Executes the Triton prosody attention kernel with PyTorch fallback.
    """
    if not HAS_TRITON or not q.is_cuda:
        # High-performance PyTorch native multi-head attention fallback
        scale = 1.0 / (q.shape[-1] ** 0.5)
        scores = torch.matmul(q, k.transpose(-2, -1)) * scale
        weights = torch.softmax(scores, dim=-1)
        return torch.matmul(weights, v)

    Z, H, N_CTX, D_MODEL = q.shape
    out = torch.empty_like(q)
    grid = (triton.cdiv(N_CTX, 64), Z * H, 1)

    _prosody_attention_fwd_kernel[grid](
        q, k, v, out,
        q.stride(0), q.stride(1), q.stride(2), q.stride(3),
        k.stride(0), k.stride(1), k.stride(2), k.stride(3),
        v.stride(0), v.stride(1), v.stride(2), v.stride(3),
        out.stride(0), out.stride(1), out.stride(2), out.stride(3),
        Z, H, N_CTX,
        BLOCK_M=64, BLOCK_DMODEL=D_MODEL, BLOCK_N=64
    )
    return out
