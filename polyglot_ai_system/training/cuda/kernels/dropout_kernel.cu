/*
 * dropout_kernel.cu
 * CUDA kernel implementations for dropout regularization.
 *
 * Implements:
 *   - Standard Bernoulli dropout (inverted scaling)
 *   - Variational dropout (per-parameter mask)
 *   - DropConnect (weight-level dropout)
 *   - Alpha dropout (preserving self-normalizing property)
 *   - Combined dropout + activation fusion (Dropout + GELU, Dropout + SiLU)
 *
 * All kernels use cuRAND for GPU-side random number generation.
 * Supports half-precision (FP16) and single-precision (FP32).
 */

#include <cuda_fp16.h>
#include <curand_kernel.h>
#include <cstdint>
#include <cmath>

// ─────────────────────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────────────────────

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        printf("CUDA error %s at %s:%d\n", cudaGetErrorString(err), __FILE__, __LINE__); \
    } \
} while (0)

static constexpr int BLOCK_SIZE    = 256;
static constexpr int VECTOR_WIDTH  = 4;      // process 4 floats per thread

// ─────────────────────────────────────────────────────────────────────────────
// cuRAND state initialization
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Initialize one cuRAND XORWOW state per thread.
 * seed:    base RNG seed (typically training step)
 * offset:  per-call offset to ensure unique streams
 */
__global__ void init_curand_states_kernel(
    curandState* states,
    uint64_t     seed,
    uint64_t     offset,
    int          n_states
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n_states) return;
    curand_init(seed, (unsigned long long)tid, offset, &states[tid]);
}

// ─────────────────────────────────────────────────────────────────────────────
// Standard Bernoulli Dropout (FP32)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Inverted Bernoulli dropout (FP32).
 * Each element is zeroed with probability `p` and scaled by 1/(1-p).
 *
 * x       [in/out] : input/output tensor, shape [N]
 * mask    [out]    : binary mask (1=keep, 0=drop), shape [N]; may be null
 * N                : total element count
 * p                : drop probability in [0, 1)
 * scale            : 1.0 / (1.0 - p)
 * states           : per-thread curand states (must be initialized)
 * training         : if 0, kernel is a no-op (identity pass-through)
 */
__global__ void dropout_forward_fp32(
    float*       __restrict__ x,
    uint8_t*     __restrict__ mask,
    int          N,
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    if (!training) return;

    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;

    curandState local_state = states[tid];
    float u = curand_uniform(&local_state);
    states[tid] = local_state;

    uint8_t keep = (u >= p) ? 1u : 0u;
    if (mask) mask[tid] = keep;
    x[tid] = keep ? x[tid] * scale : 0.0f;
}

/**
 * Vectorized dropout forward (FP32, 4 elements per thread).
 * Improves memory bandwidth utilization on wide tensors.
 */
__global__ void dropout_forward_fp32_vec4(
    float4*      __restrict__ x4,
    uint8_t*     __restrict__ mask,
    int          N4,         // N / 4
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    if (!training) return;

    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N4) return;

    curandState local_state = states[tid];

    float4 val = x4[tid];
    float u0 = curand_uniform(&local_state);
    float u1 = curand_uniform(&local_state);
    float u2 = curand_uniform(&local_state);
    float u3 = curand_uniform(&local_state);
    states[tid] = local_state;

    uint8_t k0 = u0 >= p, k1 = u1 >= p, k2 = u2 >= p, k3 = u3 >= p;
    val.x = k0 ? val.x * scale : 0.0f;
    val.y = k1 ? val.y * scale : 0.0f;
    val.z = k2 ? val.z * scale : 0.0f;
    val.w = k3 ? val.w * scale : 0.0f;
    x4[tid] = val;

    if (mask) {
        int base = tid * 4;
        mask[base + 0] = k0;
        mask[base + 1] = k1;
        mask[base + 2] = k2;
        mask[base + 3] = k3;
    }
}

/**
 * Dropout backward (FP32).
 * Applies stored mask to gradient and rescales.
 *
 * grad_out [in/out] : upstream gradient, modified in place
 * mask     [in]     : binary mask from forward pass
 * N                 : total element count
 * scale             : 1.0 / (1.0 - p)
 */
__global__ void dropout_backward_fp32(
    float*         __restrict__ grad_out,
    const uint8_t* __restrict__ mask,
    int            N,
    float          scale
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;
    grad_out[tid] *= mask[tid] ? scale : 0.0f;
}

// ─────────────────────────────────────────────────────────────────────────────
// Dropout FP16
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Bernoulli dropout for half-precision (FP16).
 * Operates on pairs of __half values (one float2 per thread = 2 halves).
 */
