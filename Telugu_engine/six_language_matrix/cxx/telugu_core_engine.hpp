#ifndef TELUGU_CORE_ENGINE_HPP
#define TELUGU_CORE_ENGINE_HPP

#include <cstdint>
#include <cstring>
#include <algorithm>

#pragma pack(push, 1)
struct alignas(64) TeluguAmsvHardwareView {
    uint8_t phoneme_state[8];
    uint8_t prosody_state[8];
    uint8_t cognitive_alpha[8];
    uint8_t cognitive_beta[8];
    uint8_t scenario_state[8];
    uint8_t exam_state[8];
    uint8_t global_alpha[8];
    uint8_t global_beta[8];
};
#pragma pack(pop)

class TeluguCoreEngine {
public:
    TeluguCoreEngine();
    void reset();
    bool processAudioFrame(const float* pcmSamples, size_t sampleCount, float sampleRate);
    void syncAmsvProsody(TeluguAmsvHardwareView* view, float f0, float tempo, float fluency);
    
    float getCurrentF0() const { return currentF0_; }
    float getSpeechTempo() const { return speechTempo_; }

private:
    float currentF0_;
    float speechTempo_;
    uint64_t frameCounter_;
};

#endif // TELUGU_CORE_ENGINE_HPP
