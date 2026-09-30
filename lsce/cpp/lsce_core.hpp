/**
 * @file lsce_core.hpp
 * @brief Long-Short Cognitive Endurance Engine (LSCE) C++ Real-Time Core.
 *
 * Evaluates cognitive stamina, performance trajectory, lexical diversity drift,
 * and concentration resilience across extended interviews.
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x3C).
 */

#ifndef LSCE_CORE_HPP
#define LSCE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::lsce {

#pragma pack(push, 8)

struct EnduranceScorecard {
    float    stamina_score{1.0f};
    float    lexical_richness{0.8f};
    float    resilience_score{0.8f};
    float    recovery_score{0.8f};
    float    endurance_index{0.0f};
    uint16_t endurance_grade{0}; // 1=Ironclad, 2=Resilient, 3=Mild Fatigue, 4=Exhausted
};

#pragma pack(pop)

class CognitiveEnduranceEngine {
public:
    explicit CognitiveEnduranceEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    EnduranceScorecard evaluate(const std::string& question, const std::string& answer, uint16_t turn = 1);
    void sync_to_amsv(const EnduranceScorecard& sc) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    float score_lexical(const std::string& text) const;
    float score_concentration(const std::string& q, const std::string& a) const;
};

} // namespace solorock::lsce

#endif // LSCE_CORE_HPP
