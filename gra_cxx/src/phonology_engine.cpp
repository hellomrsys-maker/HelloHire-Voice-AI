/**
 * @file phonology_engine.cpp
 * @brief Implementation of Phonology, Pronunciation Invariants & Stress Shift Engine.
 */

#include "../include/phonology_engine.hpp"
#include <algorithm>

namespace solorock::phonology {

PhonologyEngine::PhonologyEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

PhonologicalAnalysisReport PhonologyEngine::analyze_utterance(
    const std::string& text,
    LexicalCategory category
) {
    PhonologicalAnalysisReport report;
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // Check grammatical stress shift pair
    if (lower == "record") {
        report.has_stress_shift = true;
        if (category == LexicalCategory::Verb) {
            report.ipa_transcription = "rɪˈkɔːrd";
            report.primary_stress_syllable = "second (iambic)";
        } else {
            report.ipa_transcription = "ˈrɛk.ərd";
            report.primary_stress_syllable = "first (trochaic)";
        }
    } else if (lower == "project") {
        report.has_stress_shift = true;
        if (category == LexicalCategory::Verb) {
            report.ipa_transcription = "prəˈdʒɛkt";
            report.primary_stress_syllable = "second (iambic)";
        } else {
            report.ipa_transcription = "ˈprɒdʒ.ɛkt";
            report.primary_stress_syllable = "first (trochaic)";
        }
    } else {
        report.ipa_transcription = "/" + lower + "/";
        report.primary_stress_syllable = "penultimate";
    }

    // Connected speech phenomena
    if (lower.find("did you") != std::string::npos) {
        report.connected_speech_effects.push_back("Palatal Assimilation: /d/ + /j/ -> /dʒ/");
    }
    if (lower.find("to the") != std::string::npos) {
        report.connected_speech_effects.push_back("Vowel Reduction: /tuː/ -> /tə/");
    }

    report.phonetic_precision_score = 0.94f;
    sync_to_amsv(report);
    return report;
}

void PhonologyEngine::sync_to_amsv(const PhonologicalAnalysisReport& report) {
    if (!amsv_) return;

    // Pack into vce_phoneme_state (offset 0x00):
    // Bits 0-15: Phoneme hash
    // Bits 16-31: Articulation Accuracy (Q16 fixed-point)
    // Bits 32-63: Voicing / Stress shift flags
    uint16_t phoneme_hash = 0;
    for (char c : report.ipa_transcription) {
        phoneme_hash = (phoneme_hash * 31) + static_cast<uint16_t>(c);
    }

    uint16_t accuracy_q16 = static_cast<uint16_t>(report.phonetic_precision_score * 65535.0f);
    uint32_t flags = report.has_stress_shift ? 0x00010001 : 0x00010000;

    uint64_t packed = static_cast<uint64_t>(phoneme_hash) |
                      (static_cast<uint64_t>(accuracy_q16) << 16) |
                      (static_cast<uint64_t>(flags) << 32);

    amsv_->state_vector.vce_phoneme_state.store(packed);
}

} // namespace solorock::phonology
