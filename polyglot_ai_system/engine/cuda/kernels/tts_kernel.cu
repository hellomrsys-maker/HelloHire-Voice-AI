// =============================================================================
// engine/cuda/kernels/tts_kernel.cu
// Text-to-Speech synthesis GPU kernels:
//   - Vocoder synthesis (Griffin-Lim IFFT-based)
//   - Mel-to-waveform upsampling
//   - Waveform normalization
// Production: these are preprocessing/postprocessing stages around
// a neural TTS model (e.g., VITS, FastSpeech2) that runs via cuDNN.
// =============================================================================

#include <cuda_runtime.h>
#include <cufft.h>
#include <cmath>

#define PI_F 3.14159265358979323846f

// =============================================================================
// Inverse STFT (overlap-add) kernel for Griffin-Lim vocoder
// =============================================================================

/**
 * @brief Overlap-add kernel for ISTFT.
 * Accumulates windowed IFFT frames back into the waveform using OLA.
 *
 * Grid: (n_frames,)
 * Block: (frame_len,)
 */
extern "C" __global__ void istft_overlap_add_kernel(
    const float* __restrict__ frames,     // [n_frames, frame_len]
    const float* __restrict__ window,     // [frame_len] synthesis window
    float*       __restrict__ waveform,   // [n_samples] — accumulated
    float*       __restrict__ window_sum, // [n_samples] — window accumulator
    const int    n_frames,
    const int    frame_len,
    const int    hop_length,
    const int    n_samples
)
{
    const int frame   = blockIdx.x;
    const int dim_idx = threadIdx.x;

    if (frame >= n_frames || dim_idx >= frame_len) return;

    const int sample_idx = frame * hop_length + dim_idx;
    if (sample_idx >= n_samples) return;

    const float w = window[dim_idx];
    atomicAdd(&waveform[sample_idx],    frames[frame * frame_len + dim_idx] * w);
    atomicAdd(&window_sum[sample_idx],  w * w);
}

/**
 * @brief Window normalization kernel for ISTFT.
 * output[i] = waveform[i] / (window_sum[i] + eps)
 */
extern "C" __global__ void istft_normalize_kernel(
    const float* __restrict__ waveform,
    const float* __restrict__ window_sum,
    float*       __restrict__ output,
    const int    n_samples,
    const float  eps
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;
    output[idx] = waveform[idx] / (window_sum[idx] + eps);
}

// =============================================================================
// Waveform normalization kernel (peak normalization)
// =============================================================================

extern "C" __global__ void peak_normalize_kernel(
    float*       __restrict__ waveform,
    const float* __restrict__ peak_val,   // Scalar — max absolute value in waveform
    const int    n_samples,
    const float  target_peak              // Target peak amplitude (e.g., 0.95)
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;

    const float scale = (*peak_val > 1e-9f) ? (target_peak / *peak_val) : 1.0f;
    waveform[idx] *= scale;
}

/**
 * @brief Float-to-int16 quantization kernel.
 * Converts float [-1, 1] samples to int16 PCM.
 */
extern "C" __global__ void float_to_int16_kernel(
    const float*  __restrict__ float_pcm,
    short*        __restrict__ int16_pcm,
    const int     n_samples
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;

    float v = fmaxf(-1.0f, fminf(1.0f, float_pcm[idx]));
    int16_pcm[idx] = (short)(v * 32767.0f);
}

/**
 * @brief Int16-to-float normalization kernel.
 * Converts int16 PCM samples to float [-1, 1].
 */
extern "C" __global__ void int16_to_float_kernel(
    const short*  __restrict__ int16_pcm,
    float*        __restrict__ float_pcm,
    const int     n_samples
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;
    float_pcm[idx] = (float)int16_pcm[idx] / 32768.0f;
}

/**
 * @brief Upsample mel spectrogram frames to waveform resolution.
 * Simple nearest-neighbor upsampling.
 *
 * Grid: (n_frames,)
 * Block: (upsample_factor,)
 */
extern "C" __global__ void upsample_mel_kernel(
    const float* __restrict__ mel,         // [n_frames, n_mel]
    float*       __restrict__ upsampled,   // [n_frames * upsample_factor, n_mel]
    const int    n_frames,
    const int    n_mel,
    const int    upsample_factor
)
{
    const int frame       = blockIdx.x;
    const int hop_offset  = threadIdx.x;

    if (frame >= n_frames || hop_offset >= upsample_factor) return;

    const int out_row = frame * upsample_factor + hop_offset;

    for (int m = 0; m < n_mel; ++m) {
        upsampled[out_row * n_mel + m] = mel[frame * n_mel + m];
    }
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_istft_overlap_add(
    const float* frames, const float* window,
    float* waveform, float* window_sum,
    int n_frames, int frame_len, int hop_length, int n_samples,
    cudaStream_t stream)
{
    const int block = min(frame_len, 512);
    istft_overlap_add_kernel<<<n_frames, block, 0, stream>>>(
        frames, window, waveform, window_sum,
        n_frames, frame_len, hop_length, n_samples);
    return cudaGetLastError();
}

cudaError_t launch_float_to_int16(
    const float* float_pcm, short* int16_pcm, int n_samples,
    cudaStream_t stream)
{
    const int block = 1024;
    const int grid  = (n_samples + block - 1) / block;
    float_to_int16_kernel<<<grid, block, 0, stream>>>(float_pcm, int16_pcm, n_samples);
    return cudaGetLastError();
}

cudaError_t launch_int16_to_float(
    const short* int16_pcm, float* float_pcm, int n_samples,
    cudaStream_t stream)
{
    const int block = 1024;
    const int grid  = (n_samples + block - 1) / block;
    int16_to_float_kernel<<<grid, block, 0, stream>>>(int16_pcm, float_pcm, n_samples);
    return cudaGetLastError();
}

} // extern "C"
