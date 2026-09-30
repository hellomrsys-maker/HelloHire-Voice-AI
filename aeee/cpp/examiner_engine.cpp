/**
 * @file examiner_engine.cpp
 * @brief AI Examiner & Adaptive Examination Engine (AEEE) C++ Implementation.
 */

#include "examiner_engine.hpp"
#include <cmath>
#include <cstring>
#include <algorithm>

namespace solorock::aeee {

ExaminerEngine::ExaminerEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {
    if (amsv_) {
        sync_to_amsv();
    }
}

void ExaminerEngine::start_examination(uint16_t max_questions, float target_sem) {
    session_.question_index = 0;
    session_.max_questions = max_questions;
    session_.current_theta = 0.0f; // Prior mean = 0.0 (standardized ability scale)
    session_.standard_error = 1.0f; // Prior standard deviation = 1.0
    session_.target_sem_threshold = target_sem;
    session_.exam_completed = false;
    session_.latest_scores = RubricScores{};

    administered_difficulties_.clear();
    administered_responses_.clear();

    if (amsv_) {
        std::memset(amsv_->examiner_question_buffer, 0, sizeof(amsv_->examiner_question_buffer));
        sync_to_amsv();
    }
}

void ExaminerEngine::submit_turn_evaluation(
    const RubricScores& scores,
    float item_difficulty,
    float item_discrimination
) {
    session_.latest_scores = scores;
    session_.question_index++;

    float composite = scores.composite_score();
    administered_difficulties_.push_back(item_difficulty);
    administered_responses_.push_back(composite);

    update_ability_estimate(composite, item_difficulty, item_discrimination);

    if (check_stopping_rule()) {
        session_.exam_completed = true;
    }

    sync_to_amsv();
}

void ExaminerEngine::update_ability_estimate(
    float response_quality,
    float item_difficulty,
    float item_discrimination
) {
    // 2PL Logistic IRT Newton-Raphson update with Gaussian prior N(0, 1)
    // theta_new = theta + (Score_function) / (Fisher_Information + Prior_precision)
    float theta = session_.current_theta;

    float total_score_grad = 0.0f;
    float total_information = 0.0f;

    // Standard normal prior: d/d theta log p(theta) = -theta, Fisher info = 1.0
    total_score_grad -= theta;
    total_information += 1.0f;

    for (size_t i = 0; i < administered_difficulties_.size(); ++i) {
        float b = administered_difficulties_[i];
        float a = item_discrimination;
        float u = administered_responses_[i];

        float exp_term = std::exp(-a * (theta - b));
        float p = 1.0f / (1.0f + exp_term);
        p = std::clamp(p, 1e-4f, 1.0f - 1e-4f);

        total_score_grad += a * (u - p);
        total_information += (a * a) * p * (1.0f - p);
    }

    float delta_theta = total_score_grad / total_information;
    // Damping delta to avoid divergence
    delta_theta = std::clamp(delta_theta, -0.75f, 0.75f);

    session_.current_theta = std::clamp(theta + delta_theta, -3.5f, 3.5f);
    session_.standard_error = 1.0f / std::sqrt(total_information);
}

bool ExaminerEngine::check_stopping_rule() const noexcept {
    if (session_.question_index >= session_.max_questions) {
        return true;
    }
    // Stopping criterion: SEM <= threshold after at least 3 questions
    if (session_.question_index >= 3 && session_.standard_error <= session_.target_sem_threshold) {
        return true;
    }
    return false;
}

void ExaminerEngine::sync_to_amsv() noexcept {
    if (!amsv_) return;

    // Bit layout for offset 0x28 (aeee_examination_state):
    // [Bits 0-31: Theta (IEEE 754 float as uint32) | Bits 32-47: SEM Q16 | Bits 48-63: Question Index]
    uint32_t theta_bits = 0;
    static_assert(sizeof(float) == sizeof(uint32_t));
    std::memcpy(&theta_bits, &session_.current_theta, sizeof(float));

    uint16_t sem_q16 = static_cast<uint16_t>(std::clamp(session_.standard_error, 0.0f, 1.0f) * 65535.0f);
    uint16_t q_idx = session_.question_index;

    uint64_t word = static_cast<uint64_t>(theta_bits)
                  | (static_cast<uint64_t>(sem_q16) << 32)
                  | (static_cast<uint64_t>(q_idx) << 48);

    amsv_->state_vector.aeee_examination_state.store(word, std::memory_order_release);
}

} // namespace solorock::aeee
