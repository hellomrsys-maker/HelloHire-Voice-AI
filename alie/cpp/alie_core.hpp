/**
 * @file alie_core.hpp
 * @brief Active Listening Intelligence Engine (ALIE) C++ Real-Time Core.
 *
 * Evaluates whether the candidate is genuinely listening and responding to the
 * interviewer, vs. delivering pre-rehearsed generic responses.
 *
 * Five core metrics:
 *  1. Referential Pronoun Alignment  — echo-back of the interviewer's framing
 *  2. Question-Answer Relevance Score — direct topical match of answer to question
 *  3. Latency-to-Insight Gap          — time before first on-topic word
 *  4. Discourse Repair Signals        — "Could you clarify…", "Did you mean…"
 *  5. Co-referential Cross-Turn Track — later turns correctly reference earlier entities
 *
 * Zero-Bridge Synchronous Memory Rule: direct 0-nanosecond atomic stores into
 * the 64-byte AMSV State Vector (Offset 0x20 rsse_scenario_state repurposed for ALIE).
 */

#ifndef ALIE_CORE_HPP
#define ALIE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::alie {

#pragma pack(push, 8)

struct ReferentialAlignmentMetrics {
    float pronoun_echo_rate{0.0f};       // 0-1: how often interviewer framing is echoed
    float lexical_mirror_score{0.0f};    // 0-1: shared vocabulary with question
    float topic_frame_retention{0.0f};   // 0-1: retaining question's conceptual frame
    float composite_score{0.0f};
};

struct QARelevanceMetrics {
    float on_topic_ratio{0.0f};          // 0-1: fraction of answer tokens relevant to question
    float answer_completeness{0.0f};     // 0-1: all sub-questions addressed
    float specificity_score{0.0f};       // 0-1: concrete vs. vague response
    float composite_score{0.0f};
};

struct DiscourseRepairMetrics {
    int   repair_attempts{0};            // count of clarification requests
    float repair_appropriateness{0.0f};  // were repairs contextually justified?
    float comprehension_signal_rate{0.0f};
    float composite_score{0.0f};
};

struct CoReferenceMetrics {
    int   entities_carried_forward{0};   // entities from history re-used correctly
    float cross_turn_entity_fidelity{0.0f};
    float narrative_continuity_score{0.0f};
    float composite_score{0.0f};
};

struct ListeningIntelligenceScorecard {
    ReferentialAlignmentMetrics alignment{};
    QARelevanceMetrics          qa_relevance{};
    float                       latency_to_insight_ms{250.0f};
    float                       latency_score{1.0f};
    DiscourseRepairMetrics      discourse_repair{};
    CoReferenceMetrics          co_reference{};
    float                       global_listening_index{0.0f};
    uint16_t                    listening_grade{0}; // 1=Active, 2=Adequate, 3=Passive, 4=Disengaged
};

#pragma pack(pop)

class ActiveListeningIntelligenceEngine {
public:
    explicit ActiveListeningIntelligenceEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    ListeningIntelligenceScorecard evaluate(
        const std::string& question,
        const std::string& answer,
        const std::vector<std::string>& history,
        float latency_ms,
        uint16_t turn
    );

    void sync_to_amsv(const ListeningIntelligenceScorecard& sc, uint16_t turn) noexcept;
    [[nodiscard]] solorock::amsv::AtomicStateVector* get_amsv() const noexcept { return sv_; }

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    ReferentialAlignmentMetrics compute_alignment(const std::string& q, const std::string& a) const;
    QARelevanceMetrics          compute_relevance(const std::string& q, const std::string& a) const;
    float                       compute_latency_score(float latency_ms) const;
    DiscourseRepairMetrics      compute_repair(const std::string& a) const;
    CoReferenceMetrics          compute_coreference(const std::string& a, const std::vector<std::string>& history) const;
};

} // namespace solorock::alie

extern "C" {
    int32_t alie_cpp_evaluate(
        const char* question,
        const char* answer,
        float latency_ms,
        uint16_t turn,
        solorock::alie::ListeningIntelligenceScorecard* out
    );
}

#endif // ALIE_CORE_HPP
