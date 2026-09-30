// Bengali GPU Kernels (CUDA)
// Parallel batch processing for classifier concordance and Sadhu/Cholito register classification.

#include <cuda_runtime.h>
#include <cstdint>

extern "C" {

// GPU Kernel: Parallel classifier detection across N tokens
__global__ void bengali_batch_classifier_kernel(
    const uint32_t* d_token_hashes,
    const uint32_t* d_classifier_hashes,
    int num_classifiers,
    int num_tokens,
    uint8_t* d_match_flags
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= num_tokens) return;

    uint32_t token_hash = d_token_hashes[idx];
    uint8_t matched = 0;

    for (int c = 0; c < num_classifiers; ++c) {
        if (token_hash == d_classifier_hashes[c]) {
            matched = 1;
            break;
        }
    }

    d_match_flags[idx] = matched;
}

// GPU Kernel: Batch 64-byte AMSV state projection
__global__ void bengali_amsv_parallel_sync_kernel(
    const float* d_syntax_scores,
    const float* d_register_scores,
    int batch_size,
    uint8_t* d_amsv_buffer_64b
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= batch_size) return;

    // Offset in bytes for this batch element
    int base_offset = idx * 64;

    // Byte 18: Capability 1 (Syntax)
    float syn = d_syntax_scores[idx];
    d_amsv_buffer_64b[base_offset + 18] = (uint8_t)(syn * 255.0f);

    // Byte 22: Capability 3 (Pragmatics)
    float reg = d_register_scores[idx];
    d_amsv_buffer_64b[base_offset + 22] = (uint8_t)(reg * 255.0f);

    // Byte 52: Global Structural Score (float)
    float* structural_ptr = (float*)&d_amsv_buffer_64b[base_offset + 52];
    *structural_ptr = syn;

    // Byte 54: Global Register Score (float)
    float* register_ptr = (float*)&d_amsv_buffer_64b[base_offset + 54];
    *register_ptr = reg;
}

} // extern "C"
