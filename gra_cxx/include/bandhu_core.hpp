/**
 * @file bandhu_core.hpp
 * @brief BandhuPrime Dedicated AI Engine Architecture Core (C++20).
 *
 * Implements the core neuro-symbolic grammar verification across skills:
 * - B1: Writing Engine (Sentence completeness, punctuation, capitalization)
 * - B2: Email Engine (Salutation, subject-line micro-grammar, modal politeness, bullet parallelism)
 * - B3: Listening Engine (Reduction-form mapping, segmentation, intonation tracking)
 * - B4: Pronunciation Engine (Phoneme ending audibility, stress shift, 7-step correction path)
 * - B5: Reviewing Engine (Structural pass, 4-tier error taxonomy, hedged critique)
 * - B6: Book Writing Engine (Book-scale consistency, tense lock, reference decay, 5-stage editing)
 * - Historical Era Classifier (Ancient, Historical, Modern, Digital)
 * - Zero-Bridge Synchronous Memory direct mapping to 64-byte AtomicStateVector (AMSV)
 */

#ifndef GRA_CXX_BANDHU_CORE_HPP
#define GRA_CXX_BANDHU_CORE_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <string_view>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::bandhu {

enum class SkillType : uint8_t {
    Writing = 0,
    Emailing = 1,
    Listening = 2,
    Pronouncing = 3,
    Reviewing = 4,
    BookWriting = 5
};

enum class HistoricalEra : uint8_t {
    Ancient = 0,
    Historical = 1,
    Modern = 2,
    Digital = 3
};

enum class ErrorSeverity : uint8_t {
    Fatal = 0,
    Clarity = 1,
    Register = 2,
    StylePreference = 3
};

enum class EditingStage : uint8_t {
    Draft = 1,
    StructuralEdit = 2,
    LineEdit = 3,
    CopyEdit = 4,
    Proofread = 5
};

struct BandhuSkillResult {
    SkillType skill{SkillType::Writing};
    HistoricalEra era{HistoricalEra::Modern};
    float structural_score{1.0f};
    float register_score{1.0f};
    float consistency_score{1.0f};
    uint32_t fatal_errors{0};
    uint32_t clarity_errors{0};
    uint32_t register_errors{0};
    uint32_t style_preferences{0};
    EditingStage recommended_stage{EditingStage::CopyEdit};
    std::vector<std::string> diagnostic_notes{};
};

class BandhuCoreEngine {
public:
    static BandhuSkillResult evaluateWriting(std::string_view text);
    static BandhuSkillResult evaluateEmail(std::string_view text);
    static BandhuSkillResult evaluateReviewing(std::string_view text);
    static BandhuSkillResult evaluateBookWriting(std::string_view text);
    static HistoricalEra classifyEra(std::string_view text);

    /**
     * @brief Zero-Bridge memory synchronization to the 64-byte AtomicStateVector.
     * Updates cognitive and structural telemetry directly without serialization.
     */
    static void syncToAMSV(const BandhuSkillResult& result, solorock::amsv::AtomicStateVector* amsv);
};

} // namespace solorock::bandhu

#endif // GRA_CXX_BANDHU_CORE_HPP
