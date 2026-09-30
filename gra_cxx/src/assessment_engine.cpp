/**
 * @file assessment_engine.cpp
 * @brief Implementation of CEFR Assessment, Diagnostic Profiling & IRT Scoring Engine.
 */

#include "../include/assessment_engine.hpp"
#include <cmath>
#include <algorithm>

namespace solorock::assessment {

AssessmentEngine::AssessmentEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

CefrProficiency AssessmentEngine::score_to_cefr(float score) {
    if (score >= 90.0f) return CefrProficiency::C2;
    if (score >= 80.0f) return CefrProficiency::C1;
    if (score >= 70.0f) return CefrProficiency::B2;
    if (score >= 55.0f) return CefrProficiency::B1;
    if (score >= 40.0f) return CefrProficiency::A2;
    return CefrProficiency::A1;
}

DiagnosticEvaluationReport AssessmentEngine::evaluate_session(
    const std::vector<AssessmentItemResult>& items,
    float prior_theta
) {
    DiagnosticEvaluationReport report;
    if (items.empty()) {
        report.estimated_theta = prior_theta;
        sync_to_amsv(report);
        return report;
    }

    int correct_count = 0;
    float current_theta = prior_theta;

    for (const auto& item : items) {
        if (item.is_correct) correct_count++;

        // 2PL IRT Update Step:
        // P(theta) = 1 / (1 + exp(-a * (theta - b)))
        float z = -item.discrimination_a * (current_theta - item.difficulty_b);
        float p = 1.0f / (1.0f + std::exp(std::clamp(z, -15.0f, 15.0f)));
        float info = (item.discrimination_a * item.discrimination_a) * p * (1.0f - p);

        float u = item.is_correct ? 1.0f : 0.0f;
        float delta = (u - p) / std::max(0.15f, info);
        current_theta = std::clamp(current_theta + delta, -3.5f, 3.5f);
    }

    report.percentage_score = (static_cast<float>(correct_count) / static_cast<float>(items.size())) * 100.0f;
    report.estimated_level = score_to_cefr(report.percentage_score);
    report.estimated_theta = current_theta;
    report.standard_error = 1.0f / std::sqrt(static_cast<float>(items.size()) + 1.0f);

    report.domain_scores["morphosyntax"] = report.percentage_score * 0.01f;
    report.domain_scores["syntax_depth"] = 0.85f;
    report.domain_scores["error_suppression"] = (correct_count == items.size()) ? 1.0f : 0.70f;

    if (report.percentage_score < 70.0f) {
        report.personalized_remediation.push_back("Module CCTE-07: Subject-Verb Agreement & Concord Invariants");
        report.personalized_remediation.push_back("Module VCE-04: Clause Subordination & Case Filter Rules");
    } else {
        report.personalized_remediation.push_back("Module ADV-01: Rhetorical Device Inversion & Stylistic Register Elevation");
    }

    sync_to_amsv(report);
    return report;
}

void AssessmentEngine::sync_to_amsv(const DiagnosticEvaluationReport& report) {
    if (!amsv_) return;

    // Pack into aeee_examination_state (offset 0x28):
    // Bits 0-31: Theta (float32)
    // Bits 32-47: SEM (Q16 fixed-point)
    // Bits 48-63: CEFR level (uint16)
    union {
        float f;
        uint32_t u;
    } theta_conv;
    theta_conv.f = report.estimated_theta;

    uint16_t sem_q16 = static_cast<uint16_t>(std::clamp(report.standard_error * 65535.0f, 0.0f, 65535.0f));
    uint16_t cefr_code = static_cast<uint16_t>(report.estimated_level);

    uint64_t packed = static_cast<uint64_t>(theta_conv.u) |
                      (static_cast<uint64_t>(sem_q16) << 32) |
                      (static_cast<uint64_t>(cefr_code) << 48);

    amsv_->state_vector.aeee_examination_state.store(packed);
}

} // namespace solorock::assessment
