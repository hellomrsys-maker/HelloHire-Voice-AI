/**
 * written_grammar_kernels.cu - Engine A Sub-Core A4 (CUDA)
 * Written Grammar & Discourse Engine: Parallel GPU batch sentence embeddings,
 * clausal attention reductions, and syntax tree parallelism.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

__global__ void batch_syntax_attention_kernel(
    const float* __restrict__ query,
    const float* __restrict__ key,
    const float* __restrict__ value,
    float* __restrict__ output,
    int batch_size,
    int seq_len,
    int d_model
) {
    int b = blockIdx.z;
    int i = blockIdx.y * blockDim.y + threadIdx.y; // query position
    int d = blockIdx.x * blockDim.x + threadIdx.x; // feature dimension

    if (b >= batch_size || i >= seq_len || d >= d_model) return;

    float acc = 0.0f;
    float scale = 1.0f / sqrtf((float)d_model);

    // Compute scaled dot-product attention
    for (int j = 0; j < seq_len; ++j) {
        float score = 0.0f;
        for (int k = 0; k < d_model; ++k) {
            score += query[b * seq_len * d_model + i * d_model + k] *
                     key[b * seq_len * d_model + j * d_model + k];
        }
        score *= scale;
        float weight = __expf(fminf(score, 10.0f)); // Numerically stable soft clamp

        acc += weight * value[b * seq_len * d_model + j * d_model + d];
    }

    output[b * seq_len * d_model + i * d_model + d] = acc;
}

extern "C" void launch_batch_syntax_attention(
    const float* d_query,
    const float* d_key,
    const float* d_value,
    float* d_output,
    int batch_size,
    int seq_len,
    int d_model,
    cudaStream_t stream
) {
    dim3 block(16, 16);
    dim3 grid(
        (d_model + block.x - 1) / block.x,
        (seq_len + block.y - 1) / block.y,
        batch_size
    );

    batch_syntax_attention_kernel<<<grid, block, 0, stream>>>(
        d_query, d_key, d_value, d_output, batch_size, seq_len, d_model
    );
}
