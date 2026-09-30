/**
 * @file vce_engine.cpp
 * @brief Implementation and C ABI exports for the Verbal Communication Sub-Engine.
 */

#include "vce_engine.hpp"
#include <iostream>

static solorock::vce::VerbalCommunicationEngine* g_vce_instance = nullptr;

extern "C" {

void vce_init(void* amsv_state_vector) {
    auto* sv = reinterpret_cast<solorock::amsv::AtomicStateVector*>(amsv_state_vector);
    if (!g_vce_instance) {
        g_vce_instance = new solorock::vce::VerbalCommunicationEngine(sv);
    }
}

void vce_process_audio(const float* samples, int count, int sample_rate) {
    if (g_vce_instance && samples && count > 0) {
        g_vce_instance->process_audio_frame(samples, static_cast<size_t>(count), sample_rate);
    }
}

float vce_get_dtw_pronunciation_score(const float* cand_mels, int cand_len, const float* ref_mels, int ref_len, int dim) {
    if (!g_vce_instance || !cand_mels || !ref_mels) return 0.0f;
    std::vector<float> cand(cand_mels, cand_mels + cand_len);
    std::vector<float> ref(ref_mels, ref_mels + ref_len);
    return g_vce_instance->compute_pronunciation_dtw(cand, ref, dim);
}

void vce_shutdown() {
    delete g_vce_instance;
    g_vce_instance = nullptr;
}

}
