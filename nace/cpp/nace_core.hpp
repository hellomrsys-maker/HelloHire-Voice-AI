/**
 * @file nace_core.hpp
 * @brief Narrative Arc & Coherence Engine (NACE) C++ Real-Time Core.
 *
 * Evaluates narrative continuity across interview turns:
 *  - Factual contradiction tracking
 *  - Theme consistency & identity stability
 *  - STAR method climax structure
 *  - Forward narrative drive & momentum
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x34).
 */

#ifndef NACE_CORE_HPP
#define NACE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::nace {

#pragma pack(push, 8)

struct NarrativeScorecard {
    float    coherence_score{1.0f};
    float    theme_stability{1.0f};
    float    climax_score{0.0f};
    float    momentum_score{0.0f};
    float    narrative_coherence_index{0.0f};
    uint16_t narrative_grade{0}; // 1=Exemplary, 2=Coherent, 3=Fragmented, 4=Contradictory
};

#pragma pack(pop)

class NarrativeArcCoherenceEngine {
public:
    explicit NarrativeArcCoherenceEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    NarrativeScorecard evaluate(const std::string& answer, uint16_t turn = 1);
    void sync_to_amsv(const NarrativeScorecard& sc) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    float score_climax(const std::string& text) const;
    float score_momentum(const std::string& text) const;
};

} // namespace solorock::nace

#endif // NACE_CORE_HPP
