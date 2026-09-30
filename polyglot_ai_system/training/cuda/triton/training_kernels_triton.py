"""
training_kernels_triton.py
Triton training kernels for the polyglot AI system.

Implements:
  - Fused dropout kernel (Bernoulli + rescaling + optional activation)
  - Scaled AdamW optimizer step
  - Fused LayerNorm backward pass
  - Sparse top-k selection for MoE routing
  - Fused cross-entropy with label smoothing
  - Gradient accumulation with FP16 master copy
"""

from __future__ import annotations

import math
from typing import Optional

import torch
import triton
import triton.language as tl

# ─────────────────────────────────────────────────────────────────────────────
# 1. Fused Dropout Kernel
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _dropout_forward_kernel(
    x_ptr,
    out_ptr,
    mask_ptr,
    N: tl.constexpr,
    BLOCK: tl.constexpr,
    p: tl.constexpr,
    scale: tl.constexpr,
    seed: int,
    TRAINING: tl.constexpr,
):
    """
    Bernoulli dropout forward.
    Each element is independently dropped with probability p.
    Surviving elements are scaled by 1/(1-p) (inverted dropout).
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < N

    x = tl.load(x_ptr + offsets, mask=mask, other=0.0)

    if TRAINING:
        # Generate uniform random values using Triton's philox RNG
        rand_block = tl.rand(seed, offsets)
        keep = rand_block >= p
        x = tl.where(keep, x * scale, tl.zeros_like(x))
        if mask_ptr is not None:
            tl.store(mask_ptr + offsets, keep.to(tl.int8), mask=mask)

    tl.store(out_ptr + offsets, x, mask=mask)


@triton.jit
def _dropout_backward_kernel(
    grad_ptr,
    mask_ptr,
    out_ptr,
    N: tl.constexpr,
    BLOCK: tl.constexpr,
    scale: tl.constexpr,
):
    """Dropout backward: re-apply mask and scale to upstream gradient."""
    pid = tl.program_id(0)
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < N

    grad = tl.load(grad_ptr + offsets, mask=mask, other=0.0)
    keep = tl.load(mask_ptr + offsets, mask=mask, other=0).to(tl.int1)
    grad = tl.where(keep, grad * scale, tl.zeros_like(grad))
    tl.store(out_ptr + offsets, grad, mask=mask)


def triton_dropout_forward(
    x: torch.Tensor,
    p: float = 0.1,
    training: bool = True,
    seed: Optional[int] = None,
) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
    """
    Triton dropout forward pass.
    Returns (output, mask). mask is None when not training.
    """
    assert x.is_cuda and x.is_contiguous()
    N = x.numel()
    BLOCK = triton.next_power_of_2(min(N, 1024))
    grid = (triton.cdiv(N, BLOCK),)

    out = torch.empty_like(x)
    mask_tensor = torch.empty(N, dtype=torch.int8, device=x.device) if training else None

    rng_seed = seed if seed is not None else torch.randint(0, 2**31, (1,)).item()
    scale = 1.0 / (1.0 - p)

    _dropout_forward_kernel[grid](
        x, out,
        mask_tensor if mask_tensor is not None else x,  # dummy ptr when not training
        N, BLOCK, p, scale, rng_seed, int(training),
    )
    return out, mask_tensor


def triton_dropout_backward(
    grad: torch.Tensor,
    mask: torch.Tensor,
    p: float,
) -> torch.Tensor:
    """Triton dropout backward pass."""
    assert grad.is_cuda and grad.is_contiguous()
    N = grad.numel()
    BLOCK = triton.next_power_of_2(min(N, 1024))
    grid = (triton.cdiv(N, BLOCK),)

    out = torch.empty_like(grad)
    scale = 1.0 / (1.0 - p)

    _dropout_backward_kernel[grid](grad, mask, out, N, BLOCK, scale)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 2. Scaled AdamW Optimizer Step
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _adamw_step_kernel(
    param_ptr,
    grad_ptr,
    m_ptr,          # first moment
    v_ptr,          # second moment
    N: tl.constexpr,
    BLOCK: tl.constexpr,
    lr: tl.constexpr,
    beta1: tl.constexpr,
    beta2: tl.constexpr,
    eps: tl.constexpr,
    wd: tl.constexpr,
    step: int,      # current step for bias correction
):
    """
    Fused AdamW parameter update step.
    Updates param, m, v in-place in a single kernel pass.
    Bias correction applied using the step count.
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < N

    # Load current state
    p = tl.load(param_ptr + offsets, mask=mask, other=0.0).to(tl.float32)
    g = tl.load(grad_ptr  + offsets, mask=mask, other=0.0).to(tl.float32)
    m = tl.load(m_ptr     + offsets, mask=mask, other=0.0).to(tl.float32)
    v = tl.load(v_ptr     + offsets, mask=mask, other=0.0).to(tl.float32)

    # Moment updates
    m_new = beta1 * m + (1.0 - beta1) * g
    v_new = beta2 * v + (1.0 - beta2) * g * g

    # Bias correction
    bc1 = 1.0 - beta1 ** step
    bc2 = 1.0 - beta2 ** step
    m_hat = m_new / bc1
    v_hat = v_new / bc2

    # Parameter update with decoupled weight decay
    p_new = p - lr * (m_hat / (tl.sqrt(v_hat) + eps) + wd * p)

    # Store updated state
    tl.store(param_ptr + offsets, p_new.to(tl.float32), mask=mask)
    tl.store(m_ptr     + offsets, m_new.to(tl.float32), mask=mask)
    tl.store(v_ptr     + offsets, v_new.to(tl.float32), mask=mask)


