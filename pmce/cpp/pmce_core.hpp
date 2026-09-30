/**
 * @file pmce_core.hpp
 * @brief Persuasion & Message Construction Engine (PMCE) C++ Real-Time Core.
 *
 * Evaluates argumentative and rhetorical architecture across 5 classical dimensions:
 *  1. Logos  — Logical argument validity, evidence chain, syllogism quality
 *  2. Ethos  — Speaker credibility signaling, expertise anchoring
 *  3. Pathos — Emotional resonance, audience appeal, empathic framing
 *  4. Kairos — Timing and situational appropriateness of key message delivery
 *  5. CTA    — Call-to-Action: directional, decisive closing with clear proposal
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x28).
 */

#ifndef PMCE_CORE_HPP
#define PMCE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::pmce {

#pragma pack(push, 8)

struct LogosMetrics {
    int   logic_connectors{0};
    int   fallacy_count{0};
    bool  data_backed{false};
    float composite_score{0.0f};
};

struct EthosMetrics {
    int   credential_signals{0};
    int   expertise_markers{0};
    float composite_score{0.0f};
};

struct PathosMetrics {
    int   emotional_cues{0};
    int   empathy_cues{0};
    float composite_score{0.0f};
};

struct KairosMetrics {
    int   transition_cues{0};
    int   context_anchors{0};
    float composite_score{0.0f};
};

struct CTAMetrics {
    int   strong_cta_signals{0};
    int   weak_ending_count{0};
    float composite_score{0.0f};
};

struct PersuasionScorecard {
    LogosMetrics  logos{};
    EthosMetrics  ethos{};
    PathosMetrics pathos{};
    KairosMetrics kairos{};
    CTAMetrics    cta{};
    float         global_persuasion_index{0.0f};
    uint16_t      persuasion_grade{0}; // 1=Highly Persuasive, 2=Persuasive, 3=Adequate, 4=Weak
};

#pragma pack(pop)

class PersuasionMessageConstructionEngine {
public:
    explicit PersuasionMessageConstructionEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    PersuasionScorecard evaluate(const std::string& text, uint16_t turn = 1);
    void sync_to_amsv(const PersuasionScorecard& sc, uint16_t turn) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    LogosMetrics  compute_logos(const std::string& text) const;
    EthosMetrics  compute_ethos(const std::string& text) const;
    PathosMetrics compute_pathos(const std::string& text) const;
    KairosMetrics compute_kairos(const std::string& text, uint16_t turn) const;
    CTAMetrics    compute_cta(const std::string& text) const;
};

} // namespace solorock::pmce

#endif // PMCE_CORE_HPP
