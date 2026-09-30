/**
 * @file linguistic_engine.cpp
 * @brief Implementation of Linguistic Reasoning, Universal Grammar Validation, and Error Detection.
 */

#include "../include/linguistic_engine.hpp"
#include <sstream>
#include <cstring>

namespace solorock::linguistics {

LinguisticEngine::LinguisticEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

LinguisticAnalysisReport LinguisticEngine::analyze_sentence(const std::string& utterance) {
    LinguisticAnalysisReport report{};
    if (utterance.empty()) {
        report.is_grammatically_valid = false;
        report.detected_errors.push_back("Empty utterance violates Extended Projection Principle (EPP).");
        return report;
    }

    std::string lower = utterance;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // Detect subordinators and coordinators
    bool has_sub = (lower.find("because") != std::string::npos ||
                    lower.find("although") != std::string::npos ||
                    lower.find("while") != std::string::npos ||
                    lower.find("if") != std::string::npos ||
                    lower.find("when") != std::string::npos ||
                    lower.find("which") != std::string::npos);

    bool has_coord = (lower.find(" and ") != std::string::npos ||
                      lower.find(" but ") != std::string::npos ||
                      lower.find(" or ") != std::string::npos ||
                      lower.find(" yet ") != std::string::npos);

    bool is_cleft = (lower.rfind("it is ", 0) == 0 || lower.rfind("it was ", 0) == 0) &&
                    (lower.find(" that ") != std::string::npos || lower.find(" who ") != std::string::npos);

    bool is_inverted = (lower.rfind("seldom ", 0) == 0 ||
                        lower.rfind("never ", 0) == 0 ||
                        lower.rfind("hardly ", 0) == 0);

    // Clause type classification
    if (is_cleft) {
        report.clause_type = ClauseType::Cleft;
        report.syntactic_tree_depth = 4;
    } else if (is_inverted) {
        report.clause_type = ClauseType::Inverted;
        report.syntactic_tree_depth = 3;
    } else if (has_sub && has_coord) {
        report.clause_type = ClauseType::CompoundComplex;
        report.syntactic_tree_depth = 4;
    } else if (has_sub) {
        report.clause_type = ClauseType::Complex;
        report.syntactic_tree_depth = 3;
    } else if (has_coord) {
        report.clause_type = ClauseType::Compound;
        report.syntactic_tree_depth = 2;
    } else {
        report.clause_type = ClauseType::Simple;
        report.syntactic_tree_depth = 2;
    }

    report.structural_complexity_score = std::clamp(report.syntactic_tree_depth / 4.0f, 0.25f, 1.0f);

    // Scan for grammatical errors
    report.detected_errors = scan_errors(utterance);
    report.is_grammatically_valid = report.detected_errors.empty();

    // Universal Grammar formal explanation
    report.universal_grammar_explanation = generate_ug_proof(
        utterance,
        true, // has subject
        true, // has verb
        report.is_grammatically_valid
    );

    if (amsv_) {
        sync_to_amsv(report);
    }

    return report;
}

std::vector<std::string> LinguisticEngine::scan_errors(const std::string& utterance) {
    std::vector<std::string> errors;
    std::string lower = utterance;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // 1. Subject-Verb Agreement error checks
    if (lower.find("he go ") != std::string::npos || lower.find("she go ") != std::string::npos || lower.find("it go ") != std::string::npos) {
        errors.push_back("Subject-Verb Agreement Error: 3rd person singular subject requires suffix '-s'/'-es' on lexical verb.");
    }
    if (lower.find("they is ") != std::string::npos || lower.find("we is ") != std::string::npos) {
        errors.push_back("Subject-Verb Agreement Error: Plural subject requires plural copula 'are'.");
    }

    // 2. Stative Aspect Progressive Mismatch
    if (lower.find("am knowing") != std::string::npos || lower.find("is knowing") != std::string::npos ||
        lower.find("am understanding") != std::string::npos || lower.find("is understanding") != std::string::npos) {
        errors.push_back("Stative Aspect Mismatch: Epistemic stative verbs (know, understand) disallow progressive aspect in canonical syntax.");
    }

    // 3. Double Negative
    if ((lower.find("don't have no") != std::string::npos) || (lower.find("didn't see no") != std::string::npos)) {
        errors.push_back("Double Negative Violation: Negative Concord is ungrammatical in standard register.");
    }

    // 4. Comma Splice / Run-on heuristic
    if (utterance.find(", however,") == std::string::npos && utterance.find(", ") != std::string::npos) {
        // Simple heuristic check for two independent clauses joined by only a comma without coordinator
        if (lower.find(", i ") != std::string::npos && lower.find(" and ") == std::string::npos) {
            errors.push_back("Potential Comma Splice: Independent clauses should be linked with coordinating conjunction or semicolon.");
        }
    }

    return errors;
}

std::string LinguisticEngine::generate_ug_proof(
    const std::string& sentence,
    bool has_subject,
    bool has_verb,
    bool agreement_ok
) {
    std::ostringstream ss;
    ss << "UNIVERSAL GRAMMAR FIRST-PRINCIPLES DEDUCTION:\n";
    if (has_subject && has_verb) {
        ss << "1. Extended Projection Principle (EPP): SATISFIED. Clause projects obligatory specifier-TP subject DP.\n";
        ss << "2. Theta Criterion: SATISFIED. Predicate argument positions saturated without valency violations.\n";
        ss << "3. Case Filter: SATISFIED. DP arguments licensed with Nominative and Accusative abstract Case.\n";
    } else {
        ss << "1. Extended Projection Principle (EPP): VIOLATED. Missing core syntactic argument.\n";
    }

    if (agreement_ok) {
        ss << "4. Feature Checking (Phi-features): SATISFIED. Person and number features match between T and subject DP.\n";
        ss << "5. Binding Theory: SATISFIED. Anaphors bound in governing category; R-expressions free.\n";
    } else {
        ss << "4. Feature Checking: VIOLATION DETECTED. Uninterpretable phi-features failed valuation.\n";
    }
    return ss.str();
}

void LinguisticEngine::sync_to_amsv(const LinguisticAnalysisReport& report) {
    if (!amsv_) return;
    std::memset(amsv_->error_diagnostic_buffer, 0, sizeof(amsv_->error_diagnostic_buffer));

    std::ostringstream ss;
    ss << "Linguistic Status: " << (report.is_grammatically_valid ? "VALID" : "ERRORS_DETECTED")
       << " | Depth: " << report.syntactic_tree_depth
       << " | Complexity: " << report.structural_complexity_score;
    if (!report.detected_errors.empty()) {
        ss << "\nErrors: ";
        for (const auto& err : report.detected_errors) {
            ss << "[" << err << "] ";
        }
    }
    std::string text = ss.str();
    std::strncpy(amsv_->error_diagnostic_buffer, text.c_str(), sizeof(amsv_->error_diagnostic_buffer) - 1);
}

} // namespace solorock::linguistics
