/**
 * @file assessment_engine.hpp
 * @brief CEFR Assessment, Diagnostic Profiling & IRT Scoring Engine (C++20 Core).
 *
 * Evaluates learner grammatical proficiency across CEFR levels (A1 to C2),
 * computes multi-domain skill vectors, and synchronizes IRT theta directly to AMSV.
 */

#ifndef GRA_CXX_ASSESSMENT_ENGINE_HPP
#define GRA_CXX_ASSESSMENT_ENGINE_HPP

#include <string>
#include <vector>
#include <map>
#include <memory>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::assessment {

enum class CefrProficiency {
    A1,
    A2,
    B1,
    B2,
    C1,
    C2
};

struct AssessmentItemResult {
    std::string item_id;
    bool is_correct;
    float difficulty_b;
    float discrimination_a;
    std::string target_rule;
};

struct DiagnosticEvaluationReport {
    CefrProficiency estimated_level{CefrProficiency::B1};
    float percentage_score{0.0f};
    float estimated_theta{0.0f};
    float standard_error{0.35f};
    std::map<std::string, float> domain_scores;
    std::vector<std::string> personalized_remediation;
};

class AssessmentEngine {
public:
    explicit AssessmentEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~AssessmentEngine() = default;

    /// Evaluates a battery of assessment results and produces a diagnostic profile
    DiagnosticEvaluationReport evaluate_session(
        const std::vector<AssessmentItemResult>& items,
        float prior_theta = 0.0f
    );

    /// Maps raw composite score [0..100] to CEFR proficiency
    static CefrProficiency score_to_cefr(float score);

    /// Synchronizes diagnostic evaluation state directly to AMSV offset 0x28
    void sync_to_amsv(const DiagnosticEvaluationReport& report);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
};

} // namespace solorock::assessment

#endif // GRA_CXX_ASSESSMENT_ENGINE_HPP
