/**
 * @file ccte_gpu_kernels.cu
 * @brief CUDA Kernels for Parallel Cognitive Capability Computations.
 *
 * 1. Neural Oscillation Kernel (Wilson-Cowan Cortical Focus Simulation)
 * 2. Semantic Spreading Activation Matrix Kernel
 * 3. High-Dimensional Vector Novelty Dispersion Kernel
 * 4. Vocal Micro-Tremor Spectral Flux Kernel
 */

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

/**
 * Kernel 1: Parallel Wilson-Cowan Cortical Node Focus Simulation
 */
__global__ void wilson_cowan_cortical_kernel(
    float* __restrict__ d_E, // Excitatory population [NUM_NODES, STEPS]
    float* __restrict__ d_I, // Inhibitory population [NUM_NODES, STEPS]
    const float* __restrict__ d_external_drive,
    int num_nodes,
    int steps,
    float dt
) {
    int node_idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (node_idx >= num_nodes) return;

    float E = 0.1f;
    float I = 0.05f;
    float P = d_external_drive[node_idx];

    const float tau_E = 0.01f;
    const float tau_I = 0.02f;
    const float w_ee = 12.0f;
    const float w_ei = 10.0f;
    const float w_ie = 10.0f;
    const float w_ii = 1.5f;

    for (int t = 0; t < steps; ++t) {
        d_E[node_idx * steps + t] = E;
        d_I[node_idx * steps + t] = I;

        // Sigmoid activation
        float sig_E = 1.0f / (1.0f + __expf(-(w_ee * E - w_ei * I + P)));
        float sig_I = 1.0f / (1.0f + __expf(-(w_ie * E - w_ii * I)));

        float dE = (-E + sig_E) / tau_E;
        float dI = (-I + sig_I) / tau_I;

        E = fmaxf(0.0f, E + dt * dE);
        I = fmaxf(0.0f, I + dt * dI);
    }
}

/**
 * Kernel 2: Semantic Spreading Activation Matrix Multiply
 * A_{t+1} = \sigma(\alpha \cdot W \cdot A_t + (1 - \gamma) \cdot A_0)
 */
__global__ void semantic_spreading_activation_kernel(
    const float* __restrict__ d_W, // Adjacency weights [N, N]
    const float* __restrict__ d_A_current,
    const float* __restrict__ d_A_init,
    float* __restrict__ d_A_next,
    int N,
    float alpha,
    float decay
) {
    int row = blockDim.x * blockIdx.x + threadIdx.x;
    if (row >= N) return;

    float sum = 0.0f;
    #pragma unroll 16
    for (int col = 0; col < N; ++col) {
        sum += d_W[row * N + col] * d_A_current[col];
    }

    float act = alpha * sum + (1.0f - decay) * d_A_init[row];
    // Sigmoid thresholding
    d_A_next[row] = 1.0f / (1.0f + __expf(-act));
}

/**
 * Kernel 3: High-Dimensional Conceptual Novelty Dispersion
 * Computes cosine angular distances across concept embedding clusters.
 */
__global__ void conceptual_novelty_dispersion_kernel(
    const float* __restrict__ d_idea_embeddings, // [NUM_IDEAS, DIM]
    const float* __restrict__ d_centroids,       // [NUM_CLUSTERS, DIM]
    float* __restrict__ d_novelty_scores,        // [NUM_IDEAS]
    int num_ideas,
    int num_clusters,
    int dim
) {
    int idea_idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idea_idx >= num_ideas) return;

    const float* idea = d_idea_embeddings + (idea_idx * dim);

    float norm_idea_sq = 0.0f;
    for (int d = 0; d < dim; ++d) {
        norm_idea_sq += idea[d] * idea[d];
    }
    float norm_idea = sqrtf(norm_idea_sq) + 1e-7f;

    float total_angle = 0.0f;
    for (int c = 0; c < num_clusters; ++c) {
        const float* cent = d_centroids + (c * dim);
        float dot = 0.0f;
        float norm_cent_sq = 0.0f;
        for (int d = 0; d < dim; ++d) {
            dot += idea[d] * cent[d];
            norm_cent_sq += cent[d] * cent[d];
        }
        float norm_cent = sqrtf(norm_cent_sq) + 1e-7f;
        float cos_sim = fminf(1.0f, fmaxf(-1.0f, dot / (norm_idea * norm_cent)));
        total_angle += acosf(cos_sim);
    }

    d_novelty_scores[idea_idx] = total_angle / (float)num_clusters;
}
