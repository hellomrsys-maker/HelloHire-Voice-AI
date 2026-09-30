/**
 * verbal_keyword_kernels.cu - Engine B Sub-Core B4 (CUDA)
 * Spoken & Verbal Communication Engine: Warp-level parallel keyword spotter
 * and phonetic distance matrix reductions.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

__global__ void warp_keyword_spotter_kernel(
    const int* __restrict__ phoneme_stream,
    const int* __restrict__ target_patterns,
    float* __restrict__ match_scores,
    int stream_length,
    int num_patterns,
    int pattern_length
) {
    int pid = blockIdx.y; // pattern index
    int pos = blockIdx.x * blockDim.x + threadIdx.x; // stream position

    if (pid >= num_patterns || pos + pattern_length > stream_length) return;

    int matches = 0;
    for (int k = 0; k < pattern_length; ++k) {
        if (phoneme_stream[pos + k] == target_patterns[pid * pattern_length + k]) {
            matches++;
        }
    }

    float score = (float)matches / (float)pattern_length;
    // Atomic maximum score update for this pattern
    atomicMax((int*)&match_scores[pid], __float_as_int(score));
}

extern "C" void launch_warp_keyword_spotter(
    const int* d_stream,
    const int* d_patterns,
    float* d_scores,
    int stream_length,
    int num_patterns,
    int pattern_length,
    cudaStream_t stream
) {
    dim3 block(128);
    dim3 grid(
        (stream_length + block.x - 1) / block.x,
        num_patterns
    );

    warp_keyword_spotter_kernel<<<grid, block, 0, stream>>>(
        d_stream, d_patterns, d_scores, stream_length, num_patterns, pattern_length
    );
}
