/**
 * @file rvce_kernels.cu
 * @brief CUDA Kernels for Recruitment Verbal Cognitive Engine (RVCE).
 *
 * Implements high-throughput parallel candidate evaluation:
 * 1. parallel_candidate_competency_scoring: Batched cosine similarity against benchmark vectors.
 * 2. cognitive_trait_fusion_warp_kernel: Fast warp-level aggregation of 6 cognitive faculties.
 * 3. cognitive_snr_perturbation_kernel: Parallel speech perturbation and SNR tracking.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32

__device__ inline float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

/**
 * Kernel 1: parallel_candidate_competency_scoring
 * Computes cosine similarity between candidate semantic embedding and 6 recruitment rubrics:
 * [0: Thinking, 1: Concentration, 2: Recall, 3: Creativity, 4: Imagination, 5: Verbal]
 */
__global__ void parallel_candidate_competency_scoring(
    const float* __restrict__ candidate_embeddings, // [batch_size x dim]
    const float* __restrict__ benchmark_rubrics,     // [6 x dim]
    float* __restrict__ out_scores,                 // [batch_size x 6]
    int dim
) {
    int batch_idx = blockIdx.x;
    int rubric_idx = blockIdx.y; // 0 to 5
    int tid = threadIdx.x;
    int stride = blockDim.x;

    const float* cand = candidate_embeddings + (batch_idx * dim);
    const float* rubr = benchmark_rubrics + (rubric_idx * dim);

    float dot = 0.0f;
    float norm_cand = 0.0f;
    float norm_rubr = 0.0f;

    for (int i = tid; i < dim; i += stride) {
        float c = cand[i];
        float r = rubr[i];
        dot += c * r;
        norm_cand += c * c;
        norm_rubr += r * r;
    }

    dot = warp_reduce_sum(dot);
    norm_cand = warp_reduce_sum(norm_cand);
    norm_rubr = warp_reduce_sum(norm_rubr);

    if (tid == 0) {
        float denom = sqrtf(norm_cand) * sqrtf(norm_rubr);
        float sim = (denom > 1e-6f) ? (dot / denom) : 0.0f;
        // Clamp to [0, 1] range
        sim = fmaxf(0.0f, fminf(1.0f, (sim + 1.0f) * 0.5f));
        out_scores[batch_idx * 6 + rubric_idx] = sim;
    }
}

/**
 * Kernel 2: cognitive_trait_fusion_warp_kernel
 * Fuses the 6 cognitive metrics into a composite hireability score and recommendation code:
 * Weights: [0.22 Think, 0.15 Focus, 0.18 Recall, 0.15 Creat, 0.15 Imagi, 0.15 Verbal]
 */
__global__ void cognitive_trait_fusion_warp_kernel(
    const float* __restrict__ scores, // [batch_size x 6]
    float* __restrict__ out_composite, // [batch_size]
    int* __restrict__ out_recommendation, // [batch_size] (1=Strong, 2=Hire, 3=Lean, 4=No)
    int batch_size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= batch_size) return;

    const float* s = scores + (idx * 6);
    float think = s[0];
    float focus = s[1];
    float recall = s[2];
    float creat = s[3];
    float imagi = s[4];
    float verbal = s[5];

    float composite = (think * 0.22f) +
                      (focus * 0.15f) +
                      (recall * 0.18f) +
                      (creat * 0.15f) +
                      (imagi * 0.15f) +
                      (verbal * 0.15f);

    composite = fmaxf(0.0f, fminf(1.0f, composite));
    out_composite[idx] = composite;

    int rec = 4;
    if (composite >= 0.82f) {
        rec = 1; // Strong Hire
    } else if (composite >= 0.68f) {
        rec = 2; // Hire
    } else if (composite >= 0.52f) {
        rec = 3; // Leaning Hire
    }
    out_recommendation[idx] = rec;
}
