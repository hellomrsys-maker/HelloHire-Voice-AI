// =============================================================================
// engine/cuda/kernels/fused_rope_kernel.cu
// Fused Rotary Positional Encoding kernel — applies RoPE to Q and K
// simultaneously in a single kernel launch.
// =============================================================================

#include <cuda_runtime.h>
#include <cmath>

/**
 * @brief Fused RoPE kernel for Q and K tensors.
 *
 * Applies RoPE to both Q and K in a single pass.
 * Tensors are [seq_len, num_heads, head_dim].
 *
 * Rotation:
 *   x'[i]            = x[i] * cos(m * θᵢ) - x[i + d/2] * sin(m * θᵢ)
 *   x'[i + d/2]      = x[i] * sin(m * θᵢ) + x[i + d/2] * cos(m * θᵢ)
 *
 * where θᵢ = base^(-2i/d), m = position index.
 *
 * Grid: (seq_len, num_heads)
 * Block: (head_dim / 2,)
 */
extern "C" __global__ void fused_rope_kernel(
    float*       __restrict__ Q,         // [seq_len, num_heads, head_dim]
    float*       __restrict__ K,         // [seq_len, num_heads, head_dim]
    const float* __restrict__ cos_cache, // [max_seq_len, head_dim/2]
    const float* __restrict__ sin_cache, // [max_seq_len, head_dim/2]
    const int    seq_len,
    const int    num_heads,
    const int    head_dim,
    const int    offset                  // Starting position offset
)
{
    const int pos      = blockIdx.x;  // Sequence position
    const int head     = blockIdx.y;  // Attention head
    const int i        = threadIdx.x; // Dimension index [0, head_dim/2)
    const int half_dim = head_dim / 2;

    if (i >= half_dim) return;

    const int abs_pos = pos + offset;
    const float cos_val = cos_cache[abs_pos * half_dim + i];
    const float sin_val = sin_cache[abs_pos * half_dim + i];

    const int base_idx = (pos * num_heads + head) * head_dim;

    // Apply to Q
    {
        float x0 = Q[base_idx + i];
        float x1 = Q[base_idx + i + half_dim];
        Q[base_idx + i]           = x0 * cos_val - x1 * sin_val;
        Q[base_idx + i + half_dim] = x0 * sin_val + x1 * cos_val;
    }

    // Apply to K
    {
        float x0 = K[base_idx + i];
        float x1 = K[base_idx + i + half_dim];
        K[base_idx + i]           = x0 * cos_val - x1 * sin_val;
        K[base_idx + i + half_dim] = x0 * sin_val + x1 * cos_val;
    }
}

/**
 * @brief Precompute RoPE frequency tables and store in device memory.
 *
 * Grid: (max_seq_len,)
 * Block: (head_dim / 2,)
 */
extern "C" __global__ void rope_precompute_kernel(
    float*      __restrict__ cos_cache,
    float*      __restrict__ sin_cache,
    const int   max_seq_len,
    const int   head_dim,
    const float base
)
{
    const int pos = blockIdx.x;
    const int i   = threadIdx.x;
    const int half_dim = head_dim / 2;

    if (i >= half_dim) return;

    float theta = powf(base, -2.0f * (float)i / (float)head_dim);
    float angle = (float)pos * theta;

    cos_cache[pos * half_dim + i] = cosf(angle);
    sin_cache[pos * half_dim + i] = sinf(angle);
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_precompute_rope(
    float* cos_cache, float* sin_cache,
    int max_seq_len, int head_dim, float base,
    cudaStream_t stream)
{
    rope_precompute_kernel<<<max_seq_len, head_dim / 2, 0, stream>>>(
        cos_cache, sin_cache, max_seq_len, head_dim, base);
    return cudaGetLastError();
}

cudaError_t launch_fused_rope(
    float* Q, float* K,
    const float* cos_cache, const float* sin_cache,
    int seq_len, int num_heads, int head_dim, int offset,
    cudaStream_t stream)
{
    dim3 grid(seq_len, num_heads);
    dim3 block(head_dim / 2);
    fused_rope_kernel<<<grid, block, 0, stream>>>(
        Q, K, cos_cache, sin_cache, seq_len, num_heads, head_dim, offset);
    return cudaGetLastError();
}

} // extern "C"
