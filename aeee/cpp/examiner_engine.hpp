/**
 * @file examiner_engine.hpp
 * @brief AI Examiner & Adaptive Examination Engine (AEEE) C++ Core.
 *
 * Implements real-time multi-dimensional scoring across the 8-dimension rubric,
 * adaptive item tracking, and zero-bridge AMSV synchronization.
 */

#ifndef AEEE_EXAMINER_ENGINE_HPP
#define AEEE_EXAMINER_ENGINE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <array>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::aeee {

/**
 * 8-Dimension Holistic Scoring Rubric
 */
struct RubricScores {
    float phonetic_precision{0.0f};      // Dim 1: [0.0, 1.0] from VCE
    float prosody_fluency{0.0f};         // Dim 2: [0.0, 1.0] from VCE
    float grammatical_accuracy{0.0f};    // Dim 3: [0.0, 1.0] from Lingua Sapiens
    float structural_coherence{0.0f};    // Dim 4: [0.0, 1.0] from STAR/MECE parser
    float vocabulary_richness{0.0f};     // Dim 5: [0.0, 1.0] from RSSE register
    float analytical_depth{0.0f};        // Dim 6: [0.0, 1.0] from CCTE Analytical
    float emotional_resilience{0.0f};    // Dim 7: [0.0, 1.0] from CCTE Emotional
    float executive_presence{0.0f};      // Dim 8: [0.0, 1.0] composite impact

    [[nodiscard]] float composite_score() const noexcept {
        return (phonetic_precision * 0.10f) +
               (prosody_fluency * 0.15f) +
               (grammatical_accuracy * 0.15f) +
               (structural_coherence * 0.15f) +
               (vocabulary_richness * 0.10f) +
               (analytical_depth * 0.15f) +
               (emotional_resilience * 0.10f) +
               (executive_presence * 0.10f);
    }
};

struct ExamSessionState {
    uint16_t question_index{0};
    uint16_t max_questions{10};
    float current_theta{0.0f};         // Latent ability estimate [-3.0, +3.0]
    float standard_error{1.0f};        // SEM
    float target_sem_threshold{0.25f}; // Stopping rule criterion
    bool exam_completed{false};
    RubricScores latest_scores{};
};

class ExaminerEngine {
public:
    explicit ExaminerEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment);
    ~ExaminerEngine() = default;

    /// Initializes a new adaptive examination session
    void start_examination(uint16_t max_questions = 10, float target_sem = 0.25f);

    /// Ingests live assessment signals across all 8 dimensions
    void submit_turn_evaluation(const RubricScores& scores, float item_difficulty, float item_discrimination);

    /// Updates IRT ability estimate (theta) and standard error
    void update_ability_estimate(float response_quality, float item_difficulty, float item_discrimination);

    /// Checks if stopping rule condition is met
    [[nodiscard]] bool check_stopping_rule() const noexcept;

    /// Synchronizes current AEEE state into 64-byte AMSV state vector at offset 0x28
    void sync_to_amsv() noexcept;

    // Accessors
    [[nodiscard]] const ExamSessionState& get_session_state() const noexcept { return session_; }
    [[nodiscard]] float get_current_theta() const noexcept { return session_.current_theta; }
    [[nodiscard]] float get_standard_error() const noexcept { return session_.standard_error; }

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
    ExamSessionState session_{};
    std::vector<float> administered_difficulties_;
    std::vector<float> administered_responses_;
};

} // namespace solorock::aeee

#endif // AEEE_EXAMINER_ENGINE_HPP
