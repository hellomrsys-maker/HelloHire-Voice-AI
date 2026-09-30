// =============================================================================
// engine/cuda/kernels/layernorm_kernel.cu
// Fused Layer Normalization kernel with RMS normalization variant
// =============================================================================

#include <cuda_runtime.h>
#include <cfloat>
#include <cmath>

#define WARP_SIZE 32

__device__ __forceinline__ float warp_reduce_sum_f(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1)
        val += __shfl_down_sync(0xffffffff, val, offset);
    return val;
}

/**
 * @brief Layer Normalization kernel.
 *
 * For each row of length `hidden_dim`:
 *   μ = mean(x), σ² = var(x)
 *   y = γ * (x - μ) / sqrt(σ² + ε) + β
 *
 * Grid: (num_rows,)
 * Block: (WARP_SIZE * num_warps,)
 */
extern "C" __global__ void layer_norm_kernel(
    const float* __restrict__ input,
    const float* __restrict__ gamma,    // Scale parameter [hidden_dim]
    const float* __restrict__ beta,     // Bias parameter  [hidden_dim]
    float*       __restrict__ output,
    const int    hidden_dim,
    const float  eps
)
{
    const int row = blockIdx.x;
    const int tid = threadIdx.x;
    const float* x_row = input  + row * hidden_dim;
    float*       y_row = output + row * hidden_dim;

    // --- Step 1: Compute mean ---
    float thread_sum = 0.0f;
    for (int i = tid; i < hidden_dim; i += blockDim.x) {
        thread_sum += x_row[i];
    }
    thread_sum = warp_reduce_sum_f(thread_sum);

    __shared__ float smem[64];
    if (tid % WARP_SIZE == 0) smem[tid / WARP_SIZE] = thread_sum;
    __syncthreads();

    float mean = 0.0f;
    if (tid == 0) {
        float total = 0.0f;
        for (int w = 0; w < blockDim.x / WARP_SIZE; ++w) total += smem[w];
        smem[0] = total / (float)hidden_dim;
    }
    __syncthreads();
    mean = smem[0];

    // --- Step 2: Compute variance ---
    float thread_var = 0.0f;
    for (int i = tid; i < hidden_dim; i += blockDim.x) {
        float diff = x_row[i] - mean;
        thread_var += diff * diff;
    }
    thread_var = warp_reduce_sum_f(thread_var);
    if (tid % WARP_SIZE == 0) smem[tid / WARP_SIZE] = thread_var;
    __syncthreads();

    float variance = 0.0f;
    if (tid == 0) {
        float total = 0.0f;
        for (int w = 0; w < blockDim.x / WARP_SIZE; ++w) total += smem[w];
        smem[0] = total / (float)hidden_dim;
    }
    __syncthreads();
    variance = smem[0];

    // --- Step 3: Normalize and scale ---
    const float inv_std = rsqrtf(variance + eps);
    for (int i = tid; i < hidden_dim; i += blockDim.x) {
        y_row[i] = gamma[i] * (x_row[i] - mean) * inv_std + beta[i];
    }
}

/**
 * @brief RMS Normalization kernel (no mean subtraction).
 *
 *   y = γ * x / sqrt(mean(x²) + ε)
 *
 * Used in LLaMA-style models.
 */
extern "C" __global__ void rms_norm_kernel(
    const float* __restrict__ input,
    const float* __restrict__ gamma,
    float*       __restrict__ output,
    const int    hidden_dim,
    const float  eps
)
{
    const int row = blockIdx.x;
    const int tid = threadIdx.x;
    const float* x_row = input  + row * hidden_dim;
    float*       y_row = output + row * hidden_dim;

    // Compute mean(x²)
    float thread_sq = 0.0f;
    for (int i = tid; i < hidden_dim; i += blockDim.x) {
        thread_sq += x_row[i] * x_row[i];
    }
    thread_sq = warp_reduce_sum_f(thread_sq);

    __shared__ float smem[64];
    if (tid % WARP_SIZE == 0) smem[tid / WARP_SIZE] = thread_sq;
    __syncthreads();

    float rms_sq = 0.0f;
    if (tid == 0) {
        float total = 0.0f;
        for (int w = 0; w < blockDim.x / WARP_SIZE; ++w) total += smem[w];
        smem[0] = total / (float)hidden_dim;
    }
    __syncthreads();
    rms_sq = smem[0];

    const float inv_rms = rsqrtf(rms_sq + eps);
    for (int i = tid; i < hidden_dim; i += blockDim.x) {
        y_row[i] = gamma[i] * x_row[i] * inv_rms;
    }
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_layer_norm(
    const float* input, const float* gamma, const float* beta, float* output,
    int num_rows, int hidden_dim, float eps,
    cudaStream_t stream)
{
    const int threads = min(((hidden_dim + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    layer_norm_kernel<<<num_rows, threads, 0, stream>>>(
        input, gamma, beta, output, hidden_dim, eps);
    return cudaGetLastError();
}

cudaError_t launch_rms_norm(
    const float* input, const float* gamma, float* output,
    int num_rows, int hidden_dim, float eps,
    cudaStream_t stream)
{
    const int threads = min(((hidden_dim + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    rms_norm_kernel<<<num_rows, threads, 0, stream>>>(
        input, gamma, output, hidden_dim, eps);
    return cudaGetLastError();
}

} // extern "C"
