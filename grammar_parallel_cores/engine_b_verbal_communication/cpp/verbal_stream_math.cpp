/**
 * verbal_stream_math.cpp - Engine B Sub-Core B3 (C++20)
 * Implementation of verbal stream math and lock-free AMSV Offset 0x20 sync.
 */

#include "verbal_stream_math.hpp"
#include <algorithm>
#include <atomic>

namespace solorock::grammar::engine_b {

VerbalStreamMetrics VerbalStreamMathEngine::compute_verbal_metrics(
    std::string_view text,
    float duration_sec,
    uint16_t turn_number,
    uint16_t phase
) noexcept {
    if (text.empty()) {
        return VerbalStreamMetrics{0, 0.0f, 0.0f, 0, turn_number, phase};
    }

    uint32_t words = 0;
    bool in_word = false;

    for (char c : text) {
        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
            if (in_word) {
                words++;
                in_word = false;
            }
        } else {
            in_word = true;
        }
    }
    if (in_word) words++;

    float safe_duration = (duration_sec > 0.1f) ? duration_sec : (words * 0.4f);
    float wpm = (words / safe_duration) * 60.0f;

    // Ideal speaking rate: 120-160 WPM
    float rate_norm = 1.0f - std::clamp(std::abs(wpm - 140.0f) / 100.0f, 0.0f, 1.0f);
    float filler_ratio = 0.03f; // Baseline

    float compliance = std::clamp(rate_norm * 0.7f + (1.0f - filler_ratio) * 0.3f, 0.0f, 1.0f);
    uint16_t comp_q16 = static_cast<uint16_t>(compliance * 65535.0f);

    return VerbalStreamMetrics{
        words,
        wpm,
        filler_ratio,
        comp_q16,
        turn_number,
        phase
    };
}

void VerbalStreamMathEngine::sync_to_amsv(void* amsv_base_ptr, const VerbalStreamMetrics& metrics) noexcept {
    if (!amsv_base_ptr) return;

    // Direct physical write to Offset 0x20 (rsse_scenario_state):
    // Offset 0x20: scenario/format ID (uint16)
    // Offset 0x22: turn counter (uint16)
    // Offset 0x24: register compliance (Q16 fixed-point)
    // Offset 0x26: interview phase (uint16)
    uint8_t* raw = static_cast<uint8_t*>(amsv_base_ptr);
    std::atomic_ref<uint16_t> turn_ref(*reinterpret_cast<uint16_t*>(raw + 0x22));
    std::atomic_ref<uint16_t> comp_ref(*reinterpret_cast<uint16_t*>(raw + 0x24));
    std::atomic_ref<uint16_t> phase_ref(*reinterpret_cast<uint16_t*>(raw + 0x26));

    turn_ref.store(metrics.turn_counter, std::memory_order_relaxed);
    comp_ref.store(metrics.register_compliance_q16, std::memory_order_relaxed);
    phase_ref.store(metrics.interview_phase, std::memory_order_relaxed);
}

} // namespace solorock::grammar::engine_b
