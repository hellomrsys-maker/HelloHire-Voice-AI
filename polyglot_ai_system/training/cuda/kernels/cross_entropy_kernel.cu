// =============================================================================
// training/cuda/kernels/cross_entropy_kernel.cu
// CUDA kernels for numerically stable cross-entropy loss computation
// and its backward pass (gradient w.r.t. logits).
// =============================================================================

#include <cuda_runtime.h>
#include <cfloat>

#define WARP_SIZE 32

__device__ __forceinline__ float warp_reduce_max_f(float val) {
    for (int offset = WARP_SIZE/2; offset > 0; offset >>= 1)
        val = fmaxf(val, __shfl_down_sync(0xffffffff, val, offset));
    return val;
}

__device__ __forceinline__ float warp_reduce_sum_f(float val) {
    for (int offset = WARP_SIZE/2; offset > 0; offset >>= 1)
        val += __shfl_down_sync(0xffffffff, val, offset);
    return val;
}

/**
 * @brief Numerically stable cross-entropy loss + backward kernel.
 *
 * For each sample i:
 *   1. Compute log_softmax(logits[i]) = logits[i] - log(sum_exp(logits[i] - max(logits[i]))) - max
 *   2. loss[i] = -log_softmax[i, target[i]]
 *   3. grad_logits[i, j] = softmax[i, j] - (j == target[i])
 *
 * Grid: (batch_size,)
 * Block: (WARP_SIZE * ceil(vocab_size / WARP_SIZE),) capped at 1024
 *
 * @param logits        [batch, vocab_size] raw logits
 * @param targets       [batch] target token IDs (0-based)
 * @param losses        [batch] output per-sample losses
 * @param grad_logits   [batch, vocab_size] output gradients (may be null for forward-only)
 * @param batch_size    Batch size
 * @param vocab_size    Vocabulary size
 * @param ignore_index  Target ID to ignore (set loss=0, grad=0); use -1 to disable
 * @param compute_grad  Whether to compute gradients
 */
extern "C" __global__ void cross_entropy_forward_backward_kernel(
    const float* __restrict__ logits,      // [batch, vocab]
    const int*   __restrict__ targets,     // [batch]
    float*       __restrict__ losses,      // [batch]
    float*       __restrict__ grad_logits, // [batch, vocab] or null
    const int    batch_size,
    const int    vocab_size,
    const int    ignore_index,
    const bool   compute_grad
)
{
    const int sample = blockIdx.x;
    const int tid    = threadIdx.x;

    if (sample >= batch_size) return;

    const int target = targets[sample];
    const float* row_logits = logits + sample * vocab_size;
    float*       row_grads  = (grad_logits != nullptr) ?
                              grad_logits + sample * vocab_size : nullptr;

    // Handle ignored target
    if (target == ignore_index) {
        if (tid == 0 && losses != nullptr) losses[sample] = 0.0f;
        if (row_grads != nullptr) {
            for (int v = tid; v < vocab_size; v += blockDim.x)
                row_grads[v] = 0.0f;
        }
        return;
    }

    // Step 1: Compute max (for numerical stability)
    float thread_max = -FLT_MAX;
    for (int v = tid; v < vocab_size; v += blockDim.x)
        thread_max = fmaxf(thread_max, row_logits[v]);
    thread_max = warp_reduce_max_f(thread_max);

    __shared__ float smem[64];
    if (tid % WARP_SIZE == 0) smem[tid / WARP_SIZE] = thread_max;
    __syncthreads();
    float row_max = -FLT_MAX;
    if (tid < 32) row_max = smem[tid < (blockDim.x/WARP_SIZE) ? tid : 0];
    row_max = warp_reduce_max_f(row_max);

    // Step 2: Compute sum_exp
    float thread_sum = 0.0f;
    for (int v = tid; v < vocab_size; v += blockDim.x)
        thread_sum += expf(row_logits[v] - row_max);
    thread_sum = warp_reduce_sum_f(thread_sum);

    __shared__ float smem_sum[64];
    if (tid % WARP_SIZE == 0) smem_sum[tid / WARP_SIZE] = thread_sum;
    __syncthreads();
    float row_sum = 0.0f;
    if (tid < 32) row_sum = smem_sum[tid < (blockDim.x/WARP_SIZE) ? tid : 0];
    row_sum = warp_reduce_sum_f(row_sum);

    const float log_sum_exp = row_max + logf(row_sum + 1e-9f);

    // Step 3: Compute loss at position 0
    if (tid == 0 && losses != nullptr) {
        float loss = -(row_logits[target] - log_sum_exp);
        losses[sample] = loss;
    }

    // Step 4: Compute gradient (softmax - one_hot)
    if (compute_grad && row_grads != nullptr) {
        const float inv_sum = 1.0f / (row_sum + 1e-9f);
        for (int v = tid; v < vocab_size; v += blockDim.x) {
            float softmax_v = expf(row_logits[v] - row_max) * inv_sum;
            row_grads[v]    = softmax_v - (v == target ? 1.0f : 0.0f);
        }
    }
}

/**
 * @brief Mean reduction kernel for a batch of per-sample losses.
 * Computes mean(losses) considering only non-zero loss values.
 *
 * Grid: (1,)
 * Block: (WARP_SIZE,)
 */
extern "C" __global__ void reduce_mean_loss_kernel(
    const float* __restrict__ losses,
    float*       __restrict__ mean_loss,
    const int    batch_size
)
{
    const int tid = threadIdx.x;
    float thread_sum = 0.0f;
    int   thread_count = 0;

    for (int i = tid; i < batch_size; i += blockDim.x) {
        thread_sum += losses[i];
        if (losses[i] > 0.0f) ++thread_count;
    }

    thread_sum   = warp_reduce_sum_f(thread_sum);
    float count_f = warp_reduce_sum_f(float(thread_count));

    if (tid == 0) {
        *mean_loss = (count_f > 0.0f) ? thread_sum / count_f : 0.0f;
    }
}

// =============================================================================
// C-linkage launchers
// =============================================================================

extern "C" {

cudaError_t launch_cross_entropy_forward(
    const float* logits, const int* targets, float* losses,
    int batch_size, int vocab_size, int ignore_index,
    cudaStream_t stream)
{
    const int threads = min(((vocab_size + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    cross_entropy_forward_backward_kernel<<<batch_size, threads, 0, stream>>>(
        logits, targets, losses, nullptr, batch_size, vocab_size, ignore_index, false);
    return cudaGetLastError();
}

cudaError_t launch_cross_entropy_forward_backward(
    const float* logits, const int* targets,
    float* losses, float* grad_logits,
    int batch_size, int vocab_size, int ignore_index,
    cudaStream_t stream)
{
    const int threads = min(((vocab_size + WARP_SIZE - 1) / WARP_SIZE) * WARP_SIZE, 1024);
    cross_entropy_forward_backward_kernel<<<batch_size, threads, 0, stream>>>(
        logits, targets, losses, grad_logits,
        batch_size, vocab_size, ignore_index, true);
    return cudaGetLastError();
}

cudaError_t launch_reduce_mean_loss(
    const float* losses, float* mean_loss,
    int batch_size, cudaStream_t stream)
{
    reduce_mean_loss_kernel<<<1, WARP_SIZE, 0, stream>>>(losses, mean_loss, batch_size);
    return cudaGetLastError();
}

} // extern "C"
