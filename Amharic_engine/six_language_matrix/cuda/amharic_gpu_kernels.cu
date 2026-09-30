// Amharic GPU Accelerated Kernels (CUDA)
// Parallel multi-head attention scores and phonemic acoustic distance matrices.

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cstdint>

namespace amharic_engine {
namespace cuda {

// Q,K: [Batch,Heads,SeqLen,D_k] -> Scores: [Batch,Heads,SeqLen,SeqLen]
__global__ void AttentionScoresKernel(
    const float* __restrict__ Q, const float* __restrict__ K,
    float* __restrict__ Scores, int seq_len, int d_k, float scale) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int batch_head = blockIdx.z;
    if (row < seq_len && col < seq_len) {
        int q_off = batch_head * (seq_len * d_k) + row * d_k;
        int k_off = batch_head * (seq_len * d_k) + col * d_k;
        float dot = 0.0f;
        for (int i = 0; i < d_k; ++i) dot += Q[q_off + i] * K[k_off + i];
        Scores[batch_head * (seq_len * seq_len) + row * seq_len + col] = dot * scale;
    }
}

__global__ void PhonemeAcousticDistanceKernel(
    const float* __restrict__ a, const float* __restrict__ b,
    float* __restrict__ out_distance, int num_phonemes, int feature_dim) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < num_phonemes) {
        float sum_sq = 0.0f;
        int off = tid * feature_dim;
        for (int i = 0; i < feature_dim; ++i) {
            float diff = a[off + i] - b[off + i];
            sum_sq += diff * diff;
        }
        out_distance[tid] = sqrtf(sum_sq);
    }
}

} // namespace cuda
} // namespace amharic_engine
