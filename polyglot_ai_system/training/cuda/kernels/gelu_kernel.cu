// =============================================================================
// training/cuda/kernels/gelu_kernel.cu
// CUDA kernels for GELU activation and its derivative.
// Used in transformer FFN layers.
// =============================================================================

#include <cuda_runtime.h>
#include <cmath>

// Approximate GELU: x * 0.5 * (1 + tanh(sqrt(2/π) * (x + 0.044715 * x^3)))
__device__ __forceinline__ float gelu_approx(float x) {
    const float k0 = 0.7978845608028654f;  // sqrt(2/pi)
    const float k1 = 0.044715f;
    float inner = k0 * (x + k1 * x * x * x);
    return 0.5f * x * (1.0f + tanhf(inner));
}

// Derivative of approximate GELU
__device__ __forceinline__ float gelu_approx_grad(float x) {
    const float k0 = 0.7978845608028654f;
    const float k1 = 0.044715f;
    float t  = tanhf(k0 * (x + k1 * x * x * x));
    float dt = k0 * (1.0f + 3.0f * k1 * x * x);
    return 0.5f * (1.0f + t) + 0.5f * x * (1.0f - t * t) * dt;
}

// Exact GELU: x * 0.5 * (1 + erf(x / sqrt(2)))
__device__ __forceinline__ float gelu_exact(float x) {
    return 0.5f * x * (1.0f + erff(x * 0.7071067811865476f));  // 1/sqrt(2)
}

__device__ __forceinline__ float gelu_exact_grad(float x) {
    const float inv_sqrt2   = 0.7071067811865476f;
    const float inv_sqrt2pi = 0.3989422804014327f;
    return 0.5f * (1.0f + erff(x * inv_sqrt2)) + x * inv_sqrt2pi * expf(-0.5f * x * x);
}

/**
 * @brief Element-wise GELU forward kernel.
 *
 * Grid: (ceil(n / block_size),)
 * Block: (block_size,) up to 1024
 */
extern "C" __global__ void gelu_kernel(
    const float* __restrict__ input,
    float*       __restrict__ output,
    const int    n,
    const bool   approximate  // Use approximate (faster) or exact GELU
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;
    output[idx] = approximate ? gelu_approx(input[idx]) : gelu_exact(input[idx]);
}

/**
 * @brief Element-wise GELU backward kernel.
 * Computes element-wise: grad_input[i] = grad_output[i] * d(GELU)/dx(input[i])
 */
extern "C" __global__ void gelu_backward_kernel(
    const float* __restrict__ grad_output,
    const float* __restrict__ input,
    float*       __restrict__ grad_input,
    const int    n,
    const bool   approximate
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;
    float gelu_grad = approximate ? gelu_approx_grad(input[idx]) : gelu_exact_grad(input[idx]);
    grad_input[idx] = grad_output[idx] * gelu_grad;
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_gelu(
    const float* input, float* output, int n,
    bool approximate, cudaStream_t stream)
{
    const int block = 1024;
    const int grid  = (n + block - 1) / block;
    gelu_kernel<<<grid, block, 0, stream>>>(input, output, n, approximate);
    return cudaGetLastError();
}

cudaError_t launch_gelu_backward(
    const float* grad_output, const float* input, float* grad_input,
    int n, bool approximate, cudaStream_t stream)
{
    const int block = 1024;
    const int grid  = (n + block - 1) / block;
    gelu_backward_kernel<<<grid, block, 0, stream>>>(
        grad_output, input, grad_input, n, approximate);
    return cudaGetLastError();
}

} // extern "C"
