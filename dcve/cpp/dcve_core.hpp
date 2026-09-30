/**
 * @file dcve_core.hpp
 * @brief Domain Competence Verbal Engine (DCVE) C++ Real-Time Core.
 *
 * Evaluates authentic domain depth, conceptual precision, track classification,
 * and ontology grounding.
 *
 * Zero-Bridge Synchronous Memory Rule:
 *  Direct atomic store into the 64-byte AMSV State Vector (Offset 0x30).
 */

#ifndef DCVE_CORE_HPP
#define DCVE_CORE_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cmath>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::dcve {

#pragma pack(push, 8)

struct DomainCompetenceScorecard {
    float    depth_score{0.0f};
    float    precision_score{0.0f};
    float    grounding_score{0.0f};
    uint16_t track_id{0}; // 1=Engineering, 2=Finance, 3=Medical, 4=Legal, 5=Executive
    float    domain_competence_index{0.0f};
    uint16_t domain_grade{0}; // 1=Expert, 2=Proficient, 3=Surface Level, 4=Novice
};

#pragma pack(pop)

class DomainCompetenceVerbalEngine {
public:
    explicit DomainCompetenceVerbalEngine(solorock::amsv::AtomicStateVector* sv = nullptr);

    DomainCompetenceScorecard evaluate(const std::string& answer);
    void sync_to_amsv(const DomainCompetenceScorecard& sc) noexcept;

private:
    solorock::amsv::AtomicStateVector* sv_{nullptr};

    float    score_depth(const std::string& text) const;
    float    score_precision(const std::string& text) const;
    uint16_t classify_track(const std::string& text) const;
    float    score_grounding(const std::string& text) const;
};

} // namespace solorock::dcve

#endif // DCVE_CORE_HPP
