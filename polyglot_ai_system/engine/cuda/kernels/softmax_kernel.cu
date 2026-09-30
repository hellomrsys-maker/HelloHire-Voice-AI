// =============================================================================
// engine/cuda/kernels/softmax_kernel.cu
// High-performance online softmax with warp-level reductions
// =============================================================================

#include <cuda_runtime.h>
#include <cfloat>

#define WARP_SIZE 32

// Warp-level reduction for maximum
__device__ __forceinline__ float warp_reduce_max(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1) {
        val = fmaxf(val, __shfl_down_sync(0xffffffff, val, offset));
    }
    return val;
}

// Warp-level reduction for sum
__device__ __forceinline__ float warp_reduce_sum(float val) {
    for (int offset = WARP_SIZE / 2; offset > 0; offset >>= 1) {
        val += __shfl_down_sync(0xffffffff, val, offset);
    }
    return val;
}

/**
 * @brief Row-wise numerically stable softmax kernel.
 * Each block handles one row of the matrix.
 * Uses warp-level reductions for maximum and sum.
 *
 * Grid: (num_rows,)
 * Block: (WARP_SIZE * num_warps,)  where num_warps = ceil(row_size / WARP_SIZE)
 *
 * @param input    Input matrix  [num_rows × row_size]
 * @param output   Output matrix [num_rows × row_size]
 * @param row_size Number of elements per row
 */
extern "C" __global__ void softmax_kernel(
    const float* __restrict__ input,
    float*       __restrict__ output,
    const int    row_size
)
{
    const int row  = blockIdx.x;
    const int tid  = threadIdx.x;
    const float* row_in  = input  + row * row_size;
    float*       row_out = output + row * row_size;

    // Step 1: Find row maximum (with warp reduction)
    float thread_max = -FLT_MAX;
    for (int i = tid; i < row_size; i += blockDim.x) {
        thread_max = fmaxf(thread_max, row_in[i]);
    }
    // Warp reduction
    thread_max = warp_reduce_max(thread_max);

    // Block-wide max via shared memory
    __shared__ float smem_max[32];
    if (tid % WARP_SIZE == 0) {
        smem_max[tid / WARP_SIZE] = thread_max;
    }
    __syncthreads();

    float row_max = -FLT_MAX;
    if (tid < (blockDim.x + WARP_SIZE - 1) / WARP_SIZE) {
        row_max = smem_max[tid];
    }
    row_max = warp_reduce_max(row_max);

    // Step 2: Compute exp(x - max) and sum
    float thread_sum = 0.0f;
    for (int i = tid; i < row_size; i += blockDim.x) {
        float v = expf(row_in[i] - row_max);
        row_out[i] = v;
        thread_sum += v;
    }
    thread_sum = warp_reduce_sum(thread_sum);

    __shared__ float smem_sum[32];
    if (tid % WARP_SIZE == 0) {
        smem_sum[tid / WARP_SIZE] = thread_sum;
    }
    __syncthreads();

    float row_sum = 0.0f;
    if (tid < (blockDim.x + WARP_SIZE - 1) / WARP_SIZE) {
        row_sum = smem_sum[tid];
    }
    row_sum = warp_reduce_sum(row_sum);

    // Step 3: Normalize
    const float inv_sum = 1.0f / (row_sum + 1e-9f);
    for (int i = tid; i < row_size; i += blockDim.x) {
        row_out[i] *= inv_sum;
    }
}

/**
 * @brief Fused attention mask + softmax kernel.
 * Applies an additive mask before softmax (e.g., causal or padding mask).
 * Mask value should be 0 for allowed positions and -1e9 (or -Inf) for blocked.
 */
extern "C" __global__ void masked_softmax_kernel(
    const float* __restrict__ input,
    const float* __restrict__ mask,
    float*       __restrict__ output,
    const int    row_size
)
{
    const int row     = blockIdx.x;
    const int tid     = threadIdx.x;
    const float* row_in   = input  + row * row_size;
    const float* row_mask = mask   + row * row_size;
    float*       row_out  = output + row * row_size;

    // Find maximum of (input + mask)
    float thread_max = -FLT_MAX;
    for (int i = tid; i < row_size; i += blockDim.x) {
        float v = row_in[i] + row_mask[i];
        thread_max = fmaxf(thread_max, isinf(-v) ? -FLT_MAX : v);
    }
    thread_max = warp_reduce_max(thread_max);

    __shared__ float smem_max[32];
    if (tid % WARP_SIZE == 0) smem_max[tid / WARP_SIZE] = thread_max;
    __syncthreads();
    float row_max = -FLT_MAX;
    if (tid < 32) row_max = smem_max[tid < (blockDim.x / WARP_SIZE) ? tid : 0];
    row_max = warp_reduce_max(row_max);

    float thread_sum = 0.0f;
    for (int i = tid; i < row_size; i += blockDim.x) {
        float v = row_in[i] + row_mask[i];
        float e = isinf(-v) ? 0.0f : expf(v - row_max);
        row_out[i]  = e;
        thread_sum += e;
    }
    thread_sum = warp_reduce_sum(thread_sum);

    __shared__ float smem_sum[32];
    if (tid % WARP_SIZE == 0) smem_sum[tid / WARP_SIZE] = thread_sum;
    __syncthreads();
    float row_sum = 0.0f;
    if (tid < 32) row_sum = smem_sum[tid < (blockDim.x / WARP_SIZE) ? tid : 0];
    row_sum = warp_reduce_sum(row_sum);

    const float inv_sum = 1.0f / (row_sum + 1e-9f);
    for (int i = tid; i < row_size; i += blockDim.x) {
        row_out[i] *= inv_sum;
    }
}

// =============================================================================
// Launcher functions (C linkage for FFI)
// =============================================================================

extern "C" {

cudaError_t launch_softmax(
    const float* input, float* output,
    int num_rows, int row_size,
    cudaStream_t stream)
{
    const int threads = min(((row_size + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    dim3 grid(num_rows), block(threads);
    softmax_kernel<<<grid, block, 0, stream>>>(input, output, row_size);
    return cudaGetLastError();
}

cudaError_t launch_masked_softmax(
    const float* input, const float* mask, float* output,
    int num_rows, int row_size,
    cudaStream_t stream)
{
    const int threads = min(((row_size + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    dim3 grid(num_rows), block(threads);
    masked_softmax_kernel<<<grid, block, 0, stream>>>(input, mask, output, row_size);
    return cudaGetLastError();
}

} // extern "C"
