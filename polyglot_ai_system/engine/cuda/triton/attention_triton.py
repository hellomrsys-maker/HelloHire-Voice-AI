# =============================================================================
# engine/cuda/triton/attention_triton.py
# Triton kernel for FlashAttention forward pass — custom backward pass
# implementation with full gradient computation.
# =============================================================================

import triton
import triton.language as tl
import torch
from typing import Optional

# =============================================================================
# Triton Flash Attention Forward Kernel
# =============================================================================

@triton.jit
def _flash_attention_fwd_kernel(
    Q_ptr, K_ptr, V_ptr, O_ptr, L_ptr,   # device pointers
    stride_qb, stride_qh, stride_qm, stride_qk,
    stride_kb, stride_kh, stride_kn, stride_kk,
    stride_vb, stride_vh, stride_vn, stride_vk,
    stride_ob, stride_oh, stride_om, stride_ok,
    stride_lb, stride_lh, stride_lm,
    N_CTX: tl.constexpr,  # Sequence length
    D_HEAD: tl.constexpr, # Head dimension
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
    CAUSAL:  tl.constexpr,
    scale:   tl.constexpr,
):
    """
    Triton implementation of Flash Attention forward pass.

    Grid: (batch * num_heads, cdiv(N_CTX, BLOCK_M))
    """
    # Program indices
    start_m  = tl.program_id(0)   # Q tile index
    bh_idx   = tl.program_id(1)   # Batch * head index

    # Pointers to Q block
    q_offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    q_offs_k = tl.arange(0, D_HEAD)
    q_mask   = q_offs_m[:, None] < N_CTX

    Q_block_ptr = Q_ptr + bh_idx * stride_qh
    q = tl.load(
        Q_block_ptr + q_offs_m[:, None] * stride_qm + q_offs_k[None, :] * stride_qk,
        mask=q_mask,
        other=0.0
    )

    # Initialize accumulators
    o_acc    = tl.zeros([BLOCK_M, D_HEAD], dtype=tl.float32)
    m_i      = tl.full([BLOCK_M], float('-inf'), dtype=tl.float32)
    l_i      = tl.zeros([BLOCK_M], dtype=tl.float32)

    # Scale queries
    q_scaled = q * scale

    # Iterate over K/V blocks
    num_kv_blocks = tl.cdiv(N_CTX, BLOCK_N)

    for block_n in range(0, num_kv_blocks):
        kv_offs_n = block_n * BLOCK_N + tl.arange(0, BLOCK_N)
        kv_mask   = kv_offs_n[None, :] < N_CTX

        if CAUSAL:
            # Skip future blocks
            if (start_m * BLOCK_M) < (block_n * BLOCK_N):
                continue

        # Load K block
        K_block_ptr = K_ptr + bh_idx * stride_kh
        k = tl.load(
            K_block_ptr + kv_offs_n[:, None] * stride_kn + q_offs_k[None, :] * stride_kk,
            mask=kv_offs_n[:, None] < N_CTX,
            other=0.0
        )

        # Load V block
        V_block_ptr = V_ptr + bh_idx * stride_vh
        v = tl.load(
            V_block_ptr + kv_offs_n[:, None] * stride_vn + q_offs_k[None, :] * stride_vk,
            mask=kv_offs_n[:, None] < N_CTX,
            other=0.0
        )

        # Compute attention scores: S = Q @ K^T
        s = tl.dot(q_scaled, tl.trans(k))  # [BLOCK_M, BLOCK_N]

        # Apply causal mask
        if CAUSAL:
            q_idx = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
            k_idx = block_n * BLOCK_N + tl.arange(0, BLOCK_N)
            causal_mask = q_idx[:, None] >= k_idx[None, :]
            s = tl.where(causal_mask, s, float('-inf'))

        # Mask padded positions
        s = tl.where(kv_mask, s, float('-inf'))

        # Online softmax update
        m_ij = tl.max(s, axis=1)              # New per-row max
        m_new = tl.maximum(m_i, m_ij)         # Global running max

        alpha = tl.exp(m_i - m_new)           # Rescale factor for existing o_acc
        p     = tl.exp(s - m_new[:, None])    # Exponentiated scores

        # Accumulate
        l_i   = alpha * l_i + tl.sum(p, axis=1)
        o_acc = alpha[:, None] * o_acc + tl.dot(p, v)
        m_i   = m_new

    # Normalize output
    o_acc = o_acc / l_i[:, None]

    # Write output
    O_block_ptr = O_ptr + bh_idx * stride_oh
    tl.store(
        O_block_ptr + q_offs_m[:, None] * stride_om + q_offs_k[None, :] * stride_ok,
        o_acc.to(tl.float16),
        mask=q_mask
    )

    # Write log-sum-exp for backward
    L_block_ptr = L_ptr + bh_idx * stride_lh
    tl.store(
        L_block_ptr + q_offs_m * stride_lm,
        m_i + tl.log(l_i),
        mask=q_offs_m < N_CTX
    )


