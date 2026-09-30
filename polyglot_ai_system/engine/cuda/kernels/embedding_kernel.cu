// =============================================================================
// engine/cuda/kernels/embedding_kernel.cu
// GPU embedding lookup, scatter/gather, and embedding arithmetic kernels
// =============================================================================

#include <cuda_runtime.h>

/**
 * @brief Embedding lookup kernel.
 *
 * For each token ID in `ids`, retrieves the corresponding row from
 * the embedding table and writes it to `output`.
 *
 * Grid: (seq_len,)
 * Block: (embed_dim,) — capped at 1024
 */
extern "C" __global__ void embedding_lookup_kernel(
    const int*   __restrict__ ids,         // [seq_len] token IDs
    const float* __restrict__ table,       // [vocab_size, embed_dim]
    float*       __restrict__ output,      // [seq_len, embed_dim]
    const int    seq_len,
    const int    vocab_size,
    const int    embed_dim
)
{
    const int seq_pos = blockIdx.x;
    const int dim_idx = threadIdx.x;

    if (seq_pos >= seq_len || dim_idx >= embed_dim) return;

    const int token_id = ids[seq_pos];

    // Bounds check
    if (token_id < 0 || token_id >= vocab_size) {
        output[seq_pos * embed_dim + dim_idx] = 0.0f;
        return;
    }

    output[seq_pos * embed_dim + dim_idx] =
        table[(long)token_id * embed_dim + dim_idx];
}

/**
 * @brief Batched embedding lookup.
 *
 * Grid: (batch_size, seq_len)
 * Block: (embed_dim,)
 */
extern "C" __global__ void batched_embedding_lookup_kernel(
    const int*   __restrict__ ids,         // [batch_size, seq_len]
    const float* __restrict__ table,       // [vocab_size, embed_dim]
    float*       __restrict__ output,      // [batch_size, seq_len, embed_dim]
    const int    batch_size,
    const int    seq_len,
    const int    vocab_size,
    const int    embed_dim
)
{
    const int batch  = blockIdx.x;
    const int pos    = blockIdx.y;
    const int dim_idx = threadIdx.x;

    if (batch >= batch_size || pos >= seq_len || dim_idx >= embed_dim) return;

    const int token_id = ids[batch * seq_len + pos];
    const int out_base = (batch * seq_len + pos) * embed_dim;

    if (token_id < 0 || token_id >= vocab_size) {
        output[out_base + dim_idx] = 0.0f;
        return;
    }

    output[out_base + dim_idx] = table[(long)token_id * embed_dim + dim_idx];
}

/**
 * @brief Embedding gradient scatter kernel (for backward pass).
 * Accumulates gradients from `grad_output` into the embedding table
 * at the positions specified by `ids`.
 *
 * Uses atomic adds to handle repeated indices correctly.
 *
 * Grid: (seq_len,)
 * Block: (embed_dim,)
 */
extern "C" __global__ void embedding_backward_kernel(
    const int*   __restrict__ ids,         // [seq_len]
    const float* __restrict__ grad_output, // [seq_len, embed_dim]
    float*       __restrict__ grad_table,  // [vocab_size, embed_dim]
    const int    seq_len,
    const int    embed_dim
)
{
    const int seq_pos = blockIdx.x;
    const int dim_idx = threadIdx.x;

    if (seq_pos >= seq_len || dim_idx >= embed_dim) return;

    const int token_id = ids[seq_pos];
    if (token_id < 0) return;

    atomicAdd(
        &grad_table[(long)token_id * embed_dim + dim_idx],
        grad_output[seq_pos * embed_dim + dim_idx]
    );
}

/**
 * @brief Element-wise embedding addition (for residual connections).
 * output[i] = a[i] + b[i] for all i.
 *
 * Grid: (total_elements / 1024,)
 * Block: (1024,)
 */
extern "C" __global__ void embedding_add_kernel(
    const float* __restrict__ a,
    const float* __restrict__ b,
    float*       __restrict__ output,
    const int    total_elements
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < total_elements) {
        output[idx] = a[idx] + b[idx];
    }
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_embedding_lookup(
    const int* ids, const float* table, float* output,
    int seq_len, int vocab_size, int embed_dim,
    cudaStream_t stream)
{
    const int block_size = min(embed_dim, 1024);
    embedding_lookup_kernel<<<seq_len, block_size, 0, stream>>>(
        ids, table, output, seq_len, vocab_size, embed_dim);
    return cudaGetLastError();
}

cudaError_t launch_embedding_backward(
    const int* ids, const float* grad_output, float* grad_table,
    int seq_len, int embed_dim,
    cudaStream_t stream)
{
    const int block_size = min(embed_dim, 1024);
    embedding_backward_kernel<<<seq_len, block_size, 0, stream>>>(
        ids, grad_output, grad_table, seq_len, embed_dim);
    return cudaGetLastError();
}

cudaError_t launch_embedding_add(
    const float* a, const float* b, float* output,
    int total_elements,
    cudaStream_t stream)
{
    const int block_size = 1024;
    const int grid_size  = (total_elements + block_size - 1) / block_size;
    embedding_add_kernel<<<grid_size, block_size, 0, stream>>>(
        a, b, output, total_elements);
    return cudaGetLastError();
}

} // extern "C"
