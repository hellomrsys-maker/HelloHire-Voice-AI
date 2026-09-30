/**
 * @file ecse_core.hpp
 * @brief Emotional Communication & Social Calibration Engine (ECSE) C++ Real-Time Core.
 *
 * Evaluates bidirectional social intelligence in verbal communication:
 *  1. Affect Valence        — positive / negative / neutral emotional tone
 *  2. Rapport Building      — social bonding language, warmth signals
 *  3. Mirror Matching       — vocal rhythm & vocabulary mirroring of interviewer
 *  4. Micro-Disagreement    — hedges, silent resistance, face-saving indirectness
 *  5. Politeness Register   — formal/informal calibration, cross-cultural courtesy
 */

#ifndef ECSE_CORE_HPP
#define ECSE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::ecse {

#pragma pack(push, 8)

struct AffectValenceMetrics {
    float positive_affect{0.0f};      // Joy, enthusiasm, confidence cues
    float negative_affect{0.0f};      // Anxiety, frustration, defensiveness
    float neutral_affect{0.0f};       // Measured, clinical, information-focused
    float valence_score{0.0f};        // -1.0 (anxious/negative) to +1.0 (confident/positive)
    float composite_score{0.0f};
};

struct RapportBuildingMetrics {
    float warmth_signal_density{0.0f};  // Affirmative phrases, empathy expressions
    float shared_identity_markers{0.0f};// "We", "as a team", "together"
    float social_bonding_score{0.0f};
    float composite_score{0.0f};
};

struct MirrorMatchingMetrics {
    float vocabulary_mirror_rate{0.0f}; // How often candidate adopts interviewer's words
    float rhythm_synchrony_score{0.0f}; // Pace matching (derived from WPM comparison)
    float composite_score{0.0f};
};

struct MicroDisagreementMetrics {
    int   hedge_count{0};             // "somewhat", "in a way", "to some extent"
    float disagreement_signal{0.0f};  // 0=full agreement, 1=strong implicit resistance
    float face_saving_score{0.0f};    // Politeness despite disagreement
    float composite_score{0.0f};
};

struct PolitenessRegisterMetrics {
    float formal_compliance{1.0f};    // Professional language calibration
    float courtesy_markers{0.0f};     // Thank you, appreciate, acknowledge
    float register_appropriateness{1.0f};
    float composite_score{0.0f};
};

struct SocialCalibrationScorecard {
    AffectValenceMetrics     affect{};
    RapportBuildingMetrics   rapport{};
    MirrorMatchingMetrics    mirror{};
    MicroDisagreementMetrics micro_disagree{};
    PolitenessRegisterMetrics politeness{};
    float global_social_intelligence{0.0f};
    uint16_t social_grade{0}; // 1=Highly Attuned, 2=Calibrated, 3=Adequate, 4=Misaligned
};

#pragma pack(pop)

class EmotionalCommunicationSocialEngine {
public:
    explicit EmotionalCommunicationSocialEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    SocialCalibrationScorecard evaluate(
        const std::string& answer,
        const std::string& interviewer_last_turn,
        float candidate_wpm,
        float interviewer_wpm,
        uint16_t turn
    );

    void sync_to_amsv(const SocialCalibrationScorecard& sc, uint16_t turn) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    AffectValenceMetrics      compute_affect(const std::string& text) const;
    RapportBuildingMetrics    compute_rapport(const std::string& text) const;
    MirrorMatchingMetrics     compute_mirror(const std::string& answer, const std::string& prev_q, float c_wpm, float i_wpm) const;
    MicroDisagreementMetrics  compute_disagreement(const std::string& text) const;
    PolitenessRegisterMetrics compute_politeness(const std::string& text) const;
};

} // namespace solorock::ecse

extern "C" {
    int32_t ecse_cpp_evaluate(
        const char* answer,
        const char* interviewer_turn,
        float candidate_wpm,
        float interviewer_wpm,
        uint16_t turn,
        solorock::ecse::SocialCalibrationScorecard* out
    );
}

#endif // ECSE_CORE_HPP
