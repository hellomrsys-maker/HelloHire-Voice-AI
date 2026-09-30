"""
ccte_triton_fields.py - Triton GPU Kernels for Wilson-Cowan Neural Field Dynamics & Cognitive Tensor Ops.

Implements high-throughput parallel integration of coupled excitatory-inhibitory (E-I) neural field equations:
tau_e * dE/dt = -E + (1 - r_e * E) * S_e(c_ee * E - c_ei * I + P)
tau_i * dI/dt = -I + (1 - r_i * I) * S_i(c_ie * E - c_ii * I + Q)
"""

import triton
import triton.language as tl
import torch

@triton.jit
def wilson_cowan_field_kernel(
    E_ptr,          # [Batch, NumNodes] excitatory population state
    I_ptr,          # [Batch, NumNodes] inhibitory population state
    P_ptr,          # [Batch, NumNodes] external sensory/cognitive drive
    Out_E_ptr,      # [Batch, NumNodes] updated E state
    Out_I_ptr,      # [Batch, NumNodes] updated I state
    dt: tl.constexpr,
    tau_e: tl.constexpr,
    tau_i: tl.constexpr,
    c_ee: tl.constexpr,
    c_ei: tl.constexpr,
    c_ie: tl.constexpr,
    c_ii: tl.constexpr,
    BLOCK_SIZE: tl.constexpr
):
    pid = tl.program_id(axis=0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)

    e = tl.load(E_ptr + offsets)
    i = tl.load(I_ptr + offsets)
    p = tl.load(P_ptr + offsets)

    # Sigmoid response functions: S(x) = 1 / (1 + exp(-x))
    input_e = c_ee * e - c_ei * i + p
    input_i = c_ie * e - c_ii * i

    s_e = 1.0 / (1.0 + tl.exp(-input_e))
    s_i = 1.0 / (1.0 + tl.exp(-input_i))

    # Euler update step
    de = (-e + (1.0 - 0.5 * e) * s_e) * (dt / tau_e)
    di = (-i + (1.0 - 0.5 * i) * s_i) * (dt / tau_i)

    new_e = tl.clamp(e + de, 0.0, 1.0)
    new_i = tl.clamp(i + di, 0.0, 1.0)

    tl.store(Out_E_ptr + offsets, new_e)
    tl.store(Out_I_ptr + offsets, new_i)


def launch_wilson_cowan_triton(
    E: torch.Tensor,
    I: torch.Tensor,
    P: torch.Tensor,
    dt: float = 0.01,
    tau_e: float = 0.01,
    tau_i: float = 0.02
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Host wrapper for launching the Triton Wilson-Cowan simulation kernel.
    """
    assert E.is_cuda and I.is_cuda and P.is_cuda
    num_elements = E.numel()
    out_E = torch.empty_like(E)
    out_I = torch.empty_like(I)

    BLOCK_SIZE = 128
    grid = (triton.cdiv(num_elements, BLOCK_SIZE),)

    wilson_cowan_field_kernel[grid](
        E, I, P, out_E, out_I,
        dt=dt,
        tau_e=tau_e,
        tau_i=tau_i,
        c_ee=12.0,
        c_ei=4.0,
        c_ie=13.0,
        c_ii=11.0,
        BLOCK_SIZE=BLOCK_SIZE
    )
    return out_E, out_I
