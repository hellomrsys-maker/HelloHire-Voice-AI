// Hindustani GPU Parallel CUDA Kernels
// Parallel Batched Split-Ergative Agreement Tensor Dispatch

#include <cuda_runtime.h>
#include <cstdint>

extern "C" {

/**
 * Evaluates split-ergative verbal agreement across large batches of Hindustani sentences.
 * is_transitive: 1 if transitive, 0 if intransitive
 * is_perfective: 1 if perfective/past, 0 otherwise
 * has_ne: 1 if subject has ne, 0 otherwise
 * has_ko: 1 if direct object has ko, 0 otherwise
 * obj_gender: 0 for M, 1 for F
 * obj_number: 0 for SG, 1 for PL
 * out_valid: 1 if agreement is valid, 0 if violation
 * out_verb_form: 0=M_SG, 1=M_PL, 2=F_SG, 3=F_PL
 */
__global__ void evaluate_ergative_concord_batch_kernel(
    const int32_t* __restrict__ is_transitive,
    const int32_t* __restrict__ is_perfective,
    const int32_t* __restrict__ has_ne,
    const int32_t* __restrict__ has_ko,
    const int32_t* __restrict__ obj_gender,
    const int32_t* __restrict__ obj_number,
    int32_t* __restrict__ out_valid,
    int32_t* __restrict__ out_verb_form,
    int32_t batch_size
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= batch_size) return;

    int trans = is_transitive[idx];
    int perf = is_perfective[idx];
    int ne = has_ne[idx];
    int ko = has_ko[idx];
    int g = obj_gender[idx];
    int n = obj_number[idx];

    int valid = 1;
    int v_form = 0; // default M_SG

    if (trans == 1 && perf == 1) {
        // Transitive perfective MUST have ne on subject
        if (ne != 1) {
            valid = 0;
        }

        if (ko == 1) {
            // Default neutral masculine singular
            v_form = 0;
        } else {
            // Agrees with direct object
            if (g == 0 && n == 0) v_form = 0; // M_SG
            else if (g == 0 && n == 1) v_form = 1; // M_PL
            else if (g == 1 && n == 0) v_form = 2; // F_SG
            else if (g == 1 && n == 1) v_form = 3; // F_PL
        }
    } else {
        // Non-perfective or intransitive: ne is forbidden
        if (ne == 1) {
            valid = 0;
        }
    }

    out_valid[idx] = valid;
    out_verb_form[idx] = v_form;
}

} // extern "C"
