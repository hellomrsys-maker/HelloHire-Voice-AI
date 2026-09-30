/**
 * @file checklist_evaluator.hpp
 * @brief 7-Point Universal Correctness Framework Evaluator (C++20 Core).
 *
 * Implements the 7-point checklist defined in Part 10 of the Complete Grammar Guide:
 * - Dimension A: Structure (Complete sentence, finite verb, no fragments/run-ons)
 * - Dimension B: Agreement & Word Forms (Concord, case filter, determiners, mass/count)
 * - Dimension C: Time & Modality (Tense consistency, modal auxiliary catachresis)
 * - Dimension D: Meaning Clarity (Modifier proximity, unambiguous antecedents, parallelism)
 * - Dimension E: Punctuation & Mechanics (Terminal punctuation, introductory commas, apostrophes)
 * - Dimension F: Sound & Delivery (Stress shifts, phonological assimilation)
 * - Dimension G: Fit & Register (Active voice ratio, genre conventions: Essay, Report, Email, Letter)
 */

#ifndef GRA_CXX_CHECKLIST_EVALUATOR_HPP
#define GRA_CXX_CHECKLIST_EVALUATOR_HPP

#include <string>
#include <vector>
#include <map>
#include <memory>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::checklist {

struct UniversalGrammarMetricVector {
    float dim_a_structure{1.0f};
    float dim_b_agreement{1.0f};
    float dim_c_time_modality{1.0f};
    float dim_d_clarity{1.0f};
    float dim_e_mechanics{1.0f};
    float dim_f_sound{1.0f};
    float dim_g_register{1.0f};
    float composite_score{1.0f};
    bool is_grammatically_acceptable{true};
    std::vector<std::string> detected_violations;
};

class ChecklistEvaluator {
public:
    explicit ChecklistEvaluator(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~ChecklistEvaluator() = default;

    /// Evaluates text against the complete 7-Point Universal Correctness Framework
    UniversalGrammarMetricVector evaluate_utterance(
        const std::string& utterance,
        const std::string& target_genre = "Essay"
    );

    /// Synchronizes 7-Point checklist scores into AMSV memory
    void sync_to_amsv(const UniversalGrammarMetricVector& metrics);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
};

} // namespace solorock::checklist

#endif // GRA_CXX_CHECKLIST_EVALUATOR_HPP
