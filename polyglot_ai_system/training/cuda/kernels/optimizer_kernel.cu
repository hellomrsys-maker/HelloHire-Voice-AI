// =============================================================================
// training/cuda/kernels/optimizer_kernel.cu
// CUDA kernels for Adam / AdamW optimizer parameter updates.
// Fused to minimize global memory round-trips.
// =============================================================================

#include <cuda_runtime.h>
#include <cmath>

/**
 * @brief Fused AdamW optimizer kernel.
 *
 * Per parameter:
 *   m = β₁ * m + (1 - β₁) * g
 *   v = β₂ * v + (1 - β₂) * g²
 *   m_hat = m / (1 - β₁^t)
 *   v_hat = v / (1 - β₂^t)
 *   p -= lr * (m_hat / (√v_hat + ε) + λ * p)
 *
 * Grid: (ceil(n_params / block_size),)
 * Block: (block_size,)
 *
 * @param params      [n_params] parameter vector (updated in-place)
 * @param grads       [n_params] gradient vector
 * @param m_state     [n_params] first moment vector (updated in-place)
 * @param v_state     [n_params] second moment vector (updated in-place)
 * @param n_params    Number of parameters
 * @param lr          Current learning rate
 * @param beta1       β₁ (default 0.9)
 * @param beta2       β₂ (default 0.999)
 * @param eps         ε for numerical stability (default 1e-8)
 * @param weight_decay λ for decoupled weight decay (AdamW)
 * @param bias_corr1  1 - β₁^t (bias correction factor)
 * @param bias_corr2  1 - β₂^t
 */
extern "C" __global__ void adamw_kernel(
    float*       __restrict__ params,
    const float* __restrict__ grads,
    float*       __restrict__ m_state,
    float*       __restrict__ v_state,
    const int    n_params,
    const float  lr,
    const float  beta1,
    const float  beta2,
    const float  eps,
    const float  weight_decay,
    const float  bias_corr1,
    const float  bias_corr2
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_params) return;

    const float g = grads[idx];
    float m = beta1 * m_state[idx] + (1.0f - beta1) * g;
    float v = beta2 * v_state[idx] + (1.0f - beta2) * g * g;

    m_state[idx] = m;
    v_state[idx] = v;

    const float m_hat = m / bias_corr1;
    const float v_hat = v / bias_corr2;

    // AdamW: decoupled weight decay
    params[idx] -= lr * (m_hat / (sqrtf(v_hat) + eps) + weight_decay * params[idx]);
}

/**
 * @brief Gradient clipping kernel.
 * Clips gradient vector to max_norm (global L2 norm clipping).
 *
 * Note: This kernel should be called AFTER computing the global norm
 * (done on CPU or via a separate reduction kernel).
 *
 * @param grads        [n_params] gradient vector (clipped in-place)
 * @param clip_scale   Clipping scale factor = min(1, max_norm / global_norm)
 * @param n_params     Number of parameters
 */
extern "C" __global__ void gradient_clip_kernel(
    float*      __restrict__ grads,
    const float clip_scale,
    const int   n_params
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_params) return;
    grads[idx] *= clip_scale;
}

/**
 * @brief L2 norm squared reduction kernel.
 * Computes ∑ grads[i]² (needed for gradient clipping).
 *
 * Grid: (1,)
 * Block: (1024,)
 */
extern "C" __global__ void l2_norm_sq_kernel(
    const float* __restrict__ grads,
    float*       __restrict__ norm_sq,
    const int    n_params
)
{
    __shared__ float smem[1024];
    const int tid = threadIdx.x;
    float thread_val = 0.0f;

    for (int i = tid; i < n_params; i += blockDim.x)
        thread_val += grads[i] * grads[i];

    smem[tid] = thread_val;
    __syncthreads();

    // Block-level reduction
    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (tid < stride) smem[tid] += smem[tid + stride];
        __syncthreads();
    }

    if (tid == 0) atomicAdd(norm_sq, smem[0]);
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_adamw(
    float* params, const float* grads,
    float* m_state, float* v_state,
    int n_params, float lr,
    float beta1, float beta2, float eps,
    float weight_decay, int step,
    cudaStream_t stream)
{
    float bc1 = 1.0f - powf(beta1, (float)step);
    float bc2 = 1.0f - powf(beta2, (float)step);
    const int block = 1024;
    const int grid  = (n_params + block - 1) / block;
    adamw_kernel<<<grid, block, 0, stream>>>(
        params, grads, m_state, v_state,
        n_params, lr, beta1, beta2, eps, weight_decay, bc1, bc2);
    return cudaGetLastError();
}

cudaError_t launch_gradient_clip(
    float* grads, float max_norm, float global_norm,
    int n_params, cudaStream_t stream)
{
    if (global_norm <= max_norm) return cudaSuccess;
    float scale = max_norm / (global_norm + 1e-9f);
    const int block = 1024;
    const int grid  = (n_params + block - 1) / block;
    gradient_clip_kernel<<<grid, block, 0, stream>>>(grads, scale, n_params);
    return cudaGetLastError();
}

cudaError_t launch_l2_norm_sq(
    const float* grads, float* norm_sq,
    int n_params, cudaStream_t stream)
{
    cudaMemsetAsync(norm_sq, 0, sizeof(float), stream);
    l2_norm_sq_kernel<<<1, 1024, 0, stream>>>(grads, norm_sq, n_params);
    return cudaGetLastError();
}

} // extern "C"
