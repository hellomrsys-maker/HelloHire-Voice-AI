/**
 * @file linguistic_engine.hpp
 * @brief Linguistic Reasoning, Universal Grammar Validation, and Error Detection Engine (C++20 Core).
 *
 * Implements first-principles syntactic analysis (X-Bar Schema, EPP, Case Filter,
 * Theta Criterion, Binding Theory), clause typology classification, and real-time
 * error detection across 16+ grammatical error classes.
 */

#ifndef GRA_CXX_LINGUISTIC_ENGINE_HPP
#define GRA_CXX_LINGUISTIC_ENGINE_HPP

#include <string>
#include <vector>
#include <memory>
#include <algorithm>
#include <regex>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::linguistics {

enum class ClauseType {
    Simple,
    Compound,
    Complex,
    CompoundComplex,
    Cleft,
    Inverted,
    Nominalized
};

struct LinguisticAnalysisReport {
    ClauseType clause_type{ClauseType::Simple};
    int syntactic_tree_depth{1};
    bool is_grammatically_valid{true};
    float structural_complexity_score{0.5f};
    std::vector<std::string> detected_errors;
    std::string universal_grammar_explanation;
};

class LinguisticEngine {
public:
    explicit LinguisticEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~LinguisticEngine() = default;

    /// Full multi-level syntactic and grammatical analysis of a sentence
    LinguisticAnalysisReport analyze_sentence(const std::string& utterance);

    /// Validates sentence against Universal Grammar invariants (EPP, Case, Theta, Binding)
    std::string generate_ug_proof(const std::string& sentence, bool has_subject, bool has_verb, bool agreement_ok);

    /// Scans text for 16+ error classes (Agreement, Stative Aspect, Dangling Modifiers, etc.)
    std::vector<std::string> scan_errors(const std::string& utterance);

    /// Synchronizes diagnostic report into AMSV error_diagnostic_buffer
    void sync_to_amsv(const LinguisticAnalysisReport& report);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
    ClauseType classify_clause_structure(const std::string& sentence, int clause_count, bool has_subordinator, bool has_coordinator);
};

} // namespace solorock::linguistics

#endif // GRA_CXX_LINGUISTIC_ENGINE_HPP
