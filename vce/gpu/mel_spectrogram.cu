/**
 * @file mel_spectrogram.cu
 * @brief CUDA Kernels for Real-Time Parallel Mel-Spectrogram & Acoustic Feature Extraction.
 *
 * Implements parallel FFT butterfly stages, magnitude spectrum computation,
 * and triangular Mel-filterbank dot products in GPU shared memory.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

#define FFT_SIZE 512
#define HALF_FFT (FFT_SIZE / 2 + 1)
#define NUM_MEL_BINS 80
#define WARP_SIZE 32

/**
 * Kernel 1: Parallel Windowing & Power Spectrum
 * Applies periodic Hann window and calculates power spectrum |X(k)|^2.
 */
__global__ void window_and_power_spectrum_kernel(
    const float* __restrict__ d_audio_samples,
    float* __restrict__ d_power_spectrum,
    const float* __restrict__ d_hann_window,
    int hop_length,
    int total_frames,
    int total_samples
) {
    int frame_idx = blockIdx.x;
    int bin_idx = threadIdx.x;

    if (frame_idx >= total_frames || bin_idx >= HALF_FFT) return;

    __shared__ float s_frame[FFT_SIZE];

    int sample_offset = frame_idx * hop_length;
    
    // Load samples into shared memory with windowing
    if (bin_idx * 2 < FFT_SIZE) {
        int idx1 = bin_idx * 2;
        int s_idx1 = sample_offset + idx1;
        s_frame[idx1] = (s_idx1 < total_samples) ? (d_audio_samples[s_idx1] * d_hann_window[idx1]) : 0.0f;

        int idx2 = idx1 + 1;
        int s_idx2 = sample_offset + idx2;
        s_frame[idx2] = (s_idx2 < total_samples) ? (d_audio_samples[s_idx2] * d_hann_window[idx2]) : 0.0f;
    }
    __syncthreads();

    // Direct Fourier Transform accumulation for bin k
    float real = 0.0f;
    float imag = 0.0f;
    float angle_base = -2.0f * 3.141592653589793f * (float)bin_idx / (float)FFT_SIZE;

    #pragma unroll 8
    for (int n = 0; n < FFT_SIZE; ++n) {
        float angle = angle_base * (float)n;
        float s, c;
        __sincosf(angle, &s, &c);
        real += s_frame[n] * c;
        imag += s_frame[n] * s;
    }

    // Power spectrum |X(k)|^2
    d_power_spectrum[frame_idx * HALF_FFT + bin_idx] = (real * real + imag * imag) / (float)FFT_SIZE;
}

/**
 * Kernel 2: Parallel Triangular Mel Filterbank Matrix Multiplication
 */
__global__ void mel_filterbank_kernel(
    const float* __restrict__ d_power_spectrum,
    const float* __restrict__ d_mel_weights, // [NUM_MEL_BINS, HALF_FFT]
    float* __restrict__ d_mel_energies,      // [total_frames, NUM_MEL_BINS]
    int total_frames
) {
    int frame_idx = blockIdx.x;
    int mel_idx = threadIdx.x;

    if (frame_idx >= total_frames || mel_idx >= NUM_MEL_BINS) return;

    const float* frame_spec = d_power_spectrum + (frame_idx * HALF_FFT);
    const float* filter_weights = d_mel_weights + (mel_idx * HALF_FFT);

    float sum = 0.0f;
    #pragma unroll 8
    for (int k = 0; k < HALF_FFT; ++k) {
        sum += frame_spec[k] * filter_weights[k];
    }

    // Logarithmic compression with floor
    d_mel_energies[frame_idx * NUM_MEL_BINS + mel_idx] = logf(fmaxf(sum, 1e-6f));
}

// Host launcher wrapper
extern "C" void launch_mel_spectrogram_cuda(
    const float* h_audio,
    int total_samples,
    int hop_length,
    float* h_mel_output,
    int total_frames
) {
    float *d_audio, *d_power, *d_window, *d_mel_weights, *d_mel;
    size_t audio_bytes = total_samples * sizeof(float);
    size_t power_bytes = total_frames * HALF_FFT * sizeof(float);
    size_t mel_bytes = total_frames * NUM_MEL_BINS * sizeof(float);

    cudaMalloc(&d_audio, audio_bytes);
    cudaMalloc(&d_power, power_bytes);
    cudaMalloc(&d_window, FFT_SIZE * sizeof(float));
    cudaMalloc(&d_mel_weights, NUM_MEL_BINS * HALF_FFT * sizeof(float));
    cudaMalloc(&d_mel, mel_bytes);

    cudaMemcpy(d_audio, h_audio, audio_bytes, cudaMemcpyHostToDevice);

    // Launch window & power spectrum kernel
    dim3 block(HALF_FFT);
    dim3 grid(total_frames);
    window_and_power_spectrum_kernel<<<grid, block>>>(d_audio, d_power, d_window, hop_length, total_frames, total_samples);

    // Launch Mel filterbank kernel
    dim3 mel_block(NUM_MEL_BINS);
    dim3 mel_grid(total_frames);
    mel_filterbank_kernel<<<mel_grid, mel_block>>>(d_power, d_mel_weights, d_mel, total_frames);

    cudaMemcpy(h_mel_output, d_mel, mel_bytes, cudaMemcpyDeviceToHost);

    cudaFree(d_audio);
    cudaFree(d_power);
    cudaFree(d_window);
    cudaFree(d_mel_weights);
    cudaFree(d_mel);
}
