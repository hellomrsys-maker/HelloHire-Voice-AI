/**
 * telugu_gpu_kernels.cu - GPU Massively Parallel Kernels for Telugu Acoustic Processing.
 * Detects retroflex consonant formant dips and computes vocal jitter/shimmer.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

__global__ void telugu_retroflex_dip_kernel(
    const float* __restrict__ f3_formants,
    const float* __restrict__ f2_formants,
    float* __restrict__ retroflex_scores,
    int frame_count
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < frame_count) {
        float f3 = f3_formants[idx];
        float f2 = f2_formants[idx];
        // Retroflex consonants (ట, డ, ణ) induce characteristic F3 convergence toward F2
        float delta = f3 - f2;
        float score = 0.0f;
        if (delta > 0.0f && delta < 600.0f) {
            score = (600.0f - delta) / 600.0f;
        }
        retroflex_scores[idx] = score;
    }
}

__global__ void telugu_jitter_shimmer_kernel(
    const float* __restrict__ pitch_periods,
    const float* __restrict__ peak_amplitudes,
    float* __restrict__ jitter_out,
    float* __restrict__ shimmer_out,
    int cycle_count
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx > 0 && idx < cycle_count) {
        float t_curr = pitch_periods[idx];
        float t_prev = pitch_periods[idx - 1];
        float a_curr = peak_amplitudes[idx];
        float a_prev = peak_amplitudes[idx - 1];

        jitter_out[idx] = fabsf(t_curr - t_prev) / (t_prev > 1e-4f ? t_prev : 1.0f);
        shimmer_out[idx] = fabsf(a_curr - a_prev) / (a_prev > 1e-4f ? a_prev : 1.0f);
    }
}
