/**
 * @file verbal_communication_engine.hpp
 * @brief Recruitment Verbal Communication & STAR Evaluation Real-Time C++ Engine.
 *
 * Implements high-throughput candidate speech analysis, STAR method extraction,
 * professional vocabulary density checks, and 0-nanosecond AMSV hardware synchronization.
 */

#ifndef RSSE_VERBAL_COMMUNICATION_ENGINE_HPP
#define RSSE_VERBAL_COMMUNICATION_ENGINE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::rsse {

#pragma pack(push, 8)
struct StarMetrics {
    float situation_score{0.0f};
    float task_score{0.0f};
    float action_score{0.0f};
    float result_score{0.0f};
    float overall_coherence{0.0f};
};

struct VerbalEvaluationResult {
    float register_compliance{1.0f};
    StarMetrics star{};
    float jargon_density{0.0f};
    float wpm_score{1.0f};
    float filler_penalty{0.0f};
    float composite_verbal_score{0.0f};
    bool pass_threshold{true};
};
#pragma pack(pop)

class VerbalCommunicationEngine {
public:
    explicit VerbalCommunicationEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~VerbalCommunicationEngine() = default;

    /// Evaluates candidate transcript turn across STAR method, pacing, and jargon
    VerbalEvaluationResult evaluate_turn(const std::string& transcript, uint16_t format_code, float measured_wpm);

    /// Synchronizes verbal evaluation directly into the 64-byte AMSV State Vector (Offset 0x20)
    void sync_to_amsv(uint16_t scenario_id, uint16_t turn, float compliance, uint16_t phase) noexcept;

    /// Returns the live AMSV pointer
    [[nodiscard]] solorock::amsv::MasterSharedMemorySegment* get_amsv() const noexcept { return amsv_; }

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};

    StarMetrics compute_star(const std::string& text) const;
    float compute_filler_penalty(const std::string& text) const;
    float compute_wpm_score(float wpm) const;
};

} // namespace solorock::rsse

// C-ABI Exports
extern "C" {
    int32_t rsse_cpp_evaluate_verbal(
        const char* transcript,
        uint16_t format_code,
        float wpm,
        solorock::rsse::VerbalEvaluationResult* out_result
    );
}

#endif // RSSE_VERBAL_COMMUNICATION_ENGINE_HPP
