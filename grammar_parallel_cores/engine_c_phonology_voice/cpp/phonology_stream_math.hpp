/**
 * phonology_stream_math.hpp - Engine C Sub-Core C3 (C++20)
 * Auditory & Phonological Voice Engine: Real-time pitch tracking (F0),
 * jitter/shimmer extraction, and zero-bridge AMSV Offset 0x00-0x0F synchronization.
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace solorock::grammar::engine_c {

struct AcousticProsodyMetrics {
    float fundamental_frequency_hz;
    float jitter_percentage;
    float shimmer_percentage;
    uint16_t articulation_accuracy_q16;
    uint16_t speech_rate_q16;
    uint16_t fluency_composite_q16;
};

class PhonologyStreamMathEngine {
public:
    PhonologyStreamMathEngine() noexcept = default;

    AcousticProsodyMetrics compute_acoustic_metrics(std::span<const float> audio_frames, float sample_rate) noexcept;

    void sync_to_amsv(void* amsv_base_ptr, const AcousticProsodyMetrics& metrics) noexcept;
};

} // namespace solorock::grammar::engine_c
