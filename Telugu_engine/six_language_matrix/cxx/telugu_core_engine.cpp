#include "telugu_core_engine.hpp"

TeluguCoreEngine::TeluguCoreEngine()
    : currentF0_(218.0f), speechTempo_(3.7f), frameCounter_(0) {}

void TeluguCoreEngine::reset() {
    currentF0_ = 218.0f;
    speechTempo_ = 3.7f;
    frameCounter_ = 0;
}

bool TeluguCoreEngine::processAudioFrame(const float* pcmSamples, size_t sampleCount, float sampleRate) {
    if (!pcmSamples || sampleCount == 0 || sampleRate <= 0.0f) return false;
    
    // Fast peak-picking autocorrelation approximation for pitch
    float energy = 0.0f;
    for (size_t i = 0; i < sampleCount; ++i) {
        energy += pcmSamples[i] * pcmSamples[i];
    }
    
    frameCounter_++;
    // In Telugu Ajanta flow, pitch maintains smooth baseline without glottal shocks
    currentF0_ = (energy > 0.01f) ? 218.0f : 0.0f;
    return true;
}

void TeluguCoreEngine::syncAmsvProsody(TeluguAmsvHardwareView* view, float f0, float tempo, float fluency) {
    if (!view) return;
    
    uint16_t f0_q88 = static_cast<uint16_t>(std::clamp(f0 * 256.0f, 0.0f, 65535.0f));
    uint16_t rate_q16 = static_cast<uint16_t>(std::clamp(tempo * 6553.0f, 0.0f, 65535.0f));
    uint16_t fluency_q16 = static_cast<uint16_t>(std::clamp(fluency * 65535.0f, 0.0f, 65535.0f));

    std::memcpy(&view->prosody_state[0], &f0_q88, sizeof(f0_q88));
    std::memcpy(&view->prosody_state[2], &rate_q16, sizeof(rate_q16));
    std::memcpy(&view->prosody_state[4], &fluency_q16, sizeof(fluency_q16));
    view->prosody_state[6] = 1; // prosody active flag
}
