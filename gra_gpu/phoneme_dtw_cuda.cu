/**
 * @file phoneme_dtw_cuda.cu
 * @brief CUDA Kernel for Parallel Phonetic Dynamic Time Warping (DTW) with Sakoe-Chiba Band Pruning.
 *
 * Computes minimum cumulative acoustic-phonetic alignment distance between
 * candidate audio feature sequences and native target IPA phone templates.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <cfloat>

#define FEATURE_DIM 39 // 13 MFCC + Delta + Delta-Delta
#define MAX_TIME 256

/**
 * Kernel: parallel_phonetic_dtw_kernel
 *
 * Each block processes one (candidate, template) sequence pair.
 * Utilizes shared memory for the local DTW cumulative cost matrix.
 */
__global__ void parallel_phonetic_dtw_kernel(
    const float* __restrict__ candidate_mfcc, // [Batch x T_cand x 39]
    const float* __restrict__ template_mfcc,  // [Batch x T_temp x 39]
    float* __restrict__ out_alignment_costs,  // [Batch]
    int t_cand,
    int t_temp,
    int band_radius,
    int num_pairs
) {
    int pair_idx = blockIdx.x;
    if (pair_idx >= num_pairs) return;

    __shared__ float cost_prev[MAX_TIME];
    __shared__ float cost_curr[MAX_TIME];

    const float* c_seq = candidate_mfcc + (pair_idx * t_cand * FEATURE_DIM);
    const float* t_seq = template_mfcc + (pair_idx * t_temp * FEATURE_DIM);

    int tid = threadIdx.x;

    // Initialize DP rows
    for (int j = tid; j < t_temp; j += blockDim.x) {
        cost_prev[j] = FLT_MAX;
        cost_curr[j] = FLT_MAX;
    }
    __syncthreads();

    // Iterate through candidate frames (rows)
    for (int i = 0; i < t_cand; ++i) {
        const float* c_frame = c_seq + (i * FEATURE_DIM);

        for (int j = tid; j < t_temp; j += blockDim.x) {
            // Check Sakoe-Chiba constraint: |i - j| <= band_radius
            if (abs(i - j) > band_radius) {
                cost_curr[j] = FLT_MAX;
                continue;
            }

            const float* t_frame = t_seq + (j * FEATURE_DIM);

            // Compute Euclidean frame distance across 39 dimensions
            float dist = 0.0f;
            for (int d = 0; d < FEATURE_DIM; ++d) {
                float diff = c_frame[d] - t_frame[d];
                dist += diff * diff;
            }
            dist = sqrtf(dist);

            if (i == 0 && j == 0) {
                cost_curr[j] = dist;
            } else {
                float diag = (i > 0 && j > 0) ? cost_prev[j - 1] : FLT_MAX;
                float up = (i > 0) ? cost_prev[j] : FLT_MAX;
                float left = (j > 0) ? cost_curr[j - 1] : FLT_MAX;

                float min_prev = fminf(diag, fminf(up, left));
                cost_curr[j] = (min_prev < FLT_MAX) ? (min_prev + dist) : FLT_MAX;
            }
        }
        __syncthreads();

        // Swap cost_prev and cost_curr
        for (int j = tid; j < t_temp; j += blockDim.x) {
            cost_prev[j] = cost_curr[j];
        }
        __syncthreads();
    }

    if (tid == 0) {
        float total_cost = cost_prev[t_temp - 1];
        float norm_cost = total_cost / static_cast<float>(t_cand + t_temp);
        out_alignment_costs[pair_idx] = norm_cost;
    }
}

extern "C" {

cudaError_t launch_phonetic_dtw(
    const float* d_cand_mfcc,
    const float* d_temp_mfcc,
    float* d_out_costs,
    int t_cand,
    int t_temp,
    int band_radius,
    int num_pairs,
    cudaStream_t stream
) {
    dim3 grid(num_pairs);
    dim3 block(128);
    parallel_phonetic_dtw_kernel<<<grid, block, 0, stream>>>(
        d_cand_mfcc, d_temp_mfcc, d_out_costs, t_cand, t_temp, band_radius, num_pairs
    );
    return cudaGetLastError();
}

} // extern "C"
