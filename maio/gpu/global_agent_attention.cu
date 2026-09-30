/**
 * @file global_agent_attention.cu
 * @brief CUDA Kernel for Global Multi-Agent Cross-Attention in MAIO.
 *
 * Implements parallel scaled dot-product cross-attention across all active sub-engines
 * (VCE, CCTE-8, RSSE, AEEE) to synchronize global context and dynamic prioritization.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define NUM_AGENTS 11   // VCE(1) + CCTE(8) + RSSE(1) + AEEE(1)
#define HEAD_DIM 64
#define WARP_SIZE 32

__device__ inline float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

__device__ inline float warp_reduce_max(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val = fmaxf(val, __shfl_down_sync(0xFFFFFFFF, val, offset));
    }
    return val;
}

/**
 * Kernel: agent_cross_attention_kernel
 *
 * Computes:
 * 1. Score[i, j] = (Q[i] · K[j]) / sqrt(HEAD_DIM)
 * 2. Attn[i, j] = Softmax_j(Score[i, j])
 * 3. Out[i] = sum_j (Attn[i, j] * V[j])
 *
 * Block Dim: 64 threads (1 thread per feature dimension of HEAD_DIM)
 * Grid Dim: NUM_AGENTS (each block handles agent i's attention over all agents j)
 */
__global__ void agent_cross_attention_kernel(
    const float* __restrict__ Q,         // [NUM_AGENTS x HEAD_DIM]
    const float* __restrict__ K,         // [NUM_AGENTS x HEAD_DIM]
    const float* __restrict__ V,         // [NUM_AGENTS x HEAD_DIM]
    float* __restrict__ attention_matrix,// [NUM_AGENTS x NUM_AGENTS]
    float* __restrict__ Out              // [NUM_AGENTS x HEAD_DIM]
) {
    int i = blockIdx.x; // Query agent index
    int tid = threadIdx.x; // Dimension index [0..63]

    if (i >= NUM_AGENTS || tid >= HEAD_DIM) return;

    __shared__ float s_scores[NUM_AGENTS];
    __shared__ float s_q[HEAD_DIM];

    // Load Q[i] into shared memory
    s_q[tid] = Q[i * HEAD_DIM + tid];
    __syncthreads();

    // 1. Compute dot product Q[i] · K[j] for each agent j
    for (int j = 0; j < NUM_AGENTS; ++j) {
        float q_val = s_q[tid];
        float k_val = K[j * HEAD_DIM + tid];
        float prod = q_val * k_val;

        // Reduce across 64 threads (2 warps)
        float warp_sum = warp_reduce_sum(prod);
        __shared__ float s_warp_sums[2];
        int warp_id = tid / WARP_SIZE;
        int lane = tid % WARP_SIZE;

        if (lane == 0) {
            s_warp_sums[warp_id] = warp_sum;
        }
        __syncthreads();

        if (tid == 0) {
            float total_dot = s_warp_sums[0] + s_warp_sums[1];
            s_scores[j] = total_dot * (1.0f / 8.0f); // 1.0f / sqrt(64)
        }
        __syncthreads();
    }

    // 2. Compute Softmax over scores for agent i
    if (tid == 0) {
        float max_val = -1e9f;
        for (int j = 0; j < NUM_AGENTS; ++j) {
            if (s_scores[j] > max_val) max_val = s_scores[j];
        }

        float sum_exp = 0.0f;
        for (int j = 0; j < NUM_AGENTS; ++j) {
            s_scores[j] = expf(s_scores[j] - max_val);
            sum_exp += s_scores[j];
        }

        float inv_sum = 1.0f / (sum_exp + 1e-8f);
        for (int j = 0; j < NUM_AGENTS; ++j) {
            s_scores[j] *= inv_sum;
            attention_matrix[i * NUM_AGENTS + j] = s_scores[j];
        }
    }
    __syncthreads();

    // 3. Compute Out[i, tid] = sum_j (s_scores[j] * V[j, tid])
    float out_val = 0.0f;
    for (int j = 0; j < NUM_AGENTS; ++j) {
        float weight = s_scores[j];
        float v_val = V[j * HEAD_DIM + tid];
        out_val += weight * v_val;
    }

    Out[i * HEAD_DIM + tid] = out_val;
}

extern "C" {

cudaError_t launch_agent_cross_attention(
    const float* d_Q,
    const float* d_K,
    const float* d_V,
    float* d_attention_matrix,
    float* d_Out,
    cudaStream_t stream
) {
    dim3 block(HEAD_DIM);
    dim3 grid(NUM_AGENTS);

    agent_cross_attention_kernel<<<grid, block, 0, stream>>>(
        d_Q, d_K, d_V, d_attention_matrix, d_Out
    );

    return cudaGetLastError();
}

} // extern "C"
