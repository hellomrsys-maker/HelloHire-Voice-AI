/**
 * @file pace_core.hpp
 * @brief Pacing & Adaptation Calibration Engine (PACE) C++ Real-Time Core.
 *
 * Evaluates candidate behavioral adaptation to interviewer cues:
 *  - Vocabulary complexity compliance (simplification vs technical deep dive)
 *  - Response length modulation (brevity vs elaboration)
 *  - Register matching (formal vs casual)
 *  - Interruption composure & redirection handling
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x3E).
 */

#ifndef PACE_CORE_HPP
#define PACE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::pace {

#pragma pack(push, 8)

struct PacingScorecard {
    float    vocab_compliance{0.8f};
    float    length_compliance{0.8f};
    float    register_match{0.8f};
    float    composure_score{0.8f};
    float    adaptation_index{0.0f};
    uint16_t pacing_grade{0}; // 1=Seamless, 2=Adaptive, 3=Rigid, 4=Oblivious
};

#pragma pack(pop)

class PacingAdaptationEngine {
public:
    explicit PacingAdaptationEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    PacingScorecard evaluate(const std::string& prompt, const std::string& response);
    void sync_to_amsv(const PacingScorecard& sc) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    float score_vocab_adaptation(const std::string& prompt, const std::string& resp) const;
    float score_length(const std::string& prompt, const std::string& resp) const;
};

} // namespace solorock::pace

#endif // PACE_CORE_HPP
