/**
 * @file irt_parallel_eval.cu
 * @brief CUDA Kernel for Ultra-Low Latency Parallel 3PL Item Response Theory (IRT) Item Bank Search.
 *
 * Evaluates Fisher Information across 10,000+ calibrated items in parallel
 * to select the optimal next question for adaptive examination in < 10 microseconds.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32

/**
 * Warp-level parallel reduction to find (max_value, argmax_index).
 */
__device__ inline void warp_reduce_max_with_idx(float& val, int& idx) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        float other_val = __shfl_down_sync(0xFFFFFFFF, val, offset);
        int other_idx   = __shfl_down_sync(0xFFFFFFFF, idx, offset);
        if (other_val > val) {
            val = other_val;
            idx = other_idx;
        }
    }
}

/**
 * Kernel: evaluate_item_bank_parallel
 *
 * Each thread block processes one candidate ability theta against all items in the item bank.
 */
__global__ void evaluate_item_bank_parallel(
    const float* __restrict__ theta_candidates,
    const float* __restrict__ item_a,
    const float* __restrict__ item_b,
    const float* __restrict__ item_c,
    const unsigned char* __restrict__ item_administered,
    int* __restrict__ out_best_item_idx,
    float* __restrict__ out_max_info,
    int num_candidates,
    int num_items
) {
    int candidate_idx = blockIdx.x;
    if (candidate_idx >= num_candidates) return;

    float theta = theta_candidates[candidate_idx];
    int tid = threadIdx.x;
    int stride = blockDim.x;

    float local_max_info = -1.0f;
    int local_best_idx = -1;

    // Grid-stride loop over item bank
    for (int i = tid; i < num_items; i += stride) {
        if (item_administered[i] != 0) {
            continue; // Item already administered
        }

        float a = item_a[i];
        float b = item_b[i];
        float c = item_c[i];

        // 3PL Probability: P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
        float exp_term = expf(-fmaxf(-25.0f, fminf(25.0f, a * (theta - b))));
        float p_star = 1.0f / (1.0f + exp_term);
        float p = c + (1.0f - c) * p_star;

        if (p > c && p < 1.0f) {
            float numerator = (a * a) * (p_star * p_star) * (1.0f - p);
            float info = numerator / p;

            if (info > local_max_info) {
                local_max_info = info;
                local_best_idx = i;
            }
        }
    }

    // Shared memory reduction
    __shared__ float s_max_info[WARP_SIZE];
    __shared__ int   s_best_idx[WARP_SIZE];

    int lane = tid % WARP_SIZE;
    int warp_id = tid / WARP_SIZE;

    warp_reduce_max_with_idx(local_max_info, local_best_idx);

    if (lane == 0) {
        s_max_info[warp_id] = local_max_info;
        s_best_idx[warp_id] = local_best_idx;
    }
    __syncthreads();

    // Final reduction by first warp
    if (warp_id == 0) {
        int num_warps = blockDim.x / WARP_SIZE;
        float block_max_info = (lane < num_warps) ? s_max_info[lane] : -1.0f;
        int   block_best_idx = (lane < num_warps) ? s_best_idx[lane] : -1;

        warp_reduce_max_with_idx(block_max_info, block_best_idx);

        if (lane == 0) {
            out_best_item_idx[candidate_idx] = block_best_idx;
            out_max_info[candidate_idx] = block_max_info;
        }
    }
}

extern "C" {

/**
 * Host wrapper for launching parallel IRT item selection.
 */
cudaError_t launch_parallel_irt_evaluation(
    const float* d_theta_candidates,
    const float* d_item_a,
    const float* d_item_b,
    const float* d_item_c,
    const unsigned char* d_item_administered,
    int* d_out_best_item_idx,
    float* d_out_max_info,
    int num_candidates,
    int num_items,
    cudaStream_t stream
) {
    dim3 block(256); // 8 warps per block
    dim3 grid(num_candidates);

    evaluate_item_bank_parallel<<<grid, block, 0, stream>>>(
        d_theta_candidates,
        d_item_a,
        d_item_b,
        d_item_c,
        d_item_administered,
        d_out_best_item_idx,
        d_out_max_info,
        num_candidates,
        num_items
    );

    return cudaGetLastError();
}

} // extern "C"