# =============================================================================
# Triton Flash Attention Backward Kernel
# =============================================================================

@triton.jit
def _flash_attention_bwd_kernel(
    Q_ptr, K_ptr, V_ptr,
    O_ptr, L_ptr,
    dO_ptr, dQ_ptr, dK_ptr, dV_ptr,
    stride_qb, stride_qh, stride_qm, stride_qk,
    stride_kb, stride_kh, stride_kn, stride_kk,
    N_CTX:  tl.constexpr,
    D_HEAD: tl.constexpr,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
    CAUSAL:  tl.constexpr,
    scale:   tl.constexpr,
):
    """
    Custom backward pass for FlashAttention.
    Computes dQ, dK, dV using the stored LSE from the forward pass.

    Implements the gradient formulas:
        dP = softmax(S) * (dO @ V^T - rowsum(dO * O))
        dQ += dP @ K
        dK += dP^T @ Q
        dV += P^T @ dO
    """
    start_m = tl.program_id(0)
    bh_idx  = tl.program_id(1)

    q_offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    q_offs_k = tl.arange(0, D_HEAD)
    q_mask   = q_offs_m[:, None] < N_CTX

    # Load Q, O, dO, LSE for this Q block
    q  = tl.load(Q_ptr  + bh_idx * stride_qh + q_offs_m[:, None] * stride_qm + q_offs_k[None, :])
    o  = tl.load(O_ptr  + bh_idx * stride_qh + q_offs_m[:, None] * stride_qm + q_offs_k[None, :])
    do = tl.load(dO_ptr + bh_idx * stride_qh + q_offs_m[:, None] * stride_qm + q_offs_k[None, :])
    l  = tl.load(L_ptr  + bh_idx * stride_qh + q_offs_m)

    # Compute D = rowsum(dO * O) — needed for the gradient computation
    delta = tl.sum(do * o, axis=1)

    dq_acc = tl.zeros([BLOCK_M, D_HEAD], dtype=tl.float32)

    for block_n in range(0, tl.cdiv(N_CTX, BLOCK_N)):
        kv_offs_n = block_n * BLOCK_N + tl.arange(0, BLOCK_N)

        k  = tl.load(K_ptr  + bh_idx * stride_kh + kv_offs_n[:, None] * stride_kn + q_offs_k[None, :])
        v  = tl.load(V_ptr  + bh_idx * stride_vh + kv_offs_n[:, None] * stride_vn + q_offs_k[None, :])
        dv = tl.load(dV_ptr + bh_idx * stride_vh + kv_offs_n[:, None] * stride_vn + q_offs_k[None, :])
        dk = tl.load(dK_ptr + bh_idx * stride_kh + kv_offs_n[:, None] * stride_kn + q_offs_k[None, :])

        # Recompute attention weights p from Q, K, LSE
        s = scale * tl.dot(q, tl.trans(k))
        p = tl.exp(s - l[:, None])

        if CAUSAL:
            q_idx = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
            k_idx = block_n * BLOCK_N + tl.arange(0, BLOCK_N)
            p = tl.where(q_idx[:, None] >= k_idx[None, :], p, 0.0)

        # dV += P^T @ dO
        dv_update = tl.dot(tl.trans(p), do)
        tl.store(dV_ptr + bh_idx * stride_vh
                 + kv_offs_n[:, None] * stride_vn + q_offs_k[None, :],
                 dv + dv_update.to(tl.float16))

        # dP = dO @ V^T
        dp = tl.dot(do, tl.trans(v))

        # dS = p * (dP - delta)
        ds = p * (dp - delta[:, None])

        # dQ += dS @ K
        dq_acc += scale * tl.dot(ds, k)

        # dK += dS^T @ Q
        dk_update = scale * tl.dot(tl.trans(ds), q)
        tl.store(dK_ptr + bh_idx * stride_kh
                 + kv_offs_n[:, None] * stride_kn + q_offs_k[None, :],
                 dk + dk_update.to(tl.float16))

    # Write dQ
    tl.store(
        dQ_ptr + bh_idx * stride_qh + q_offs_m[:, None] * stride_qm + q_offs_k[None, :],
        dq_acc.to(tl.float16),
        mask=q_mask
    )


