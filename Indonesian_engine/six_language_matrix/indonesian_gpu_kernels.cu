// Indonesian Engine — CUDA Parallel GPU Kernels
// Parallel evaluation of morphophonemic nasal assimilation and voice symmetry.

#include <cuda_runtime.h>
#include <cstdint>

__device__ bool is_invalid_unassimilated_stop(uint8_t first_char, uint8_t prefix_code) {
    // prefix_code: 1=mem, 2=men, 3=meny, 4=meng
    // If root starts with 'p' ('p'=112) and prefix is 'mem' with 'p' retained (e.g. memp)
    if (first_char == 'p' && prefix_code == 1) return true;
    if (first_char == 't' && prefix_code == 2) return true;
    if (first_char == 'k' && prefix_code == 4) return true;
    return false;
}

__global__ void evaluate_indonesian_nasal_batches_kernel(
    const uint8_t* __restrict__ root_initials,
    const uint8_t* __restrict__ prefix_codes,
    uint8_t* __restrict__ violation_flags,
    int batch_size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < batch_size) {
        uint8_t rc = root_initials[idx];
        uint8_t pc = prefix_codes[idx];
        violation_flags[idx] = is_invalid_unassimilated_stop(rc, pc) ? 1 : 0;
    }
}

extern "C" void launch_indonesian_nasal_eval(
    const uint8_t* d_roots,
    const uint8_t* d_prefixes,
    uint8_t* d_violations,
    int batch_size,
    cudaStream_t stream
) {
    int threads = 256;
    int blocks = (batch_size + threads - 1) / threads;
    evaluate_indonesian_nasal_batches_kernel<<<blocks, threads, 0, stream>>>(d_roots, d_prefixes, d_violations, batch_size);
}
