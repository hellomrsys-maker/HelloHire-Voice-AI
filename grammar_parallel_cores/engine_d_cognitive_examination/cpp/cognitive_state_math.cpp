/**
 * cognitive_state_math.cpp - Engine D Sub-Core D3 (C++20)
 * Implementation of cognitive state math and lock-free AMSV synchronization.
 */

#include "cognitive_state_math.hpp"
#include <algorithm>
#include <atomic>
#include <cstring>

namespace solorock::grammar::engine_d {

CognitiveStateMetrics CognitiveStateMathEngine::compute_cognitive_metrics(
    const std::array<float, 8>& scores,
    float prior_theta,
    uint16_t question_idx
) noexcept {
    CognitiveStateMetrics m{};
    float sum_scores = 0.0f;

    for (size_t i = 0; i < 8; ++i) {
        float s = std::clamp(scores[i], 0.0f, 1.0f);
        m.cognitive_scores_q16[i] = static_cast<uint16_t>(s * 65535.0f);
        sum_scores += s;
    }

    float mean_score = sum_scores / 8.0f;
    float current_theta = (mean_score - 0.5f) * 6.0f;
    // Smoothed theta update
    m.irt_theta = 0.7f * prior_theta + 0.3f * current_theta;

    // SEM decreases as questions increase: SEM = 1 / sqrt(I(theta))
    float sem = 1.0f / std::sqrt(1.0f + question_idx * 0.5f);
    m.standard_error_measurement_q16 = static_cast<uint16_t>(std::clamp(sem, 0.0f, 1.0f) * 65535.0f);
    m.question_index = question_idx;

    return m;
}

void CognitiveStateMathEngine::sync_to_amsv(void* amsv_base_ptr, const CognitiveStateMetrics& metrics) noexcept {
    if (!amsv_base_ptr) return;

    uint8_t* raw = static_cast<uint8_t*>(amsv_base_ptr);

    // Direct physical write to Offset 0x10 - 0x17 (ccte_cog_bank_alpha: Thinking, Focus, Memory, Creative)
    // and Offset 0x18 - 0x1F (ccte_cog_bank_beta: Imagination, Analytical, Verbal, Emotional)
    for (size_t i = 0; i < 8; ++i) {
        size_t offset = 0x10 + i * 2;
        std::atomic_ref<uint16_t> score_ref(*reinterpret_cast<uint16_t*>(raw + offset));
        score_ref.store(metrics.cognitive_scores_q16[i], std::memory_order_relaxed);
    }

    // Direct physical write to Offset 0x28 - 0x2F (aeee_examination_state):
    // Offset 0x28: IRT Ability Theta (IEEE 754 float32)
    // Offset 0x2C: SEM Q16 (uint16_t)
    // Offset 0x2E: Question Index (uint16_t)
    std::atomic_ref<uint32_t> theta_ref(*reinterpret_cast<uint32_t*>(raw + 0x28));
    uint32_t theta_bits;
    std::memcpy(&theta_bits, &metrics.irt_theta, sizeof(float));
    theta_ref.store(theta_bits, std::memory_order_relaxed);

    std::atomic_ref<uint16_t> sem_ref(*reinterpret_cast<uint16_t*>(raw + 0x2C));
    sem_ref.store(metrics.standard_error_measurement_q16, std::memory_order_relaxed);

    std::atomic_ref<uint16_t> q_ref(*reinterpret_cast<uint16_t*>(raw + 0x2E));
    q_ref.store(metrics.question_index, std::memory_order_relaxed);
}

} // namespace solorock::grammar::engine_d