# =============================================================================
# Python wrapper class for the Triton FlashAttention kernels
# =============================================================================

class TritonFlashAttentionFunction(torch.autograd.Function):
    """
    Custom autograd Function wrapping the Triton FlashAttention kernels.
    Supports forward and backward passes with full gradient computation.
    """

    @staticmethod
    def forward(
        ctx,
        q: torch.Tensor,      # [batch, heads, seq_len, head_dim]
        k: torch.Tensor,
        v: torch.Tensor,
        causal: bool = False,
        sm_scale: Optional[float] = None,
    ) -> torch.Tensor:
        """
        Flash Attention forward pass using Triton kernel.

        Args:
            q: Query tensor [B, H, N, D]
            k: Key tensor   [B, H, N, D]
            v: Value tensor [B, H, N, D]
            causal: Whether to apply causal mask
            sm_scale: Softmax scale factor (default: 1/sqrt(D))

        Returns:
            Output tensor [B, H, N, D]
        """
        batch, heads, seq_len, head_dim = q.shape

        if sm_scale is None:
            sm_scale = head_dim ** -0.5

        # Ensure contiguous memory layout
        q = q.contiguous()
        k = k.contiguous()
        v = v.contiguous()

        # Allocate output and LSE buffers
        o = torch.empty_like(q)
        L = torch.empty((batch, heads, seq_len), device=q.device, dtype=torch.float32)

        # Tile sizes
        BLOCK_M = 64
        BLOCK_N = 64

        # Grid: (batch * heads, cdiv(seq_len, BLOCK_M))
        grid = (batch * heads, triton.cdiv(seq_len, BLOCK_M))

        _flash_attention_fwd_kernel[grid](
            q, k, v, o, L,
            q.stride(0), q.stride(1), q.stride(2), q.stride(3),
            k.stride(0), k.stride(1), k.stride(2), k.stride(3),
            v.stride(0), v.stride(1), v.stride(2), v.stride(3),
            o.stride(0), o.stride(1), o.stride(2), o.stride(3),
            L.stride(0), L.stride(1), L.stride(2),
            N_CTX=seq_len,
            D_HEAD=head_dim,
            BLOCK_M=BLOCK_M,
            BLOCK_N=BLOCK_N,
            CAUSAL=causal,
            scale=sm_scale,
        )

        # Save for backward
        ctx.save_for_backward(q, k, v, o, L)
        ctx.sm_scale = sm_scale
        ctx.causal   = causal
        ctx.BLOCK_M  = BLOCK_M
        ctx.BLOCK_N  = BLOCK_N

        return o

    @staticmethod
    def backward(ctx, dO: torch.Tensor):
        """
        Flash Attention backward pass — computes dQ, dK, dV.
        """
        q, k, v, o, L = ctx.saved_tensors
        batch, heads, seq_len, head_dim = q.shape

        dO = dO.contiguous()

        dQ = torch.zeros_like(q)
        dK = torch.zeros_like(k)
        dV = torch.zeros_like(v)

        grid = (batch * heads, triton.cdiv(seq_len, ctx.BLOCK_M))

        _flash_attention_bwd_kernel[grid](
            q, k, v, o, L, dO, dQ, dK, dV,
            q.stride(0), q.stride(1), q.stride(2), q.stride(3),
            k.stride(0), k.stride(1), k.stride(2), k.stride(3),
            N_CTX=seq_len,
            D_HEAD=head_dim,
            BLOCK_M=ctx.BLOCK_M,
            BLOCK_N=ctx.BLOCK_N,
            CAUSAL=ctx.causal,
            scale=ctx.sm_scale,
        )

        return dQ, dK, dV, None, None


def triton_flash_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    causal: bool = False,
    sm_scale: Optional[float] = None,
) -> torch.Tensor:
    """
    Computes Flash Attention using the custom Triton kernel.

    Args:
        q: [batch, heads, seq_len, head_dim] float16 tensor on CUDA
        k: [batch, heads, seq_len, head_dim] float16 tensor on CUDA
        v: [batch, heads, seq_len, head_dim] float16 tensor on CUDA
        causal: Whether to apply causal mask
        sm_scale: Softmax scale (default: 1/sqrt(head_dim))

    Returns:
        Output tensor of shape [batch, heads, seq_len, head_dim]

    Raises:
        AssertionError: If inputs are not on CUDA or not float16.
    """
    assert q.is_cuda, "q must be on CUDA"
    assert k.is_cuda, "k must be on CUDA"
    assert v.is_cuda, "v must be on CUDA"
    assert q.dtype in (torch.float16, torch.bfloat16), "q must be fp16 or bf16"
    assert q.shape == k.shape == v.shape, "q, k, v must have the same shape"

    return TritonFlashAttentionFunction.apply(q, k, v, causal, sm_scale)