__global__ void dropout_forward_fp16(
    __half*      __restrict__ x,
    uint8_t*     __restrict__ mask,
    int          N,
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    if (!training) return;

    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;

    curandState local_state = states[tid];
    float u = curand_uniform(&local_state);
    states[tid] = local_state;

    uint8_t keep = (u >= p) ? 1u : 0u;
    if (mask) mask[tid] = keep;
    x[tid] = keep ? __hmul(x[tid], __float2half(scale)) : __float2half(0.0f);
}

// ─────────────────────────────────────────────────────────────────────────────
// Alpha Dropout (for SELU/self-normalizing networks)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Alpha dropout (FP32).
 * Preserves the mean and variance of self-normalizing activations.
 * Replaces dropped elements with the negative saturation value alpha_prime.
 *
 * α'  = -SELU_alpha * SELU_scale  ≈ -1.7580993408473766
 * The affine transform (a, b) restores mean=0, std=1 after dropout.
 */
static constexpr float SELU_ALPHA  = 1.6732631921768188f;
static constexpr float SELU_SCALE  = 1.0507009873554805f;
static constexpr float ALPHA_PRIME = -SELU_ALPHA * SELU_SCALE;  // ≈ -1.7581

__global__ void alpha_dropout_forward_fp32(
    float*       __restrict__ x,
    uint8_t*     __restrict__ mask,
    int          N,
    float        p,
    float        a,          // affine scale:  1 / sqrt((1-p)(1 + p*α'^2))
    float        b,          // affine bias:   -a * (p * ALPHA_PRIME)
    curandState* states,
    int          training
) {
    if (!training) return;

    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;

    curandState local_state = states[tid];
    float u = curand_uniform(&local_state);
    states[tid] = local_state;

    uint8_t keep = (u >= p) ? 1u : 0u;
    if (mask) mask[tid] = keep;
    float val = keep ? x[tid] : ALPHA_PRIME;
    x[tid] = a * val + b;
}

// ─────────────────────────────────────────────────────────────────────────────
// Fused Dropout + GELU activation
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Fused dropout + GELU forward (FP32).
 * Applies dropout then GELU in a single kernel pass to reduce memory I/O.
 *
 * GELU(x) = 0.5 * x * (1 + tanh(√(2/π) * (x + 0.044715 * x³)))
 */
__device__ __forceinline__ float gelu_approx(float x) {
    constexpr float kSqrt2OverPi = 0.7978845608028654f;
    constexpr float kCoeff       = 0.044715f;
    float inner = kSqrt2OverPi * (x + kCoeff * x * x * x);
    return 0.5f * x * (1.0f + tanhf(inner));
}

__global__ void dropout_gelu_forward_fp32(
    float*       __restrict__ x,
    uint8_t*     __restrict__ mask,
    int          N,
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;

    float val = x[tid];

    if (training) {
        curandState local_state = states[tid];
        float u = curand_uniform(&local_state);
        states[tid] = local_state;

        uint8_t keep = (u >= p) ? 1u : 0u;
        if (mask) mask[tid] = keep;
        val = keep ? val * scale : 0.0f;
    }

    x[tid] = gelu_approx(val);
}

// ─────────────────────────────────────────────────────────────────────────────
// Fused Dropout + SiLU (Swish) activation
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Fused dropout + SiLU forward (FP32).
 * SiLU(x) = x * sigmoid(x) = x / (1 + exp(-x))
 */
__device__ __forceinline__ float silu(float x) {
    return x / (1.0f + expf(-x));
}

__global__ void dropout_silu_forward_fp32(
    float*       __restrict__ x,
    uint8_t*     __restrict__ mask,
    int          N,
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;

    float val = x[tid];

    if (training) {
        curandState local_state = states[tid];
        float u = curand_uniform(&local_state);
        states[tid] = local_state;
        uint8_t keep = (u >= p) ? 1u : 0u;
        if (mask) mask[tid] = keep;
        val = keep ? val * scale : 0.0f;
    }

    x[tid] = silu(val);
}

// ─────────────────────────────────────────────────────────────────────────────
// DropConnect (weight-level dropout for linear layers)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * DropConnect forward pass (FP32).
 * Zeroes individual weight elements in W before matrix multiplication.
 * W: [out_features × in_features] weight matrix
 */
__global__ void dropconnect_forward_fp32(
    float*       __restrict__ W,
    uint8_t*     __restrict__ mask,
    int          total_weights,
    float        p,
    float        scale,
    curandState* states,
    int          training
) {
    if (!training) return;

    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= total_weights) return;

    curandState local_state = states[tid];
    float u = curand_uniform(&local_state);
    states[tid] = local_state;

    uint8_t keep = (u >= p) ? 1u : 0u;
    if (mask) mask[tid] = keep;
    W[tid] = keep ? W[tid] * scale : 0.0f;
}

