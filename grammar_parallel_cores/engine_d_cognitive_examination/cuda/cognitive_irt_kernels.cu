/**
 * cognitive_irt_kernels.cu - Engine D Sub-Core D4 (CUDA)
 * Cognitive Capabilities & Adaptive Examination Engine: Massively parallel 3PL IRT
 * likelihood reductions and item Fisher Information kernel.
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

// 3PL IRT model: P(theta) = c + (1 - c) / (1 + exp(-1.7 * a * (theta - b)))
__device__ inline float irt_3pl_probability(float theta, float a, float b, float c) {
    float exponent = -1.702f * a * (theta - b);
    float logistic = 1.0f / (1.0f + __expf(fminf(fmaxf(exponent, -20.0f), 20.0f)));
    return c + (1.0f - c) * logistic;
}

__global__ void batch_irt_fisher_information_kernel(
    const float* __restrict__ thetas,
    const float* __restrict__ item_a,
    const float* __restrict__ item_b,
    const float* __restrict__ item_c,
    float* __restrict__ fisher_information,
    int num_candidates,
    int num_items
) {
    int cid = blockIdx.y; // candidate index
    int iid = blockIdx.x * blockDim.x + threadIdx.x; // item index

    if (cid >= num_candidates || iid >= num_items) return;

    float theta = thetas[cid];
    float a = item_a[iid];
    float b = item_b[iid];
    float c = item_c[iid];

    float P = irt_3pl_probability(theta, a, b, c);
    float Q = 1.0f - P;

    // Fisher Information I(theta) = (1.702 * a)^2 * (Q / P) * ((P - c) / (1 - c))^2
    float numerator = (P - c) / fmaxf(1.0f - c, 1e-4f);
    float info = (1.702f * a) * (1.702f * a) * (Q / fmaxf(P, 1e-4f)) * (numerator * numerator);

    fisher_information[cid * num_items + iid] = info;
}

extern "C" void launch_batch_irt_fisher_information(
    const float* d_thetas,
    const float* d_a,
    const float* d_b,
    const float* d_c,
    float* d_info,
    int num_candidates,
    int num_items,
    cudaStream_t stream
) {
    dim3 block(128);
    dim3 grid(
        (num_items + block.x - 1) / block.x,
        num_candidates
    );

    batch_irt_fisher_information_kernel<<<grid, block, 0, stream>>>(
        d_thetas, d_a, d_b, d_c, d_info, num_candidates, num_items
    );
}
