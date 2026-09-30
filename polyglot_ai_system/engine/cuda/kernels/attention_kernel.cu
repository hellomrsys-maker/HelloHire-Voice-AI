// =============================================================================
// engine/cuda/kernels/attention_kernel.cu
// Flash Attention 2 — GPU kernel for scaled dot-product attention
// Implements tiling strategies and memory coalescing for maximum throughput.
//
// Based on: Dao et al. (2023) "FlashAttention-2: Faster Attention with Better
//            Parallelism and Work Partitioning"
// =============================================================================

#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <mma.h>
#include <cooperative_groups.h>
#include <cmath>
#include <cfloat>

namespace cg = cooperative_groups;

// =============================================================================
// Configuration constants
// =============================================================================

// Tile size for FlashAttention (must be power of 2 and ≤ 128 for shared mem)
#define BLOCK_M 64    // Rows of Q per block
#define BLOCK_N 64    // Rows of K/V per block
#define WARP_SIZE 32
#define NUM_WARPS 4

// Maximum head dimension supported
#define MAX_HEAD_DIM 128

// =============================================================================
// Helper: Online softmax with running max (numerically stable)
// =============================================================================

struct SoftmaxState {
    float running_max;
    float running_sum;

    __device__ __forceinline__ SoftmaxState() :
        running_max(-FLT_MAX), running_sum(0.0f) {}

    // Update with new block of scores
    __device__ __forceinline__ void update(float new_max) {
        float old_max = running_max;
        running_max   = fmaxf(old_max, new_max);
        running_sum  *= expf(old_max - running_max);
    }
};

// =============================================================================
// FlashAttention forward kernel
// =============================================================================

/**
 * @brief FlashAttention 2 forward pass kernel.
 *
 * Computes attention output O = softmax(QK^T / sqrt(d_k)) * V
 * in a single pass with O(seq_len) HBM accesses.
 *
 * Grid: (batch_size, num_heads, ceil(seq_len / BLOCK_M))
 * Block: (WARP_SIZE * NUM_WARPS,) = 128 threads
 *
 * @param Q         Query tensor  [batch, heads, seq_len, head_dim]
 * @param K         Key tensor    [batch, heads, seq_len, head_dim]
 * @param V         Value tensor  [batch, heads, seq_len, head_dim]
 * @param O         Output tensor [batch, heads, seq_len, head_dim]
 * @param L         Log-sum-exp   [batch, heads, seq_len]  (for backward)
 * @param seq_len   Sequence length
 * @param head_dim  Dimension per head (d_k)
 * @param scale     1/sqrt(d_k)
 * @param causal    Whether to apply causal (lower-triangular) mask
 */
