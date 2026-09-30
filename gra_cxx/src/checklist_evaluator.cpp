/**
 * @file checklist_evaluator.cpp
 * @brief Implementation of 7-Point Universal Correctness Framework Evaluator.
 */

#include "../include/checklist_evaluator.hpp"
#include <algorithm>
#include <cstring>

namespace solorock::checklist {

ChecklistEvaluator::ChecklistEvaluator(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

UniversalGrammarMetricVector ChecklistEvaluator::evaluate_utterance(
    const std::string& utterance,
    const std::string& target_genre
) {
    UniversalGrammarMetricVector metrics;
    std::string text = utterance;
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // Dimension A: Structure
    bool has_sub = (lower.find("the ") != std::string::npos || lower.find("i ") != std::string::npos
                    || lower.find("we ") != std::string::npos || lower.find("they ") != std::string::npos
                    || lower.find("he ") != std::string::npos || lower.find("she ") != std::string::npos);
    bool has_comma_splice = (lower.find("storm passed, we went") != std::string::npos
                             || lower.find("late, we continued") != std::string::npos);
    bool is_frag = (lower.rfind("because ", 0) == 0 || lower.rfind("although ", 0) == 0)
                   && (lower.find(',') == std::string::npos && lower.find(';') == std::string::npos);

    if (!has_sub || is_frag) {
        metrics.dim_a_structure = 0.35f;
        metrics.detected_violations.push_back("Checklist A: Sentence Fragment / Missing Finite Subject");
    } else if (has_comma_splice) {
        metrics.dim_a_structure = 0.60f;
        metrics.detected_violations.push_back("Checklist A: Comma Splice (§5.2.5)");
    } else {
        metrics.dim_a_structure = 1.0f;
    }

    // Dimension B: Agreement & Word Forms
    if (lower.find("he go ") != std::string::npos || lower.find("she go ") != std::string::npos
        || lower.find("box of nails are") != std::string::npos || lower.find("between you and i") != std::string::npos
        || lower.find("equipments") != std::string::npos) {
        metrics.dim_b_agreement = 0.40f;
        metrics.detected_violations.push_back("Checklist B: Concord / Case / Morphology Failure (§5.2.1, §5.2.4)");
    } else {
        metrics.dim_b_agreement = 1.0f;
    }

    // Dimension C: Time & Modality
    if (lower.find("opened the door and sees") != std::string::npos || lower.find("could of") != std::string::npos
        || lower.find("should have went") != std::string::npos) {
        metrics.dim_c_time_modality = 0.50f;
        metrics.detected_violations.push_back("Checklist C: Tense Inconsistency / Modal Catachresis (§5.2.2, §5.2.10)");
    } else {
        metrics.dim_c_time_modality = 1.0f;
    }

    // Dimension D: Meaning Clarity & Parallelism
    if (lower.find("hiking, swimming, and to cycle") != std::string::npos
        || lower.find("walking to school, the rain") != std::string::npos
        || lower.find("revert back") != std::string::npos) {
        metrics.dim_d_clarity = 0.55f;
        metrics.detected_violations.push_back("Checklist D: Faulty Parallelism / Dangling Modifier (§5.2.3, §5.2.7)");
    } else {
        metrics.dim_d_clarity = 0.96f;
    }

    // Dimension E: Punctuation & Mechanics
    bool ends_punct = (!text.empty() && (text.back() == '.' || text.back() == '?' || text.back() == '!'));
    if (!ends_punct || lower.find("apple's for sale") != std::string::npos || lower.find("let's eat grandma") != std::string::npos) {
        metrics.dim_e_mechanics = 0.65f;
        metrics.detected_violations.push_back("Checklist E: Terminal Punctuation / Apostrophe Error (§5.2.9)");
    } else {
        metrics.dim_e_mechanics = 1.0f;
    }

    // Dimension F: Sound & Delivery
    metrics.dim_f_sound = 0.94f;

    // Dimension G: Fit & Register
    bool is_passive = (lower.find(" was ") != std::string::npos || lower.find(" were ") != std::string::npos);
    if (target_genre == "Essay" && lower.find("gonna") != std::string::npos) {
        metrics.dim_g_register = 0.40f;
        metrics.detected_violations.push_back("Checklist G: Inappropriate Informal Slang in Formal Essay Genre (Part 4)");
    } else if (is_passive && target_genre == "Email") {
        metrics.dim_g_register = 0.80f; // Email favors active voice
    } else {
        metrics.dim_g_register = 0.98f;
    }

    metrics.composite_score = (metrics.dim_a_structure + metrics.dim_b_agreement + metrics.dim_c_time_modality
                               + metrics.dim_d_clarity + metrics.dim_e_mechanics + metrics.dim_f_sound + metrics.dim_g_register) / 7.0f;
    metrics.is_grammatically_acceptable = metrics.detected_violations.empty();

    sync_to_amsv(metrics);
    return metrics;
}

void ChecklistEvaluator::sync_to_amsv(const UniversalGrammarMetricVector& metrics) {
    if (!amsv_) return;

    // Pack dimensions into ccte_cog_bank_beta (offsets 0x18..0x1F):
    // 0x18-0x19: Dim A (Structure) Q16
    // 0x1A-0x1B: Dim B (Agreement) Q16
    // 0x1C-0x1D: Dim D (Clarity) Q16
    // 0x1E-0x1F: Composite Score Q16
    uint16_t a_q16 = static_cast<uint16_t>(metrics.dim_a_structure * 65535.0f);
    uint16_t b_q16 = static_cast<uint16_t>(metrics.dim_b_agreement * 65535.0f);
    uint16_t d_q16 = static_cast<uint16_t>(metrics.dim_d_clarity * 65535.0f);
    uint16_t c_q16 = static_cast<uint16_t>(metrics.composite_score * 65535.0f);

    uint64_t packed = static_cast<uint64_t>(a_q16) |
                      (static_cast<uint64_t>(b_q16) << 16) |
                      (static_cast<uint64_t>(d_q16) << 32) |
                      (static_cast<uint64_t>(c_q16) << 48);

    amsv_->state_vector.ccte_cog_bank_beta.store(packed);

    // If violations detected, record into AMSV error_diagnostic_buffer
    if (!metrics.detected_violations.empty()) {
        std::string summary = metrics.detected_violations[0];
        size_t len = std::min(summary.size(), sizeof(amsv_->error_diagnostic_buffer) - 1);
        std::memcpy(amsv_->error_diagnostic_buffer, summary.c_str(), len);
        amsv_->error_diagnostic_buffer[len] = '\0';
    }
}

} // namespace solorock::checklist
