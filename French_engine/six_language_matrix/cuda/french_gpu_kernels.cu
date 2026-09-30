// French GPU Parallel CUDA Kernels
// Parallel Batched Participle Concordance & Liaison Coda Dispatch

#include <cuda_runtime.h>
#include <cstdint>

extern "C" {

/**
 * Evaluates past participle concordance in parallel across large sentence batches.
 * aux_type: 0 for avoir, 1 for etre
 * cod_precedes: 1 if COD precedes verb, 0 otherwise
 * gender: 0 for M, 1 for F
 * number: 0 for SG, 1 for PL
 * out_agreement_suffix: 0=none, 1='e', 2='s', 3='es'
 */
__global__ void evaluate_participle_agreement_batch_kernel(
    const int32_t* __restrict__ aux_type,
    const int32_t* __restrict__ cod_precedes,
    const int32_t* __restrict__ gender,
    const int32_t* __restrict__ number,
    int32_t* __restrict__ out_suffix,
    int32_t batch_size
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= batch_size) return;

    int aux = aux_type[idx];
    int cod_prec = cod_precedes[idx];
    int g = gender[idx];
    int n = number[idx];

    int suffix = 0; // default none

    if (aux == 1) {
        // Auxiliary être: agrees with subject
        if (g == 1 && n == 1) {
            suffix = 3; // 'es'
        } else if (g == 1) {
            suffix = 1; // 'e'
        } else if (n == 1) {
            suffix = 2; // 's'
        }
    } else if (aux == 0 && cod_prec == 1) {
        // Auxiliary avoir with preceding COD: agrees with COD
        if (g == 1 && n == 1) {
            suffix = 3; // 'es'
        } else if (g == 1) {
            suffix = 1; // 'e'
        } else if (n == 1) {
            suffix = 2; // 's'
        }
    }

    out_suffix[idx] = suffix;
}

/**
 * Parallel liaison consonantal voicing shift kernel.
 */
__global__ void french_liaison_voicing_kernel(
    const char* __restrict__ codas,
    char* __restrict__ out_realizations,
    int32_t length
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= length) return;

    char c = codas[idx];
    char out_c = 0;

    switch (c) {
        case 's':
        case 'x':
        case 'z':
            out_c = 'z';
            break;
        case 'd':
        case 't':
            out_c = 't';
            break;
        case 'n':
            out_c = 'n';
            break;
        case 'p':
            out_c = 'p';
            break;
        default:
            out_c = 0;
            break;
    }

    out_realizations[idx] = out_c;
}

} // extern "C"
