/**
 * @file verbal_kernels.cu
 * @brief CUDA Massively Parallel GPU Acceleration Kernels for Recruitment Verbal Communication.
 *
 * Implements:
 * 1. Parallel Keyword & Professional Jargon Match Kernel across candidate utterance tokens.
 * 2. Vocal Jitter & Shimmer Perturbation Analysis Kernel for candidate confidence estimation.
 * 3. Warp-Level Reduction for Real-Time STAR Coherence Matrix.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32
#define MAX_JARGON_COUNT 128

/**
 * Warp-level parallel reduction for summing floats.
 */
__device__ inline float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

/**
 * Kernel 1: parallel_jargon_density_kernel
 *
 * Scans candidate token streams against target professional lexicon bitmasks.
 * Computes jargon density and filler word penalty in parallel.
 *
 * @param token_ids          [batch_size x seq_len] candidate input token IDs
 * @param jargon_token_mask  [vocab_size] boolean/byte mask of approved professional jargon
 * @param filler_token_mask  [vocab_size] boolean/byte mask of disfluent filler tokens
 * @param out_jargon_density [batch_size] output jargon density in [0, 1]
 * @param out_filler_penalty [batch_size] output filler penalty in [0, 1]
 * @param seq_len            Sequence length per candidate response
 */
__global__ void parallel_jargon_density_kernel(
    const int* __restrict__ token_ids,
    const unsigned char* __restrict__ jargon_token_mask,
    const unsigned char* __restrict__ filler_token_mask,
    float* __restrict__ out_jargon_density,
    float* __restrict__ out_filler_penalty,
    int seq_len
) {
    int batch_idx = blockIdx.x;
    int tid = threadIdx.x;
    int stride = blockDim.x;

    const int* tokens = token_ids + (batch_idx * seq_len);

    int local_jargon_count = 0;
    int local_filler_count = 0;
    int valid_token_count = 0;

    for (int i = tid; i < seq_len; i += stride) {
        int tok = tokens[i];
        if (tok > 0) { // Non-padding token
            valid_token_count++;
            if (jargon_token_mask[tok] != 0) {
                local_jargon_count++;
            }
            if (filler_token_mask[tok] != 0) {
                local_filler_count++;
            }
        }
    }

    // Warp-level reduction
    local_jargon_count = (int)warp_reduce_sum((float)local_jargon_count);
    local_filler_count = (int)warp_reduce_sum((float)local_filler_count);
    valid_token_count  = (int)warp_reduce_sum((float)valid_token_count);

    __shared__ int s_jargon[WARP_SIZE];
    __shared__ int s_filler[WARP_SIZE];
    __shared__ int s_valid[WARP_SIZE];

    int lane = tid % WARP_SIZE;
    int warp_id = tid / WARP_SIZE;

    if (lane == 0) {
        s_jargon[warp_id] = local_jargon_count;
        s_filler[warp_id] = local_filler_count;
        s_valid[warp_id]  = valid_token_count;
    }
    __syncthreads();

    if (warp_id == 0) {
        int num_warps = blockDim.x / WARP_SIZE;
        float total_j = (lane < num_warps) ? (float)s_jargon[lane] : 0.0f;
        float total_f = (lane < num_warps) ? (float)s_filler[lane] : 0.0f;
        float total_v = (lane < num_warps) ? (float)s_valid[lane]  : 0.0f;

        total_j = warp_reduce_sum(total_j);
        total_f = warp_reduce_sum(total_f);
        total_v = warp_reduce_sum(total_v);

        if (lane == 0) {
            float v = fmaxf(1.0f, total_v);
            out_jargon_density[batch_idx] = fminf(1.0f, (total_j / v) * 4.0f);
            out_filler_penalty[batch_idx] = fminf(0.50f, (total_f / v) * 6.0f);
        }
    }
}

