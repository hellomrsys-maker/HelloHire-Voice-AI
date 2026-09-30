/**
 * @file scenario_embedding.cu
 * @brief CUDA Kernel for Real-Time Parallel Candidate Utterance vs Scenario Competency Alignment.
 *
 * Computes high-dimensional cosine similarity and projection of 512-dim candidate
 * representation vectors against target competency archetype embeddings.
 * Utilizes warp-level shuffle reductions (__shfl_down_sync) for ultra-low latency execution.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32
#define EMBEDDING_DIM 512

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
 * Kernel: candidate_competency_cosine_similarity
 *
 * Each block computes the cosine similarity between one candidate embedding (dim 512)
 * and one target competency archetype vector (dim 512).
 *
 * @param candidate_embeddings   [num_candidates x 512] candidate vectors
 * @param competency_archetypes  [num_archetypes x 512] reference rubric vectors
 * @param out_similarity_matrix  [num_candidates x num_archetypes] similarity scores
 * @param num_candidates         Number of candidate utterances in batch
 * @param num_archetypes         Number of competency benchmarks (e.g. 8)
 */
__global__ void candidate_competency_cosine_similarity(
    const float* __restrict__ candidate_embeddings,
    const float* __restrict__ competency_archetypes,
    float* __restrict__ out_similarity_matrix,
    int num_candidates,
    int num_archetypes
) {
    int candidate_idx = blockIdx.y;
    int archetype_idx = blockIdx.x;

    if (candidate_idx >= num_candidates || archetype_idx >= num_archetypes) {
        return;
    }

    const float* cand_vec = candidate_embeddings + (candidate_idx * EMBEDDING_DIM);
    const float* arch_vec = competency_archetypes + (archetype_idx * EMBEDDING_DIM);

    int tid = threadIdx.x;
    int stride = blockDim.x;

    float dot_product = 0.0f;
    float norm_cand_sq = 0.0f;
    float norm_arch_sq = 0.0f;

    // Strided accumulation across 512 dimensions
    for (int d = tid; d < EMBEDDING_DIM; d += stride) {
        float c = cand_vec[d];
        float a = arch_vec[d];

        dot_product += c * a;
        norm_cand_sq += c * c;
        norm_arch_sq += a * a;
    }

    // Shared memory for block reduction
    __shared__ float s_dot[WARP_SIZE];
    __shared__ float s_nc[WARP_SIZE];
    __shared__ float s_na[WARP_SIZE];

    int lane = tid % WARP_SIZE;
    int warp_id = tid / WARP_SIZE;

    // Warp-level reduction
    dot_product = warp_reduce_sum(dot_product);
    norm_cand_sq = warp_reduce_sum(norm_cand_sq);
    norm_arch_sq = warp_reduce_sum(norm_arch_sq);

    if (lane == 0) {
        s_dot[warp_id] = dot_product;
        s_nc[warp_id] = norm_cand_sq;
        s_na[warp_id] = norm_arch_sq;
    }
    __syncthreads();

    // Final warp reduction by first warp
    if (warp_id == 0) {
        int num_warps = blockDim.x / WARP_SIZE;
        float final_dot = (lane < num_warps) ? s_dot[lane] : 0.0f;
        float final_nc  = (lane < num_warps) ? s_nc[lane]  : 0.0f;
        float final_na  = (lane < num_warps) ? s_na[lane]  : 0.0f;

        final_dot = warp_reduce_sum(final_dot);
        final_nc  = warp_reduce_sum(final_nc);
        final_na  = warp_reduce_sum(final_na);

        if (lane == 0) {
            float denominator = sqrtf(final_nc) * sqrtf(final_na);
            float cosine_sim = (denominator > 1e-8f) ? (final_dot / denominator) : 0.0f;
            
            // Store result in output matrix
            out_similarity_matrix[candidate_idx * num_archetypes + archetype_idx] = cosine_sim;
        }
    }
}

extern "C" {

/**
 * Host wrapper to launch candidate_competency_cosine_similarity kernel.
 */
cudaError_t launch_competency_similarity(
    const float* d_candidate_embeddings,
    const float* d_competency_archetypes,
    float* d_out_similarity_matrix,
    int num_candidates,
    int num_archetypes,
    cudaStream_t stream
) {
    dim3 block(128); // 4 warps per block
    dim3 grid(num_archetypes, num_candidates);

    candidate_competency_cosine_similarity<<<grid, block, 0, stream>>>(
        d_candidate_embeddings,
        d_competency_archetypes,
        d_out_similarity_matrix,
        num_candidates,
        num_archetypes
    );

    return cudaGetLastError();
}

} // extern "C"
