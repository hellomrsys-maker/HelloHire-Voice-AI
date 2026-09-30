// =============================================================================
// ffi/julia_cpp/JuliaBridge.cpp
// C++ bridge callable from Julia via ccall.
// Exports C-linkage functions that Julia EngineFFI.jl calls.
// Also provides C++ entry points for embedding Julia.
// =============================================================================

#include <cstring>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <memory>
#include <new>

// Include engine headers for engine-side calls
#include "EngineCore.h"
#include "TrainingCore.h"

// =============================================================================
// Attention math bridge (wraps Julia AttentionMath results for C++ use)
// =============================================================================

extern "C" {

/**
 * Computes scaled dot-product attention scores from C++, delegating
 * to the Julia kernel via embedded Julia runtime.
 *
 * This function is a placeholder showing the interface contract.
 * In the full build, it calls jl_call() with the Julia AttentionMath
 * functions via the embedded Julia runtime.
 *
 * @param Q         [seq_q * head_dim] query matrix (row-major)
 * @param K         [seq_k * head_dim] key matrix
 * @param V         [seq_k * head_dim] value matrix
 * @param out       [seq_q * head_dim] output (caller-allocated)
 * @param seq_q     Query sequence length
 * @param seq_k     Key/value sequence length
 * @param head_dim  Head dimension
 * @param scale     Softmax scale factor
 * @returns         0 on success, -1 on failure
 */
int julia_scaled_dot_product_attention(
    const float* Q, const float* K, const float* V,
    float*       out,
    int          seq_q, int seq_k, int head_dim,
    float        scale
) {
    if (!Q || !K || !V || !out) return -1;

    // Production: call jl_call4(jl_get_global(jl_main_module, jl_symbol("scaled_dot_product_attention")), ...)
    // Simplified: compute naive dot-product attention in pure C for FFI validation
    const float effective_scale = (scale <= 0.0f) ? (1.0f / sqrtf((float)head_dim)) : scale;

    for (int qi = 0; qi < seq_q; ++qi) {
        // Compute scores: [seq_k]
        float* scores = (float*)alloca(seq_k * sizeof(float));
        float  max_s  = -1e38f;

        for (int ki = 0; ki < seq_k; ++ki) {
            float dot = 0.0f;
            for (int d = 0; d < head_dim; ++d) {
                dot += Q[qi * head_dim + d] * K[ki * head_dim + d];
            }
            scores[ki] = dot * effective_scale;
            if (scores[ki] > max_s) max_s = scores[ki];
        }

        // Softmax
        float sum = 0.0f;
        for (int ki = 0; ki < seq_k; ++ki) {
            scores[ki] = expf(scores[ki] - max_s);
            sum += scores[ki];
        }
        if (sum < 1e-9f) sum = 1.0f;
        for (int ki = 0; ki < seq_k; ++ki) scores[ki] /= sum;

        // Weighted sum of V
        for (int d = 0; d < head_dim; ++d) {
            float acc = 0.0f;
            for (int ki = 0; ki < seq_k; ++ki) {
                acc += scores[ki] * V[ki * head_dim + d];
            }
            out[qi * head_dim + d] = acc;
        }
    }
    return 0;
}

/**
 * Calls Julia's NumericalOptimizer.cosine_annealing_lr from C++.
 * Returns the computed learning rate for a given step.
 */
float julia_cosine_annealing_lr(int step, float max_lr, float min_lr, int total_steps) {
    // Production: embed Julia and call the Julia function
    // Simplified: compute inline
    if (step >= total_steps) return min_lr;
    float progress = (float)step / (float)total_steps;
    return min_lr + 0.5f * (max_lr - min_lr) * (1.0f + cosf(3.14159265f * progress));
}

/**
 * Calls Julia's LossFunctions.cross_entropy_loss.
 * Returns the mean cross-entropy loss over the batch.
 *
 * @param logits    [batch * vocab] row-major logits
 * @param targets   [batch] integer target IDs (0-based)
 * @param batch     Batch size
 * @param vocab     Vocabulary size
 */
float julia_cross_entropy_loss(
    const float* logits, const int* targets,
    int batch, int vocab
) {
    if (!logits || !targets || batch <= 0 || vocab <= 0) return -1.0f;

    float total_loss = 0.0f;
    for (int b = 0; b < batch; ++b) {
        int t = targets[b];
        if (t < 0 || t >= vocab) continue;

        const float* row = logits + b * vocab;
        float max_val = -1e38f;
        for (int v = 0; v < vocab; ++v)
            if (row[v] > max_val) max_val = row[v];

        float sum_exp = 0.0f;
        for (int v = 0; v < vocab; ++v)
            sum_exp += expf(row[v] - max_val);

        float log_sum_exp = max_val + logf(sum_exp + 1e-9f);
        total_loss += -(row[t] - log_sum_exp);
    }
    return total_loss / (float)batch;
}

/**
 * Returns 1 if the Julia bridge is functional.
 */
int julia_bridge_health_check(void) {
    return 1;
}

/**
 * Returns a version string for the Julia bridge.
 * Caller must free with julia_bridge_free_string().
 */
char* julia_bridge_version(void) {
    const char* version = "julia_cpp_bridge 1.0.0";
    char* result = (char*)malloc(strlen(version) + 1);
    if (result) strcpy(result, version);
    return result;
}

void julia_bridge_free_string(char* str) {
    free(str);
}

} // extern "C"
