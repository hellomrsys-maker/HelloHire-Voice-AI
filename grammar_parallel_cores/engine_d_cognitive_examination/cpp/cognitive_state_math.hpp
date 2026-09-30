/**
 * cognitive_state_math.hpp - Engine D Sub-Core D3 (C++20)
 * Cognitive Capabilities & Adaptive Examination Engine: Fast cognitive state tracking,
 * IRT 3PL ability estimation, and zero-bridge AMSV Offsets 0x10-0x1F & 0x28-0x2F synchronization.
 */

#pragma once

#include <cstdint>
#include <array>

namespace solorock::grammar::engine_d {

struct CognitiveStateMetrics {
    std::array<uint16_t, 8> cognitive_scores_q16;
    float irt_theta;
    uint16_t standard_error_measurement_q16;
    uint16_t question_index;
};

class CognitiveStateMathEngine {
public:
    CognitiveStateMathEngine() noexcept = default;

    CognitiveStateMetrics compute_cognitive_metrics(
        const std::array<float, 8>& scores,
        float prior_theta,
        uint16_t question_idx
    ) noexcept;

    void sync_to_amsv(void* amsv_base_ptr, const CognitiveStateMetrics& metrics) noexcept;
};

} // namespace solorock::grammar::engine_d