def triton_adamw_step(
    param: torch.Tensor,
    grad: torch.Tensor,
    m: torch.Tensor,
    v: torch.Tensor,
    step: int,
    lr: float = 1e-4,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    weight_decay: float = 0.01,
) -> None:
    """
    In-place Triton AdamW optimizer step.
    Modifies param, m, v tensors directly.
    """
    assert param.is_cuda and param.is_contiguous()
    assert grad.shape == param.shape

    N = param.numel()
    BLOCK = triton.next_power_of_2(min(N, 1024))
    grid = (triton.cdiv(N, BLOCK),)

    _adamw_step_kernel[grid](
        param, grad, m, v,
        N, BLOCK,
        lr, beta1, beta2, eps, weight_decay, step,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Fused LayerNorm Backward
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _layernorm_backward_kernel(
    dy_ptr,         # upstream gradient [B, T, H]
    x_ptr,          # forward input [B, T, H]
    w_ptr,          # weight (gamma) [H]
    mean_ptr,       # saved mean [B, T]
    rstd_ptr,       # saved 1/std [B, T]
    dx_ptr,         # output gradient wrt x
    dw_ptr,         # output gradient wrt weight (atomic)
    db_ptr,         # output gradient wrt bias (atomic)
    BT: int,        # B * T (number of rows)
    H: tl.constexpr,
    BLOCK: tl.constexpr,
):
    """
    Fused LayerNorm backward pass (Welford algorithm for numerical stability).
    Computes dx, dw, db in a single kernel.
    """
    row_id = tl.program_id(0)
    if row_id >= BT:
        return

    offsets = tl.arange(0, BLOCK)
    mask = offsets < H

    # Load saved statistics
    mean = tl.load(mean_ptr + row_id)
    rstd = tl.load(rstd_ptr + row_id)

    # Load x, dy, w for this row
    x  = tl.load(x_ptr  + row_id * H + offsets, mask=mask, other=0.0).to(tl.float32)
    dy = tl.load(dy_ptr + row_id * H + offsets, mask=mask, other=0.0).to(tl.float32)
    w  = tl.load(w_ptr  +             offsets, mask=mask, other=0.0).to(tl.float32)

    # Normalized value
    x_hat = (x - mean) * rstd

    # Gradient wrt normalized x
    dy_w = dy * w

    # Sum reductions (over hidden dim)
    sum_dy_w       = tl.sum(tl.where(mask, dy_w,       tl.zeros_like(dy_w)))
    sum_dy_w_xhat  = tl.sum(tl.where(mask, dy_w * x_hat, tl.zeros_like(dy_w)))

    # Gradient wrt x
    dx = rstd * (dy_w - (sum_dy_w + x_hat * sum_dy_w_xhat) / H)

    # Store dx
    tl.store(dx_ptr + row_id * H + offsets, dx.to(tl.float32), mask=mask)

    # Accumulate dw, db (atomically, since multiple rows contribute)
    tl.atomic_add(dw_ptr + offsets, (dy * x_hat).to(tl.float32), mask=mask)
    tl.atomic_add(db_ptr + offsets, dy.to(tl.float32),           mask=mask)


def triton_layernorm_backward(
    dy: torch.Tensor,
    x: torch.Tensor,
    weight: torch.Tensor,
    mean: torch.Tensor,
    rstd: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Triton fused LayerNorm backward.
    Returns (dx, dweight, dbias).
    """
    B, T, H = x.shape
    BT = B * T

    dy_c  = dy.contiguous().view(BT, H)
    x_c   = x.contiguous().view(BT, H)
    mean_c = mean.contiguous().view(BT)
    rstd_c = rstd.contiguous().view(BT)

    BLOCK = triton.next_power_of_2(H)
    grid = (BT,)

    dx  = torch.zeros_like(x_c)
    dw  = torch.zeros(H, device=x.device, dtype=torch.float32)
    db  = torch.zeros(H, device=x.device, dtype=torch.float32)

    _layernorm_backward_kernel[grid](
        dy_c, x_c, weight, mean_c, rstd_c, dx, dw, db, BT, H, BLOCK,
    )
    return dx.view_as(x), dw.to(weight.dtype), db.to(weight.dtype)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Fused Cross-Entropy with Label Smoothing
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _cross_entropy_fwd_kernel(
    logits_ptr,     # [N, V]
    labels_ptr,     # [N] int64 class indices
    loss_ptr,       # [N] output per-sample loss
    N: int,
    V: tl.constexpr,
    BLOCK: tl.constexpr,
    smoothing: tl.constexpr,
    ignore_index: tl.constexpr,
):
    """
    Fused softmax + cross-entropy with label smoothing.
    loss_i = (1 - ε)·CE(logits_i, y_i) + ε·mean_j[-log softmax_j(logits_i)]
    """
    row_id = tl.program_id(0)
    if row_id >= N:
        return

    offsets = tl.arange(0, BLOCK)
    mask = offsets < V

    logits = tl.load(logits_ptr + row_id * V + offsets, mask=mask, other=-1e9).to(tl.float32)
    label  = tl.load(labels_ptr + row_id).to(tl.int32)

    # Ignore padding labels
    if label == ignore_index:
        tl.store(loss_ptr + row_id, tl.zeros(1, dtype=tl.float32))
        return

    # Numerically stable softmax
    max_logit = tl.max(tl.where(mask, logits, tl.full([BLOCK], -1e9, dtype=tl.float32)))
    shifted   = logits - max_logit
    exp_vals  = tl.exp(shifted)
    sum_exp   = tl.sum(tl.where(mask, exp_vals, tl.zeros_like(exp_vals)))
    log_sum   = tl.log(sum_exp) + max_logit

    # Log-softmax of target class
    log_prob_target = tl.load(logits_ptr + row_id * V + label) - log_sum

    # Mean log-softmax over all classes (for uniform smoothing distribution)
    log_probs = logits - log_sum
    mean_lp   = tl.sum(tl.where(mask, log_probs, tl.zeros_like(log_probs))) / V

    # Label-smoothed cross-entropy
    loss = -(1.0 - smoothing) * log_prob_target - smoothing * mean_lp
    tl.store(loss_ptr + row_id, loss)


def triton_cross_entropy(
    logits: torch.Tensor,
    labels: torch.Tensor,
    label_smoothing: float = 0.0,
    ignore_index: int = -100,
    reduction: str = "mean",
) -> torch.Tensor:
    """
    Triton fused cross-entropy with label smoothing.
    logits: [N, V] FP32
    labels: [N]    int64
    Returns scalar loss (if reduction='mean'/'sum') or per-sample [N] tensor.
    """
    assert logits.is_cuda and logits.is_contiguous()
    N, V = logits.shape

    BLOCK = triton.next_power_of_2(V)
    grid = (N,)

    losses = torch.empty(N, dtype=torch.float32, device=logits.device)

    _cross_entropy_fwd_kernel[grid](
        logits, labels, losses, N, V, BLOCK,
        label_smoothing, ignore_index,
    )

    if reduction == "none":
        return losses
    valid_mask = labels != ignore_index
    losses = losses[valid_mask]
    if reduction == "sum":
        return losses.sum()
    return losses.mean()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Gradient Accumulation with FP16 Master Copy
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _grad_accumulate_kernel(
    master_ptr,    # float32 master gradient accumulator [N]
    grad16_ptr,    # float16 incoming gradient [N]
    N: tl.constexpr,
    BLOCK: tl.constexpr,
    scale: tl.constexpr,   # 1.0 / num_accumulation_steps
):
    """
    Accumulate FP16 gradient into FP32 master buffer, scaled by 1/num_steps.
    master[i] += scale * float32(grad16[i])
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < N

    g16  = tl.load(grad16_ptr  + offsets, mask=mask, other=0.0).to(tl.float32)
    acc  = tl.load(master_ptr  + offsets, mask=mask, other=0.0).to(tl.float32)
    acc += scale * g16
    tl.store(master_ptr + offsets, acc, mask=mask)


def triton_grad_accumulate(
    master_grad: torch.Tensor,
    grad16: torch.Tensor,
    num_accumulation_steps: int,
) -> None:
    """
    Accumulate a FP16 gradient into a FP32 master buffer.
    Scales by 1/num_accumulation_steps.
    In-place on master_grad.
    """
    assert master_grad.is_cuda
    N = master_grad.numel()
    BLOCK = triton.next_power_of_2(min(N, 1024))
    grid = (triton.cdiv(N, BLOCK),)

    scale = 1.0 / num_accumulation_steps
    _grad_accumulate_kernel[grid](
        master_grad, grad16.to(torch.float16),
        N, BLOCK, scale,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Top-K Sparse Selection for MoE Routing
# ─────────────────────────────────────────────────────────────────────────────


@triton.jit
def _topk_softmax_kernel(
    gates_ptr,      # [N, E] float32 router logits
    out_ptr,        # [N, K] float32 top-k softmax weights
    idx_ptr,        # [N, K] int32 selected expert indices
    N: int,
    E: tl.constexpr,
    K: tl.constexpr,
    BLOCK: tl.constexpr,
):
    """
    Compute top-K softmax router weights from gate logits.
    Uses insertion sort for small K (typical K=2 or K=4 in MoE).
    """
    row_id = tl.program_id(0)
    if row_id >= N:
        return

    offsets = tl.arange(0, BLOCK)
    mask = offsets < E

    # Load gate logits
    logits = tl.load(gates_ptr + row_id * E + offsets, mask=mask, other=-1e9).to(tl.float32)

    # Softmax over all experts
    max_l = tl.max(tl.where(mask, logits, tl.full([BLOCK], -1e9, dtype=tl.float32)))
    exp_l = tl.exp(logits - max_l)
    sum_e = tl.sum(tl.where(mask, exp_l, tl.zeros_like(exp_l)))
    softmax_all = tl.where(mask, exp_l / sum_e, tl.zeros_like(exp_l))

    # Select top-K by argmax K times (sequential, suitable for small K)
    for k in range(K):
        # Find argmax
        best_idx = tl.argmax(tl.where(mask, softmax_all, tl.zeros_like(softmax_all)), axis=0)
        best_val = tl.load(gates_ptr + row_id * E + best_idx)

        tl.store(idx_ptr + row_id * K + k, best_idx)
        tl.store(out_ptr + row_id * K + k, tl.load(gates_ptr + row_id * E + best_idx))

        # Mask out selected expert
        softmax_all = tl.where(offsets == best_idx, tl.zeros_like(softmax_all), softmax_all)


def triton_topk_routing(
    gates: torch.Tensor,
    k: int = 2,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Top-K expert routing from gate logits.
    gates: [N, num_experts] FP32
    Returns (weights [N, k], indices [N, k]).
    """
    assert gates.is_cuda and gates.is_contiguous()
    N, E = gates.shape
    BLOCK = triton.next_power_of_2(E)
    grid = (N,)

    weights = torch.empty(N, k, dtype=torch.float32, device=gates.device)
    indices = torch.empty(N, k, dtype=torch.int32,   device=gates.device)

    _topk_softmax_kernel[grid](gates, weights, indices, N, E, k, BLOCK)
    # Normalize selected weights
    weights = torch.softmax(weights, dim=-1)
    return weights, indices


# ─────────────────────────────────────────────────────────────────────────────
# Module exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    "triton_dropout_forward",
    "triton_dropout_backward",
    "triton_adamw_step",
    "triton_layernorm_backward",
    "triton_cross_entropy",
    "triton_grad_accumulate",
    "triton_topk_routing",
]
