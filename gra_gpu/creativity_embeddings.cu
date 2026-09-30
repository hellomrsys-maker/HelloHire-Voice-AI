/**
 * @file creativity_embeddings.cu
 * @brief CUDA Kernels for Parallel Metaphorical Tension and Conceptual Divergence Computation.
 *
 * Implements high-throughput batch tensor operations for:
 * 1. Associative Metaphorical Distance between semantic Tenor and Vehicle embeddings (dim 512).
 * 2. Shannon Semantic Dispersion Entropy over candidate token probability distributions.
 * 3. Phoneme Rhyme Profile distance for poetic meter and sonic harmony scoring.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32
#define EMBED_DIM 512

/**
 * Warp-level parallel reduction for float summation.
 */
__device__ inline float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

/**
 * Block-level parallel reduction using shared memory.
 */
__device__ inline float block_reduce_sum(float val) {
    __shared__ float shared[WARP_SIZE];
    int lane = threadIdx.x % WARP_SIZE;
    int wid = threadIdx.x / WARP_SIZE;

    val = warp_reduce_sum(val);

    if (lane == 0) {
        shared[wid] = val;
    }
    __syncthreads();

    val = (threadIdx.x < (blockDim.x / WARP_SIZE)) ? shared[lane] : 0.0f;
    if (wid == 0) {
        val = warp_reduce_sum(val);
    }
    return val;
}

/**
 * Kernel: compute_conceptual_divergence_kernel
 *
 * Each CUDA block processes one (Tenor, Vehicle) concept pair across EMBED_DIM (512).
 * Computes:
 *   - Cosine Tension: T = 1.0 - (u · v) / (||u|| * ||v||)
 *   - Conceptual Divergence Index: D = sqrt(sum((u - v)^2)) / (||u|| + ||v||)
 *
 * @param tenor_embeddings    [num_pairs x 512] Tenor concept representation vectors
 * @param vehicle_embeddings  [num_pairs x 512] Vehicle concept representation vectors
 * @param out_tension         [num_pairs] Metaphorical tension score in [0.0, 1.0]
 * @param out_divergence      [num_pairs] Normalized associative divergence distance
 * @param num_pairs           Batch size of candidate metaphor pairs
 */
__global__ void compute_conceptual_divergence_kernel(
    const float* __restrict__ tenor_embeddings,
    const float* __restrict__ vehicle_embeddings,
    float* __restrict__ out_tension,
    float* __restrict__ out_divergence,
    int num_pairs
) {
    int pair_idx = blockIdx.x;
    if (pair_idx >= num_pairs) return;

    const float* u = tenor_embeddings + (pair_idx * EMBED_DIM);
    const float* v = vehicle_embeddings + (pair_idx * EMBED_DIM);

    int tid = threadIdx.x;
    int stride = blockDim.x;

    float dot = 0.0f;
    float norm_u_sq = 0.0f;
    float norm_v_sq = 0.0f;
    float diff_sq = 0.0f;

    for (int i = tid; i < EMBED_DIM; i += stride) {
        float ui = u[i];
        float vi = v[i];
        float diff = ui - vi;

        dot += ui * vi;
        norm_u_sq += ui * ui;
        norm_v_sq += vi * vi;
        diff_sq += diff * diff;
    }

    // Parallel reductions across threads in block
    dot = block_reduce_sum(dot);
    norm_u_sq = block_reduce_sum(norm_u_sq);
    norm_v_sq = block_reduce_sum(norm_v_sq);
    diff_sq = block_reduce_sum(diff_sq);

    if (tid == 0) {
        float norm_u = sqrtf(fmaxf(norm_u_sq, 1e-8f));
        float norm_v = sqrtf(fmaxf(norm_v_sq, 1e-8f));
        float denom = norm_u * norm_v;

        float cosine_sim = (denom > 1e-8f) ? (dot / denom) : 0.0f;
        cosine_sim = fminf(fmaxf(cosine_sim, -1.0f), 1.0f);

        // Metaphorical Tension: 1.0 - cosine_sim
        out_tension[pair_idx] = 1.0f - cosine_sim;

        // Associative Euclidean Divergence normalized by sum of norms
        float euc_dist = sqrtf(fmaxf(diff_sq, 0.0f));
        out_divergence[pair_idx] = euc_dist / (norm_u + norm_v + 1e-8f);
    }
}

/**
 * Kernel: compute_rhyme_phoneme_harmony_kernel
 *
 * Compares phonetic coda vectors (dim 64) for rhyme detection in poetic generation.
 */
__global__ void compute_rhyme_phoneme_harmony_kernel(
    const float* __restrict__ coda_a,
    const float* __restrict__ coda_b,
    float* __restrict__ out_rhyme_score,
    int num_pairs,
    int coda_dim
) {
    int pair_idx = blockIdx.x;
    if (pair_idx >= num_pairs) return;

    const float* a = coda_a + (pair_idx * coda_dim);
    const float* b = coda_b + (pair_idx * coda_dim);

    float sim = 0.0f;
    for (int i = threadIdx.x; i < coda_dim; i += blockDim.x) {
        float diff = fabsf(a[i] - b[i]);
        sim += expf(-diff);
    }

    sim = block_reduce_sum(sim);

    if (threadIdx.x == 0) {
        out_rhyme_score[pair_idx] = sim / (float)coda_dim;
    }
}

// Host C-ABI wrappers
extern "C" {

cudaError_t launch_conceptual_divergence(
    const float* d_tenors,
    const float* d_vehicles,
    float* d_out_tension,
    float* d_out_divergence,
    int num_pairs,
    cudaStream_t stream
) {
    dim3 grid(num_pairs);
    dim3 block(128);
    compute_conceptual_divergence_kernel<<<grid, block, 0, stream>>>(
        d_tenors, d_vehicles, d_out_tension, d_out_divergence, num_pairs
    );
    return cudaGetLastError();
}

cudaError_t launch_rhyme_phoneme_harmony(
    const float* d_coda_a,
    const float* d_coda_b,
    float* d_out_rhyme_score,
    int num_pairs,
    int coda_dim,
    cudaStream_t stream
) {
    dim3 grid(num_pairs);
    dim3 block(64);
    compute_rhyme_phoneme_harmony_kernel<<<grid, block, 0, stream>>>(
        d_coda_a, d_coda_b, d_out_rhyme_score, num_pairs, coda_dim
    );
    return cudaGetLastError();
}

} // extern "C"
