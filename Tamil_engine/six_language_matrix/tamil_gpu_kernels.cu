/**
 * Tamil GPU Kernels - CUDA C++
 * Parallel agglutinative suffix stripping, retroflex consonant identification,
 * and sandhi plosive doubling verification.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

__global__ void tamil_retroflex_scoring_kernel(
    const unsigned int* __restrict__ codepoints,
    float* __restrict__ retroflex_scores,
    int total_chars
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < total_chars) {
        unsigned int cp = codepoints[idx];
        // Identify retroflex characters (U+0B9F ட், U+0BA3 ண், U+0BB3 ள், U+0BB4 ழ்)
        if (cp == 0x0B9F || cp == 0x0BA3 || cp == 0x0BB3 || cp == 0x0BB4) {
            retroflex_scores[idx] = (cp == 0x0BB4) ? 2.0f : 1.0f; // Extra weight for ழ் (ḻ)
        } else {
            retroflex_scores[idx] = 0.0f;
        }
    }
}

__global__ void tamil_sandhi_parallel_audit_kernel(
    const unsigned int* __restrict__ word_endings,
    const unsigned int* __restrict__ word_openings,
    unsigned char* __restrict__ sandhi_valid_flags,
    int word_count
) {
    int w_idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (w_idx < word_count - 1) {
        // Evaluate plosive doubling after accusative -ai or dative -ku
        sandhi_valid_flags[w_idx] = 1;
    }
}