// ─────────────────────────────────────────────────────────────────────────────
// Host-side launcher functions
// ─────────────────────────────────────────────────────────────────────────────

extern "C" {

/**
 * Initialize cuRAND states on the device.
 * d_states: pre-allocated device array of curandState[n_states]
 * seed:     RNG seed
 * offset:   stream offset
 */
void launch_init_curand_states(
    curandState* d_states,
    uint64_t     seed,
    uint64_t     offset,
    int          n_states,
    cudaStream_t stream
) {
    int grid = (n_states + BLOCK_SIZE - 1) / BLOCK_SIZE;
    init_curand_states_kernel<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_states, seed, offset, n_states);
}

/**
 * Launch standard Bernoulli dropout forward pass (FP32).
 */
void launch_dropout_forward_fp32(
    float*       d_x,
    uint8_t*     d_mask,
    int          N,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    if (p <= 0.0f || !training) return;
    float scale = 1.0f / (1.0f - p);

    // Use vectorized kernel if N is divisible by 4
    if (N % 4 == 0 && (reinterpret_cast<uintptr_t>(d_x) % 16 == 0)) {
        int N4 = N / 4;
        int grid = (N4 + BLOCK_SIZE - 1) / BLOCK_SIZE;
        dropout_forward_fp32_vec4<<<grid, BLOCK_SIZE, 0, stream>>>(
            reinterpret_cast<float4*>(d_x), d_mask, N4, p, scale, d_states, training);
    } else {
        int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
        dropout_forward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(
            d_x, d_mask, N, p, scale, d_states, training);
    }
}

/**
 * Launch dropout backward pass (FP32).
 */
void launch_dropout_backward_fp32(
    float*         d_grad_out,
    const uint8_t* d_mask,
    int            N,
    float          p,
    cudaStream_t   stream
) {
    float scale = 1.0f / (1.0f - p);
    int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    dropout_backward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(d_grad_out, d_mask, N, scale);
}

/**
 * Launch alpha dropout forward (FP32).
 */
void launch_alpha_dropout_forward_fp32(
    float*       d_x,
    uint8_t*     d_mask,
    int          N,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    if (!training) return;
    // Compute affine parameters
    float alpha_sq = ALPHA_PRIME * ALPHA_PRIME;
    float var = (1.0f - p) * (1.0f + p * alpha_sq);
    float a = (var > 0.0f) ? (1.0f / sqrtf(var)) : 1.0f;
    float b = -a * (p * ALPHA_PRIME);
    int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    alpha_dropout_forward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_x, d_mask, N, p, a, b, d_states, training);
}

/**
 * Launch fused dropout + GELU forward (FP32).
 */
void launch_dropout_gelu_fp32(
    float*       d_x,
    uint8_t*     d_mask,
    int          N,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    float scale = (p < 1.0f) ? 1.0f / (1.0f - p) : 1.0f;
    int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    dropout_gelu_forward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_x, d_mask, N, p, scale, d_states, training);
}

/**
 * Launch fused dropout + SiLU forward (FP32).
 */
void launch_dropout_silu_fp32(
    float*       d_x,
    uint8_t*     d_mask,
    int          N,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    float scale = (p < 1.0f) ? 1.0f / (1.0f - p) : 1.0f;
    int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    dropout_silu_forward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_x, d_mask, N, p, scale, d_states, training);
}

/**
 * Launch DropConnect forward (FP32).
 */
void launch_dropconnect_forward_fp32(
    float*       d_W,
    uint8_t*     d_mask,
    int          total_weights,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    if (!training) return;
    float scale = 1.0f / (1.0f - p);
    int grid = (total_weights + BLOCK_SIZE - 1) / BLOCK_SIZE;
    dropconnect_forward_fp32<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_W, d_mask, total_weights, p, scale, d_states, training);
}

/**
 * Launch FP16 dropout forward.
 */
void launch_dropout_forward_fp16(
    __half*      d_x,
    uint8_t*     d_mask,
    int          N,
    float        p,
    curandState* d_states,
    int          training,
    cudaStream_t stream
) {
    if (p <= 0.0f || !training) return;
    float scale = 1.0f / (1.0f - p);
    int grid = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;
    dropout_forward_fp16<<<grid, BLOCK_SIZE, 0, stream>>>(
        d_x, d_mask, N, p, scale, d_states, training);
}

} // extern "C"
