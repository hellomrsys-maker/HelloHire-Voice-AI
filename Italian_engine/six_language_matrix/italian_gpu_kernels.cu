// Italian Engine — CUDA Parallel GPU Kernels
// High-throughput parallel evaluation of clitic ordering and past participle concord.

#include <cuda_runtime.h>
#include <cstdint>

__device__ bool is_unshifted_clitic(uint16_t c1, uint16_t c2) {
    // Check if indirect clitic failed to shift -i -> -e before direct clitic
    // e.g. mi(0x01) + lo(0x02) instead of me(0x11) + lo(0x02)
    return (c1 <= 0x05 && c2 >= 0x10 && c2 <= 0x15);
}

__global__ void evaluate_italian_clitic_batches_kernel(
    const uint16_t* __restrict__ first_clitics,
    const uint16_t* __restrict__ second_clitics,
    uint8_t* __restrict__ violation_flags,
    int batch_size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < batch_size) {
        uint16_t c1 = first_clitics[idx];
        uint16_t c2 = second_clitics[idx];
        violation_flags[idx] = is_unshifted_clitic(c1, c2) ? 1 : 0;
    }
}

extern "C" void launch_italian_clitic_eval(
    const uint16_t* d_c1,
    const uint16_t* d_c2,
    uint8_t* d_violations,
    int batch_size,
    cudaStream_t stream
) {
    int threads = 256;
    int blocks = (batch_size + threads - 1) / threads;
    evaluate_italian_clitic_batches_kernel<<<blocks, threads, 0, stream>>>(d_c1, d_c2, d_violations, batch_size);
}
