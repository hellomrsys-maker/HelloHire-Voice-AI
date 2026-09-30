/**
 * @file rvce_core.hpp
 * @brief Recruitment Verbal Cognitive Engine (RVCE) C++ Real-Time Core.
 *
 * Implements microsecond deterministic candidate speech & cognition evaluation:
 * 1. Thinking Ability (Reasoning depth, MECE structuring, First-Principles, STAR coherence)
 * 2. Concentrating Functioning (Sustained focus, distraction resistance, cognitive endurance)
 * 3. Recalling Ability (Working memory capacity, factual consistency, resume anchoring)
 * 4. Creativity & Out-of-the-Box Thinking (Divergent ideation, conceptual distance, lateral synthesis)
 * 5. Imagination (Counterfactual forecasting, prospective simulation, theory of mind)
 * 6. Verbal Articulation (Fluency, register compliance, professional vocabulary, zero-filler clarity)
 *
 * Adheres strictly to the Zero-Bridge Synchronous Memory Rule: Direct 0-nanosecond
 * hardware writes into the 64-byte Atomic Memory State Vector (AMSV).
 */

#ifndef RVCE_CORE_HPP
#define RVCE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include <numeric>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::rvce {

#pragma pack(push, 8)

struct ThinkingMetrics {
    int   reasoning_depth{1};              // 1 - 10 scale
    float first_principles_score{0.0f};   // 0.0 - 1.0
    float mece_structuring_score{0.0f};   // 0.0 - 1.0 (Mutually Exclusive, Collectively Exhaustive)
    float star_coherence{0.0f};           // 0.0 - 1.0 (Situation, Task, Action, Result)
    float deductive_validity{0.0f};       // 0.0 - 1.0
    float composite_score{0.0f};          // 0.0 - 1.0
};

struct ConcentrationMetrics {
    float sustained_attention_sec{0.0f};   // Continuous focus duration
    float distraction_resistance{1.0f};    // Resilience against interruption/noise
    float cognitive_endurance_factor{1.0f};// Stability over elapsed interview turns
    float noise_suppression_snr_db{18.0f}; // Effective cognitive SNR in dB
    float composite_score{0.0f};           // 0.0 - 1.0
};

struct RecallMetrics {
    float working_memory_retention{0.0f};  // Cross-turn fact retention
    float cross_turn_consistency{1.0f};    // Absence of contradictory statements
    float resume_fact_fidelity{1.0f};      // Alignment with claimed background
    float retrieval_latency_ms{120.0f};    // Working memory access latency
    float composite_score{0.0f};           // 0.0 - 1.0
};

struct CreativityMetrics {
    float divergent_thinking_score{0.0f};  // Number & breadth of alternative solutions
    float conceptual_distance_novelty{0.0f};// Semantic gap in conceptual combinations
    float lateral_solution_synthesis{0.0f};// Out-of-the-box cross-domain transfer
    float metaphoric_richness{0.0f};       // Expressive analogical reasoning
    float composite_score{0.0f};           // 0.0 - 1.0
};

struct ImaginationMetrics {
    float counterfactual_simulation{0.0f}; // "What-if" reasoning depth
    float prospective_forecasting{0.0f};   // Forward timeline scenario projection
    float theory_of_mind_empathy{0.0f};    // Stakeholder perspective modeling
    float vision_articulation_clarity{0.0f};// Strategic future-state communication
    float composite_score{0.0f};           // 0.0 - 1.0
};

struct VerbalArticulationMetrics {
    float fluency_wpm_score{1.0f};         // Optimum: 130 - 165 words per minute
    float register_compliance{1.0f};       // Professional executive linguistic register
    float vocabulary_density{0.0f};        // Type-Token Ratio & technical lexicon
    float filler_penalty{0.0f};            // Penalty for "um", "like", "sort of"
    float composite_score{0.0f};           // 0.0 - 1.0
};

struct CandidateScorecard {
    ThinkingMetrics           thinking{};
    ConcentrationMetrics      concentration{};
    RecallMetrics             recall{};
    CreativityMetrics         creativity{};
    ImaginationMetrics        imagination{};
    VerbalArticulationMetrics verbal{};
    float                     global_hireability_index{0.0f};
    uint16_t                  recommendation_code{0}; // 1=Strong Hire, 2=Hire, 3=Leaning Hire, 4=No Hire
};

#pragma pack(pop)

class RecruitmentVerbalCognitiveEngine {
public:
    explicit RecruitmentVerbalCognitiveEngine(solorock::amsv::AtomicStateVector* state_vector = nullptr);
    ~RecruitmentVerbalCognitiveEngine() = default;

    /// Evaluates a single candidate verbal turn across all 6 cognitive faculties
    CandidateScorecard evaluate_candidate_turn(
        const std::string& transcript,
        const std::vector<std::string>& conversation_history,
        float measured_wpm,
        float elapsed_interview_minutes,
        uint16_t active_turn
    );

    /// Synchronizes cognitive scores directly to the 64-byte AMSV State Vector (0-ns Zero-Bridge)
    void sync_to_amsv(const CandidateScorecard& scorecard, uint16_t scenario_id, uint16_t turn) noexcept;

    /// Returns the live AMSV pointer
    [[nodiscard]] solorock::amsv::AtomicStateVector* get_amsv() const noexcept { return state_vector_; }

private:
    solorock::amsv::AtomicStateVector* state_vector_{nullptr};

    ThinkingMetrics           compute_thinking(const std::string& text) const;
    ConcentrationMetrics      compute_concentration(float wpm, float elapsed_minutes, uint16_t turn) const;
    RecallMetrics             compute_recall(const std::string& text, const std::vector<std::string>& history) const;
    CreativityMetrics         compute_creativity(const std::string& text) const;
    ImaginationMetrics        compute_imagination(const std::string& text) const;
    VerbalArticulationMetrics compute_verbal(const std::string& text, float wpm) const;
};

} // namespace solorock::rvce

// C-ABI Exports for zero-overhead linkage
extern "C" {
    int32_t rvce_cpp_evaluate_turn(
        const char* transcript,
        float wpm,
        float elapsed_minutes,
        uint16_t turn,
        solorock::rvce::CandidateScorecard* out_scorecard
    );

    void rvce_cpp_sync_amsv(
        void* amsv_state_vector_ptr,
        const solorock::rvce::CandidateScorecard* scorecard,
        uint16_t scenario_id,
        uint16_t turn
    );
}

#endif // RVCE_CORE_HPP