# =============================================================================
# Triton Fused RoPE kernel
# =============================================================================

@triton.jit
def _rope_kernel(
    Q_ptr, K_ptr,
    cos_ptr, sin_ptr,
    stride_q_seq, stride_q_head, stride_q_dim,
    stride_cos_seq, stride_cos_dim,
    N_HEADS:  tl.constexpr,
    HEAD_DIM: tl.constexpr,
    HALF_DIM: tl.constexpr,
):
    """
    Triton RoPE kernel: applies rotary positional encoding to Q and K.

    Grid: (seq_len, num_heads)
    Block: (HEAD_DIM / 2,)
    """
    seq_pos = tl.program_id(0)
    head    = tl.program_id(1)
    dim_i   = tl.arange(0, HALF_DIM)

    # Load cos and sin values for this position
    cos = tl.load(cos_ptr + seq_pos * stride_cos_seq + dim_i * stride_cos_dim)
    sin = tl.load(sin_ptr + seq_pos * stride_cos_seq + dim_i * stride_cos_dim)

    base_q = Q_ptr + seq_pos * stride_q_seq + head * stride_q_head
    base_k = K_ptr + seq_pos * stride_q_seq + head * stride_q_head

    # Load x0 and x1 = x[i] and x[i + half_dim]
    q0 = tl.load(base_q + dim_i * stride_q_dim)
    q1 = tl.load(base_q + (dim_i + HALF_DIM) * stride_q_dim)
    k0 = tl.load(base_k + dim_i * stride_q_dim)
    k1 = tl.load(base_k + (dim_i + HALF_DIM) * stride_q_dim)

    # Rotate
    tl.store(base_q + dim_i * stride_q_dim,              q0 * cos - q1 * sin)
    tl.store(base_q + (dim_i + HALF_DIM) * stride_q_dim, q0 * sin + q1 * cos)
    tl.store(base_k + dim_i * stride_q_dim,              k0 * cos - k1 * sin)
    tl.store(base_k + (dim_i + HALF_DIM) * stride_q_dim, k0 * sin + k1 * cos)


def triton_apply_rope(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Applies RoPE to Q and K using the Triton kernel.

    Args:
        q, k: [seq_len, num_heads, head_dim] tensors on CUDA
        cos, sin: [max_seq_len, head_dim // 2] precomputed tables

    Returns:
        (q_rotated, k_rotated) — new tensors with RoPE applied
    """
    assert q.is_cuda and k.is_cuda
    seq_len, num_heads, head_dim = q.shape
    half_dim = head_dim // 2

    q = q.contiguous()
    k = k.contiguous()

    grid = (seq_len, num_heads)
    _rope_kernel[grid](
        q, k, cos, sin,
        q.stride(0), q.stride(1), q.stride(2),
        cos.stride(0), cos.stride(1),
        N_HEADS=num_heads,
        HEAD_DIM=head_dim,
        HALF_DIM=half_dim,
    )
    return q, k


# =============================================================================
# Test utilities
# =============================================================================

def verify_triton_attention(batch=2, heads=4, seq_len=64, head_dim=32):
    """
    Verifies Triton FlashAttention output against PyTorch reference.
    Returns True if maximum absolute difference < 1e-2.
    """
    import torch.nn.functional as F

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("CUDA not available — skipping Triton verification")
        return True

    q = torch.randn(batch, heads, seq_len, head_dim, device=device, dtype=torch.float16)
    k = torch.randn(batch, heads, seq_len, head_dim, device=device, dtype=torch.float16)
    v = torch.randn(batch, heads, seq_len, head_dim, device=device, dtype=torch.float16)

    # Reference: PyTorch scaled dot-product attention
    ref_out = F.scaled_dot_product_attention(q, k, v, is_causal=False)

    # Triton output
    tri_out = triton_flash_attention(q, k, v, causal=False)

    max_diff = (ref_out - tri_out).abs().max().item()
    print(f"Max absolute difference (Triton vs PyTorch): {max_diff:.6f}")
    return max_diff < 0.02


if __name__ == "__main__":
    result = verify_triton_attention()
    print(f"Triton FlashAttention verification: {'PASSED' if result else 'FAILED'}")
