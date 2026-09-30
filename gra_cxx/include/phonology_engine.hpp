/**
 * @file phonology_engine.hpp
 * @brief Phonology, Pronunciation Invariants & Stress Shift Engine (C++20 Core).
 *
 * Implements trochaic/iambic stress shift verification, acoustic formant tracking,
 * and connected speech elision analysis.
 */

#ifndef GRA_CXX_PHONOLOGY_ENGINE_HPP
#define GRA_CXX_PHONOLOGY_ENGINE_HPP

#include <string>
#include <vector>
#include <memory>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::phonology {

enum class LexicalCategory {
    Noun,
    Verb,
    Adjective
};

struct PhonologicalAnalysisReport {
    std::string ipa_transcription;
    bool has_stress_shift{false};
    std::string primary_stress_syllable;
    std::vector<std::string> connected_speech_effects;
    float phonetic_precision_score{0.92f};
};

class PhonologyEngine {
public:
    explicit PhonologyEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~PhonologyEngine() = default;

    /// Analyzes pronunciation, stress placement, and connected speech phenomena
    PhonologicalAnalysisReport analyze_utterance(
        const std::string& text,
        LexicalCategory category = LexicalCategory::Noun
    );

    /// Synchronizes phonetic state directly to AMSV vce_phoneme_state (offset 0x00)
    void sync_to_amsv(const PhonologicalAnalysisReport& report);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
};

} // namespace solorock::phonology

#endif // GRA_CXX_PHONOLOGY_ENGINE_HPP
