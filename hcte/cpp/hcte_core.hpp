/**
 * @file hcte_core.hpp
 * @brief Human Cognitive Thinking Engine (HCTE) C++ Real-Time Core.
 *
 * Implements real-time C++ persona synthesis across 11 cognitive styles:
 *  - Optimist, Pessimist, Pre-Mortem (2x weight), Devil's Advocate
 *  - Analyst, Intuitive, Empath, Systems Thinker
 *  - Visionary, Absurdist, Metacognition Monitor
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x38 maio_global_state_beta).
 */

#ifndef HCTE_CORE_HPP
#define HCTE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::hcte {

#pragma pack(push, 8)

struct CognitiveScorecard {
    float optimism_charge{0.0f};
    float pessimism_index{0.0f};
    float premortem_rpn_norm{0.0f};
    float solution_density{0.0f};
    float devils_advocate_score{0.0f};
    float analyst_score{0.0f};
    float systems_score{0.0f};
    float cognitive_tension{0.0f};
    float global_cognitive_index{0.0f};
    uint16_t cognitive_grade{0}; // 1=Highly Insightful, 2=Insightful, 3=Adequate, 4=Shallow
};

#pragma pack(pop)

class HumanCognitiveThinkingEngine {
public:
    explicit HumanCognitiveThinkingEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    CognitiveScorecard evaluate(const std::string& scenario);
    void sync_to_amsv(const CognitiveScorecard& sc) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    float score_optimism(const std::string& text) const;
    float score_pessimism(const std::string& text) const;
    void  score_premortem(const std::string& text, float& rpn, float& solutions) const;
    float score_systems(const std::string& text) const;
    float score_tension(float optimism, float pessimism) const;
};

} // namespace solorock::hcte

#endif // HCTE_CORE_HPP
