// =============================================================================
// engine/cuda/kernels/asr_kernel.cu
// Automatic Speech Recognition (ASR) GPU processing kernels:
//   - Mel spectrogram extraction
//   - Feature normalization
//   - Log-filterbank energies
// These are preprocessing stages before Whisper-style ASR inference.
// =============================================================================

#include <cuda_runtime.h>
#include <cufft.h>
#include <cmath>

#define PI_F 3.14159265358979323846f
#define LOG_EPS 1e-10f

// =============================================================================
// Pre-emphasis filter kernel
// Applies pre-emphasis: y[t] = x[t] - alpha * x[t-1]
// =============================================================================

extern "C" __global__ void preemphasis_kernel(
    const float* __restrict__ input,    // [n_samples]
    float*       __restrict__ output,   // [n_samples]
    const int    n_samples,
    const float  alpha                  // Pre-emphasis coefficient (typical: 0.97)
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_samples) return;
    output[idx] = (idx == 0) ? input[0] : input[idx] - alpha * input[idx - 1];
}

// =============================================================================
// Hamming window kernel
// =============================================================================

extern "C" __global__ void hamming_window_kernel(
    float*       __restrict__ frame,   // [frame_len] — modified in-place
    const int    frame_len
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= frame_len) return;
    float w = 0.54f - 0.46f * cosf(2.0f * PI_F * (float)idx / (float)(frame_len - 1));
    frame[idx] *= w;
}

// =============================================================================
// Power spectrum kernel
// Converts complex FFT output to power spectrum: |X[k]|²
// =============================================================================

extern "C" __global__ void power_spectrum_kernel(
    const float* __restrict__ fft_real,  // [n_fft/2 + 1]
    const float* __restrict__ fft_imag,  // [n_fft/2 + 1]
    float*       __restrict__ power,     // [n_fft/2 + 1]
    const int    n_fft_half_plus1
)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n_fft_half_plus1) return;
    power[idx] = fft_real[idx] * fft_real[idx] + fft_imag[idx] * fft_imag[idx];
}

// =============================================================================
// Mel filterbank application kernel
// Applies triangular Mel filters to power spectrum
// =============================================================================

extern "C" __global__ void mel_filterbank_kernel(
    const float* __restrict__ power,        // [n_fft/2 + 1]
    const float* __restrict__ filterbank,   // [n_mel, n_fft/2 + 1]
    float*       __restrict__ mel_energy,   // [n_mel]
    const int    n_mel,
    const int    n_fft_half_plus1
)
{
    const int mel_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (mel_idx >= n_mel) return;

    float energy = 0.0f;
    for (int k = 0; k < n_fft_half_plus1; ++k) {
        energy += filterbank[mel_idx * n_fft_half_plus1 + k] * power[k];
    }
    mel_energy[mel_idx] = energy;
}

// =============================================================================
// Log-energy normalization kernel
// Applies log transformation and CMVN normalization
// =============================================================================

extern "C" __global__ void log_mel_kernel(
    const float* __restrict__ mel_energy, // [n_frames, n_mel]
    float*       __restrict__ log_mel,    // [n_frames, n_mel]
    const int    n_frames,
    const int    n_mel
)
{
    const int frame   = blockIdx.x;
    const int mel_idx = threadIdx.x;

    if (frame >= n_frames || mel_idx >= n_mel) return;

    const int idx = frame * n_mel + mel_idx;
    log_mel[idx] = log10f(fmaxf(mel_energy[idx], LOG_EPS));
}

// =============================================================================
// CMVN (Cepstral Mean-Variance Normalization) kernel
// =============================================================================

extern "C" __global__ void cmvn_kernel(
    float*       __restrict__ features,   // [n_frames, n_mel] — modified in-place
    const float* __restrict__ mean,       // [n_mel]
    const float* __restrict__ std_inv,    // [n_mel] — 1/std
    const int    n_frames,
    const int    n_mel
)
{
    const int frame   = blockIdx.x;
    const int mel_idx = threadIdx.x;

    if (frame >= n_frames || mel_idx >= n_mel) return;

    const int idx = frame * n_mel + mel_idx;
    features[idx] = (features[idx] - mean[mel_idx]) * std_inv[mel_idx];
}

// =============================================================================
// Stacking / striding kernel for temporal context
// Stacks `context_frames` consecutive frames into a single feature vector
// =============================================================================

extern "C" __global__ void frame_stacking_kernel(
    const float* __restrict__ features,      // [n_frames, n_mel]
    float*       __restrict__ stacked,       // [n_output_frames, n_mel * context]
    const int    n_frames,
    const int    n_mel,
    const int    context,                    // Total context frames to stack
    const int    stride                      // Frame stride (e.g., 3 for 3x downsampling)
)
{
    const int out_frame = blockIdx.x;
    const int dim       = threadIdx.x;

    const int in_center = out_frame * stride;
    const int half_ctx  = context / 2;

    if (dim >= n_mel * context) return;

    const int ctx_offset = dim / n_mel;         // Which context frame
    const int feat_dim   = dim % n_mel;          // Which feature dimension
    const int in_frame   = in_center + ctx_offset - half_ctx;

    // Pad with zeros at boundaries
    float val = 0.0f;
    if (in_frame >= 0 && in_frame < n_frames) {
        val = features[in_frame * n_mel + feat_dim];
    }

    stacked[out_frame * (n_mel * context) + dim] = val;
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_preemphasis(
    const float* input, float* output, int n_samples, float alpha,
    cudaStream_t stream)
{
    const int block = 256;
    const int grid  = (n_samples + block - 1) / block;
    preemphasis_kernel<<<grid, block, 0, stream>>>(input, output, n_samples, alpha);
    return cudaGetLastError();
}

cudaError_t launch_hamming_window(
    float* frame, int frame_len, cudaStream_t stream)
{
    hamming_window_kernel<<<1, min(frame_len, 1024), 0, stream>>>(frame, frame_len);
    return cudaGetLastError();
}

cudaError_t launch_mel_filterbank(
    const float* power, const float* filterbank, float* mel_energy,
    int n_mel, int n_fft_half_plus1, cudaStream_t stream)
{
    const int block = min(n_mel, 256);
    mel_filterbank_kernel<<<(n_mel + block - 1) / block, block, 0, stream>>>(
        power, filterbank, mel_energy, n_mel, n_fft_half_plus1);
    return cudaGetLastError();
}

cudaError_t launch_log_mel(
    const float* mel_energy, float* log_mel,
    int n_frames, int n_mel, cudaStream_t stream)
{
    log_mel_kernel<<<n_frames, min(n_mel, 1024), 0, stream>>>(
        mel_energy, log_mel, n_frames, n_mel);
    return cudaGetLastError();
}

cudaError_t launch_cmvn(
    float* features, const float* mean, const float* std_inv,
    int n_frames, int n_mel, cudaStream_t stream)
{
    cmvn_kernel<<<n_frames, min(n_mel, 1024), 0, stream>>>(
        features, mean, std_inv, n_frames, n_mel);
    return cudaGetLastError();
}

} // extern "C"
