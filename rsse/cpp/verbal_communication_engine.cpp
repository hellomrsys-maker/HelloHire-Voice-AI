/**
 * @file verbal_communication_engine.cpp
 * @brief Implementation of Recruitment Verbal Communication C++ Engine.
 */

#include "verbal_communication_engine.hpp"
#include <cstring>
#include <cctype>
#include <sstream>

namespace solorock::rsse {

static std::string to_lower_string(const std::string& str) {
    std::string out = str;
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c){ return std::tolower(c); });
    return out;
}

VerbalCommunicationEngine::VerbalCommunicationEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

StarMetrics VerbalCommunicationEngine::compute_star(const std::string& text) const {
    std::string lower = to_lower_string(text);

    static const std::vector<std::string> sit_cues = {
        "when i was at", "in my previous role", "the situation was", "our team was facing", "the context was"
    };
    static const std::vector<std::string> task_cues = {
        "my objective was", "i was tasked with", "the goal was to", "we needed to resolve", "my responsibility was"
    };
    static const std::vector<std::string> action_cues = {
        "i initiated", "i refactored", "i architected", "i implemented", "we deployed", "i coordinated", "i developed"
    };
    static const std::vector<std::string> result_cues = {
        "resulting in", "achieved a", "reduced latency by", "improved throughput", "which delivered", "the outcome was"
    };

    auto check_cues = [&](const std::vector<std::string>& cues) -> bool {
        for (const auto& cue : cues) {
            if (lower.find(cue) != std::string::npos) return true;
        }
        return false;
    };

    bool has_s = check_cues(sit_cues);
    bool has_t = check_cues(task_cues);
    bool has_a = check_cues(action_cues);
    bool has_r = check_cues(result_cues);

    StarMetrics m;
    m.situation_score = has_s ? 0.90f : 0.35f;
    m.task_score      = has_t ? 0.92f : 0.40f;
    m.action_score    = has_a ? 0.95f : 0.45f;
    m.result_score    = has_r ? 0.94f : 0.30f;

    uint32_t count = (has_s ? 1 : 0) + (has_t ? 1 : 0) + (has_a ? 1 : 0) + (has_r ? 1 : 0);
    switch (count) {
        case 4: m.overall_coherence = 0.98f; break;
        case 3: m.overall_coherence = 0.85f; break;
        case 2: m.overall_coherence = 0.65f; break;
        case 1: m.overall_coherence = 0.40f; break;
        default: m.overall_coherence = 0.20f; break;
    }
    return m;
}

float VerbalCommunicationEngine::compute_filler_penalty(const std::string& text) const {
    std::string lower = to_lower_string(text);
    static const std::vector<std::string> fillers = {
        " um ", " uh ", " like ", " you know ", " sort of ", " kind of ", " basically ", " literally "
    };

    uint32_t count = 0;
    for (const auto& f : fillers) {
        size_t pos = 0;
        while ((pos = lower.find(f, pos)) != std::string::npos) {
            count++;
            pos += f.length();
        }
    }

    std::stringstream ss(text);
    std::string w;
    uint32_t word_count = 0;
    while (ss >> w) word_count++;
    if (word_count == 0) word_count = 1;

    float ratio = static_cast<float>(count) / static_cast<float>(word_count);
    return std::min(0.40f, ratio * 5.0f);
}

float VerbalCommunicationEngine::compute_wpm_score(float wpm) const {
    if (wpm >= 130.0f && wpm <= 155.0f) return 1.0f;
    if (wpm >= 115.0f && wpm <= 170.0f) return 0.85f;
    if (wpm >= 90.0f && wpm <= 190.0f)  return 0.65f;
    return 0.40f;
}

VerbalEvaluationResult VerbalCommunicationEngine::evaluate_turn(
    const std::string& transcript,
    uint16_t format_code,
    float measured_wpm
) {
    VerbalEvaluationResult res;
    res.star = compute_star(transcript);
    res.filler_penalty = compute_filler_penalty(transcript);
    res.wpm_score = compute_wpm_score(measured_wpm);
    res.jargon_density = 0.88f;

    float format_weight = (format_code == 2 || format_code == 3) ? 0.50f : 0.35f;
    float base_reg = (1.0f - res.filler_penalty) * res.wpm_score;

    res.composite_verbal_score = std::clamp(
        (res.star.overall_coherence * format_weight) + (base_reg * (1.0f - format_weight)),
        0.10f, 1.0f
    );
    res.register_compliance = std::clamp(base_reg - res.filler_penalty, 0.10f, 1.0f);
    res.pass_threshold = res.composite_verbal_score >= 0.70f;

    return res;
}

void VerbalCommunicationEngine::sync_to_amsv(
    uint16_t scenario_id,
    uint16_t turn,
    float compliance,
    uint16_t phase
) noexcept {
    if (!amsv_) return;

    uint16_t comp_q16 = static_cast<uint16_t>(std::clamp(compliance, 0.0f, 1.0f) * 65535.0f);
    uint64_t word = static_cast<uint64_t>(scenario_id)
                  | (static_cast<uint64_t>(turn) << 16)
                  | (static_cast<uint64_t>(comp_q16) << 32)
                  | (static_cast<uint64_t>(phase) << 48);

    // Direct atomic write to Offset 0x20 without locks or sockets
    amsv_->state_vector.rsse_scenario_state.store(word, std::memory_order_release);
}

} // namespace solorock::rsse

extern "C" {
int32_t rsse_cpp_evaluate_verbal(
    const char* transcript,
    uint16_t format_code,
    float wpm,
    solorock::rsse::VerbalEvaluationResult* out_result
) {
    if (!transcript || !out_result) return -1;
    solorock::rsse::VerbalCommunicationEngine engine(nullptr);
    *out_result = engine.evaluate_turn(std::string(transcript), format_code, wpm);
    return 0;
}
}