/**
 * Kernel 2: vocal_jitter_shimmer_kernel
 *
 * Computes acoustic cycle-to-cycle F0 perturbation (jitter) and amplitude perturbation (shimmer).
 * Elevated jitter/shimmer indicates candidate nervous tension or loss of vocal composure.
 *
 * @param pitch_periods      [batch_size x num_cycles] consecutive pitch period lengths (seconds)
 * @param amplitudes         [batch_size x num_cycles] peak cycle amplitudes
 * @param out_jitter_percent [batch_size] Relative Jitter (RAP/Jitta %)
 * @param out_shimmer_db     [batch_size] Relative Shimmer (dB)
 * @param num_cycles         Number of detected glottal cycles
 */
__global__ void vocal_jitter_shimmer_kernel(
    const float* __restrict__ pitch_periods,
    const float* __restrict__ amplitudes,
    float* __restrict__ out_jitter_percent,
    float* __restrict__ out_shimmer_db,
    int num_cycles
) {
    int batch_idx = blockIdx.x;
    int tid = threadIdx.x;
    int stride = blockDim.x;

    if (num_cycles < 2) {
        if (tid == 0) {
            out_jitter_percent[batch_idx] = 0.5f;
            out_shimmer_db[batch_idx] = 0.5f;
        }
        return;
    }

    const float* p_vec = pitch_periods + (batch_idx * num_cycles);
    const float* a_vec = amplitudes + (batch_idx * num_cycles);

    float sum_p_diff = 0.0f;
    float sum_p = 0.0f;
    float sum_a_diff = 0.0f;
    float sum_a = 0.0f;

    for (int i = tid; i < num_cycles - 1; i += stride) {
        float p_curr = p_vec[i];
        float p_next = p_vec[i + 1];
        float a_curr = a_vec[i];
        float a_next = a_vec[i + 1];

        sum_p_diff += fabsf(p_curr - p_next);
        sum_p += p_curr;

        sum_a_diff += fabsf(a_curr - a_next);
        sum_a += a_curr;
    }

    sum_p_diff = warp_reduce_sum(sum_p_diff);
    sum_p      = warp_reduce_sum(sum_p);
    sum_a_diff = warp_reduce_sum(sum_a_diff);
    sum_a      = warp_reduce_sum(sum_a);

    __shared__ float s_pd[WARP_SIZE];
    __shared__ float s_p[WARP_SIZE];
    __shared__ float s_ad[WARP_SIZE];
    __shared__ float s_a[WARP_SIZE];

    int lane = tid % WARP_SIZE;
    int warp_id = tid / WARP_SIZE;

    if (lane == 0) {
        s_pd[warp_id] = sum_p_diff;
        s_p[warp_id]  = sum_p;
        s_ad[warp_id] = sum_a_diff;
        s_a[warp_id]  = sum_a;
    }
    __syncthreads();

    if (warp_id == 0) {
        int num_warps = blockDim.x / WARP_SIZE;
        float final_pd = (lane < num_warps) ? s_pd[lane] : 0.0f;
        float final_p  = (lane < num_warps) ? s_p[lane]  : 0.0f;
        float final_ad = (lane < num_warps) ? s_ad[lane] : 0.0f;
        float final_a  = (lane < num_warps) ? s_a[lane]  : 0.0f;

        final_pd = warp_reduce_sum(final_pd);
        final_p  = warp_reduce_sum(final_p);
        final_ad = warp_reduce_sum(final_ad);
        final_a  = warp_reduce_sum(final_a);

        if (lane == 0) {
            float mean_p = fmaxf(1e-6f, final_p / (float)(num_cycles - 1));
            float mean_a = fmaxf(1e-6f, final_a / (float)(num_cycles - 1));

            // Jitter % = (Sum(|T_i - T_{i+1}|) / (N - 1)) / Mean(T) * 100
            out_jitter_percent[batch_idx] = (final_pd / (float)(num_cycles - 1)) / mean_p * 100.0f;

            // Shimmer dB = 20 * log10(Sum(|A_i - A_{i+1}|) / Mean(A) + 1.0)
            out_shimmer_db[batch_idx] = 20.0f * log10f((final_ad / mean_a) + 1.0f);
        }
    }
}
