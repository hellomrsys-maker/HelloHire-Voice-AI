// Mandarin GPU CUDA Kernels
// High-throughput parallel Mandarin Aspect collocation and Serial Verb Construction attention
#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cstdint>
#include <cmath>

namespace mandarin_cuda {

__global__ void mandarin_aspect_attention_kernel(
    const float* __restrict__ Q,
    const float* __restrict__ K,
    float* __restrict__ AttnScores,
    int batch_size,
    int seq_len,
    int d_model,
    float scale
) {
    int b = blockIdx.z;
    int i = blockIdx.y * blockDim.y + threadIdx.y; // Source character/token
    int j = blockIdx.x * blockDim.x + threadIdx.x; // Target character/token

    if (b < batch_size && i < seq_len && j < seq_len) {
        float dot = 0.0f;
        const float* q_vec = Q + (b * seq_len + i) * d_model;
        const float* k_vec = K + (b * seq_len + j) * d_model;

        for (int d = 0; d < d_model; ++d) {
            dot += q_vec[d] * k_vec[d];
        }

        AttnScores[b * seq_len * seq_len + i * seq_len + j] = dot * scale;
    }
}

extern "C" void launch_mandarin_aspect_attention(
    const float* d_Q,
    const float* d_K,
    float* d_Scores,
    int batch_size,
    int seq_len,
    int d_model,
    cudaStream_t stream
) {
    dim3 block(16, 16);
    dim3 grid(
        (seq_len + block.x - 1) / block.x,
        (seq_len + block.y - 1) / block.y,
        batch_size
    );
    float scale = 1.0f / sqrtf(static_cast<float>(d_model));

    mandarin_aspect_attention_kernel<<<grid, block, 0, stream>>>(
        d_Q, d_K, d_Scores, batch_size, seq_len, d_model, scale
    );
}

} // namespace mandarin_cuda