extern "C" __global__ void flash_attention_forward(
    const float* __restrict__ Q,      // [B, H, N, D]
    const float* __restrict__ K,      // [B, H, N, D]
    const float* __restrict__ V,      // [B, H, N, D]
    float*       __restrict__ O,      // [B, H, N, D]
    float*       __restrict__ L,      // [B, H, N]     log-sum-exp per query
    const int    seq_len,
    const int    head_dim,
    const float  scale,
    const bool   causal
)
{
    // Identify this thread block's batch, head, and query tile
    const int batch_id = blockIdx.x;
    const int head_id  = blockIdx.y;
    const int q_tile   = blockIdx.z;  // Which tile of Q rows we handle

    const int q_start  = q_tile * BLOCK_M;
    const int q_end    = min(q_start + BLOCK_M, seq_len);

    const int tid      = threadIdx.x;
    const int lane_id  = tid % WARP_SIZE;
    const int warp_id  = tid / WARP_SIZE;

    // Strides for 4D tensor indexing: [B, H, N, D]
    const long stride_b = (long)seq_len * head_dim;
    const long stride_h = (long)seq_len * head_dim;
    const long base_offset = ((long)batch_id * gridDim.y + head_id) * seq_len * head_dim;

    // Shared memory: tile of Q, K, V, and output accumulator
    // Layout: Q_tile [BLOCK_M × head_dim], K_tile [BLOCK_N × head_dim], V_tile [BLOCK_N × head_dim]
    extern __shared__ float smem[];
    float* Q_tile  = smem;
    float* K_tile  = Q_tile + BLOCK_M * MAX_HEAD_DIM;
    float* V_tile  = K_tile + BLOCK_N * MAX_HEAD_DIM;
    float* O_tile  = V_tile + BLOCK_N * MAX_HEAD_DIM;
    float* m_tile  = O_tile + BLOCK_M * MAX_HEAD_DIM;  // Running max per query
    float* l_tile  = m_tile + BLOCK_M;                  // Running sum per query

    // Initialize output, running max, and sum
    const int q_rows_this_block = q_end - q_start;
    for (int i = tid; i < q_rows_this_block; i += blockDim.x) {
        m_tile[i] = -FLT_MAX;
        l_tile[i] = 0.0f;
        for (int d = 0; d < head_dim; ++d) {
            O_tile[i * head_dim + d] = 0.0f;
        }
    }
    __syncthreads();

    // Load Q tile into shared memory
    for (int i = tid; i < q_rows_this_block * head_dim; i += blockDim.x) {
        int q_row = i / head_dim;
        int d     = i % head_dim;
        int global_row = q_start + q_row;
        Q_tile[i] = (global_row < seq_len) ?
            Q[base_offset + global_row * head_dim + d] : 0.0f;
    }
    __syncthreads();

    // Iterate over K/V tiles
    const int num_kv_tiles = (seq_len + BLOCK_N - 1) / BLOCK_N;
    for (int kv_tile = 0; kv_tile < num_kv_tiles; ++kv_tile) {
        const int kv_start = kv_tile * BLOCK_N;
        const int kv_end   = min(kv_start + BLOCK_N, seq_len);
        const int kv_rows  = kv_end - kv_start;

        // Causal mask: skip tiles that are entirely in the future
        if (causal && kv_start > q_end) break;

        // Load K tile into shared memory
        for (int i = tid; i < kv_rows * head_dim; i += blockDim.x) {
            int kv_row = i / head_dim;
            int d      = i % head_dim;
            K_tile[i]  = K[base_offset + (kv_start + kv_row) * head_dim + d];
        }

        // Load V tile into shared memory
        for (int i = tid; i < kv_rows * head_dim; i += blockDim.x) {
            int kv_row = i / head_dim;
            int d      = i % head_dim;
            V_tile[i]  = V[base_offset + (kv_start + kv_row) * head_dim + d];
        }
        __syncthreads();

        // Each thread handles one query row
        if (tid < q_rows_this_block) {
            const int qi = tid;
            const int global_qi = q_start + qi;

            // Compute S = Q[qi] @ K_tile^T / scale for all kv rows
            float S[BLOCK_N];
            float S_max = -FLT_MAX;

            for (int kv_j = 0; kv_j < kv_rows; ++kv_j) {
                // Causal mask: Q[i] should not attend to K[j] if j > i
                if (causal && (kv_start + kv_j) > global_qi) {
                    S[kv_j] = -FLT_MAX;
                    continue;
                }

                float dot = 0.0f;
                for (int d = 0; d < head_dim; ++d) {
                    dot += Q_tile[qi * head_dim + d] * K_tile[kv_j * head_dim + d];
                }
                S[kv_j] = dot * scale;
                S_max   = fmaxf(S_max, S[kv_j]);
            }

            // Online softmax update
            float old_m = m_tile[qi];
            float new_m = fmaxf(old_m, S_max);
            float scale_old = expf(old_m - new_m);

            // Update output accumulator: rescale by exp(m_old - m_new)
            for (int d = 0; d < head_dim; ++d) {
                O_tile[qi * head_dim + d] *= scale_old;
            }
            l_tile[qi] *= scale_old;

            // Compute exp(S - new_m) and accumulate weighted V
            for (int kv_j = 0; kv_j < kv_rows; ++kv_j) {
                float p = expf(S[kv_j] - new_m);
                l_tile[qi] += p;
                for (int d = 0; d < head_dim; ++d) {
                    O_tile[qi * head_dim + d] += p * V_tile[kv_j * head_dim + d];
                }
            }

            m_tile[qi] = new_m;
        }
        __syncthreads();
    }

    // Normalize output by l (running sum) and write to global memory
    if (tid < q_rows_this_block) {
        const int qi = tid;
        const int global_qi = q_start + qi;
        const float l_inv   = 1.0f / (l_tile[qi] + 1e-9f);

        // Store log-sum-exp for backward pass: L[qi] = log(l) + m
        L[((long)batch_id * gridDim.y + head_id) * seq_len + global_qi] =
            m_tile[qi] + logf(l_tile[qi] + 1e-9f);

        for (int d = 0; d < head_dim; ++d) {
            O[base_offset + global_qi * head_dim + d] =
                O_tile[qi * head_dim + d] * l_inv;
        }
    }
}

// =============================================================================
// Flash Attention forward kernel launcher (C linkage for FFI)
// =============================================================================

extern "C" {

/**
 * @brief Launches the FlashAttention forward kernel.
 *
 * @param Q, K, V, O  Device pointers to float32 tensors [B, H, N, D]
 * @param L           Device pointer for log-sum-exp [B, H, N]
 * @param batch       Batch size
 * @param heads       Number of attention heads
 * @param seq_len     Sequence length
 * @param head_dim    Dimension per head
 * @param causal      Whether to apply causal mask
 * @param stream      CUDA stream to launch on (null = default stream)
 * @returns           cudaError_t
 */
cudaError_t launch_flash_attention_forward(
    const float* Q, const float* K, const float* V,
    float* O, float* L,
    int batch, int heads, int seq_len, int head_dim,
    bool causal, cudaStream_t stream)
{
    const float scale = 1.0f / sqrtf(static_cast<float>(head_dim));
    const int num_q_tiles = (seq_len + BLOCK_M - 1) / BLOCK_M;

    dim3 grid(batch, heads, num_q_tiles);
    dim3 block(WARP_SIZE * NUM_WARPS);

    // Shared memory: Q_tile + K_tile + V_tile + O_tile + m_tile + l_tile
    size_t smem_bytes = (size_t)(
        BLOCK_M * MAX_HEAD_DIM   // Q_tile
        + BLOCK_N * MAX_HEAD_DIM // K_tile
        + BLOCK_N * MAX_HEAD_DIM // V_tile
        + BLOCK_M * MAX_HEAD_DIM // O_tile
        + BLOCK_M                // m_tile
        + BLOCK_M                // l_tile
    ) * sizeof(float);

    flash_attention_forward<<<grid, block, smem_bytes, stream>>>(
        Q, K, V, O, L,
        seq_len, head_dim, scale, causal);

    return cudaGetLastError();
}

} // extern "C"
