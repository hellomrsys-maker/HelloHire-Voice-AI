/**
 * @file grammar_checklist_cuda.cu
 * @brief CUDA Kernel for Parallel 7-Point Universal Correctness Framework Scoring (Part 10 of Guide).
 *
 * Evaluates candidate sentence token vectors across all 7 dimensions [A..G]:
 *   Dim 0: Structure (clause completeness, non-fragment)
 *   Dim 1: Agreement & Word Forms (concord, case)
 *   Dim 2: Time & Modality (tense consistency)
 *   Dim 3: Meaning Clarity (parallelism, modifier proximity)
 *   Dim 4: Punctuation & Mechanics (sentence boundaries)
 *   Dim 5: Sound & Delivery (phonetic stress timing)
 *   Dim 6: Fit & Register (genre appropriateness)
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>

#define WARP_SIZE 32
#define NUM_CHECKLIST_DIMS 7

__device__ inline float warp_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(0xFFFFFFFF, val, offset);
    }
    return val;
}

/**
 * Kernel: parallel_checklist_scoring_kernel
 *
 * Each block evaluates one candidate sentence embedding (dim 256)
 * against reference grammatical constraint hyperplanes for all 7 dimensions.
 *
 * @param sentence_embeddings     [num_sentences x 256]
 * @param constraint_hyperplanes  [7 x 256]
 * @param out_dimension_scores    [num_sentences x 7]
 * @param out_composite_scores    [num_sentences]
 * @param num_sentences           Batch size
 * @param embed_dim               256
 */
__global__ void parallel_checklist_scoring_kernel(
    const float* __restrict__ sentence_embeddings,
    const float* __restrict__ constraint_hyperplanes,
    float* __restrict__ out_dimension_scores,
    float* __restrict__ out_composite_scores,
    int num_sentences,
    int embed_dim
) {
    int sent_idx = blockIdx.x;
    if (sent_idx >= num_sentences) return;

    const float* sent_vec = sentence_embeddings + (sent_idx * embed_dim);
    int tid = threadIdx.x;

    __shared__ float s_dim_scores[NUM_CHECKLIST_DIMS];

    for (int dim = 0; dim < NUM_CHECKLIST_DIMS; ++dim) {
        const float* plane_vec = constraint_hyperplanes + (dim * embed_dim);

        float dot = 0.0f;
        for (int i = tid; i < embed_dim; i += blockDim.x) {
            dot += sent_vec[i] * plane_vec[i];
        }

        dot = warp_sum(dot);

        if (tid == 0) {
            // Sigmoidal score in [0.0, 1.0] representing compliance
            float score = 1.0f / (1.0f + expf(-dot));
            s_dim_scores[dim] = score;
            out_dimension_scores[sent_idx * NUM_CHECKLIST_DIMS + dim] = score;
        }
        __syncthreads();
    }

    if (tid == 0) {
        float sum = 0.0f;
        for (int d = 0; d < NUM_CHECKLIST_DIMS; ++d) {
            sum += s_dim_scores[d];
        }
        out_composite_scores[sent_idx] = sum / (float)NUM_CHECKLIST_DIMS;
    }
}

extern "C" {

cudaError_t launch_checklist_scoring(
    const float* d_sentences,
    const float* d_hyperplanes,
    float* d_out_dims,
    float* d_out_composite,
    int num_sentences,
    int embed_dim,
    cudaStream_t stream
) {
    dim3 grid(num_sentences);
    dim3 block(128);
    parallel_checklist_scoring_kernel<<<grid, block, 0, stream>>>(
        d_sentences, d_hyperplanes, d_out_dims, d_out_composite, num_sentences, embed_dim
    );
    return cudaGetLastError();
}

} // extern "C"
