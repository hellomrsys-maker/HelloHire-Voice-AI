/**
 * phonology_fft_kernels.cu - Engine C Sub-Core C4 (CUDA)
 * Auditory & Phonological Voice Engine: GPU parallel Fast Fourier Transform (FFT)
 * and mel-spectrogram feature reduction.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

__global__ void mel_spectrogram_reduction_kernel(
    const float* __restrict__ fft_magnitudes,
    const float* __restrict__ mel_filterbank,
    float* __restrict__ mel_energies,
    int num_frames,
    int num_fft_bins,
    int num_mel_bins
) {
    int frame_idx = blockIdx.y;
    int mel_idx = blockIdx.x * blockDim.x + threadIdx.x;

    if (frame_idx >= num_frames || mel_idx >= num_mel_bins) return;

    float energy = 0.0f;
    for (int bin = 0; bin < num_fft_bins; ++bin) {
        float mag = fft_magnitudes[frame_idx * num_fft_bins + bin];
        float weight = mel_filterbank[mel_idx * num_fft_bins + bin];
        energy += mag * weight;
    }

    // Log-mel compression
    mel_energies[frame_idx * num_mel_bins + mel_idx] = logf(fmaxf(energy, 1e-6f));
}

extern "C" void launch_mel_spectrogram_reduction(
    const float* d_fft_magnitudes,
    const float* d_filterbank,
    float* d_mel_energies,
    int num_frames,
    int num_fft_bins,
    int num_mel_bins,
    cudaStream_t stream
) {
    dim3 block(64);
    dim3 grid(
        (num_mel_bins + block.x - 1) / block.x,
        num_frames
    );

    mel_spectrogram_reduction_kernel<<<grid, block, 0, stream>>>(
        d_fft_magnitudes, d_filterbank, d_mel_energies, num_frames, num_fft_bins, num_mel_bins
    );
}
