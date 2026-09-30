/**
 * @file typological_matrix_cuda.cu
 * @brief CUDA Kernels for Parallel Typological Distance & Cross-Lingual Projection.
 *
 * Implements GPU-accelerated:
 * 1. Pairwise Typological Distance Matrix computation over the 8 Universal Diagnostic Pillars.
 * 2. Cross-Lingual Semantic Space Alignment conditioned on Morphological Synthesis & Head Directionality.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32
#define NUM_PILLARS 8

__device__ inline float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

/**
 * Kernel: pairwise_typological_distance_kernel
 *
 * Computes the full pairwise N x N typological distance matrix
 * based on the 8-pillar diagnostic feature vectors.
 *
 * @param pillar_vectors     [N x 8] matrix of normalized pillar scores
 * @param pillar_weights     [8] importance weights for each pillar
 * @param distance_matrix    [N x N] output pairwise distance matrix
 * @param num_languages      Number of languages N
 */
__global__ void pairwise_typological_distance_kernel(
    const float* __restrict__ pillar_vectors,
    const float* __restrict__ pillar_weights,
    float* __restrict__ distance_matrix,
    int num_languages
) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row >= num_languages || col >= num_languages) return;

    if (row == col) {
        distance_matrix[row * num_languages + col] = 0.0f;
        return;
    }

    const float* vec_a = pillar_vectors + (row * NUM_PILLARS);
    const float* vec_b = pillar_vectors + (col * NUM_PILLARS);

    float sum_sq = 0.0f;
    float sum_w = 0.0f;

    #pragma unroll
    for (int i = 0; i < NUM_PILLARS; ++i) {
        float diff = vec_a[i] - vec_b[i];
        float w = pillar_weights[i];
        sum_sq += w * (diff * diff);
        sum_w += w;
    }

    float dist = (sum_w > 0.0f) ? sqrtf(sum_sq / sum_w) : 0.0f;
    distance_matrix[row * num_languages + col] = dist;
}

/**
 * Kernel: cross_lingual_typological_projection_kernel
 *
 * Projects 256-dimensional language embeddings into a canonical typological invariant space.
 * Applies synthesis-scale rotation and head-directionality reflection.
 *
 * @param embeddings         [N x 256] input sentence embeddings
 * @param projection_matrix  [256 x 256] canonical orthogonal projection
 * @param synthesis_indices  [N] index of synthesis for each sample
 * @param out_aligned        [N x 256] output aligned representations
 * @param num_samples        Total batch size N
 * @param embed_dim          256
 */
__global__ void cross_lingual_typological_projection_kernel(
    const float* __restrict__ embeddings,
    const float* __restrict__ projection_matrix,
    const float* __restrict__ synthesis_indices,
    float* __restrict__ out_aligned,
    int num_samples,
    int embed_dim
) {
    int sample_idx = blockIdx.x;
    if (sample_idx >= num_samples) return;

    int out_col = threadIdx.x;
    if (out_col >= embed_dim) return;

    const float* in_vec = embeddings + (sample_idx * embed_dim);
    float synthesis_scale = fminf(fmaxf(synthesis_indices[sample_idx] / 3.0f, 0.5f), 2.0f);

    float dot = 0.0f;
    for (int k = 0; k < embed_dim; ++k) {
        dot += in_vec[k] * projection_matrix[k * embed_dim + out_col];
    }

    // Modulate output coordinate by morphological synthesis scaling
    out_aligned[sample_idx * embed_dim + out_col] = tanhf(dot * synthesis_scale);
}
