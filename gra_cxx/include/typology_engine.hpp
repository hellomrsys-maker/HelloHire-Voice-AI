/**
 * @file typology_engine.hpp
 * @brief Universal Comparative Grammar Typology Engine Core (C++20).
 *
 * Implements the cross-linguistic diagnostic framework defined in the Comparative Grammar Typology Guide:
 * - 11 Language Families
 * - 4 Morphological Types (Isolating, Agglutinative, Fusional, Polysynthetic)
 * - 4 Grammatical Alignments (Nominative-Accusative, Ergative-Absolutive, Active-Stative, Symmetrical Voice)
 * - Head Directionality (Head-Initial vs Head-Final)
 * - 8 Universal Diagnostic Pillars
 * - Zero-Bridge Synchronous Memory synchronization to AMSV
 */

#ifndef GRA_CXX_TYPOLOGY_ENGINE_HPP
#define GRA_CXX_TYPOLOGY_ENGINE_HPP

#include <string>
#include <vector>
#include <array>
#include <cstdint>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::typology {

enum class LanguageFamily : uint8_t {
    IndoEuropean = 0,
    SinoTibetan = 1,
    AfroAsiatic = 2,
    Austronesian = 3,
    NigerCongo = 4,
    JaponicKoreanic = 5,
    Dravidian = 6,
    Uralic = 7,
    Turkic = 8,
    NativeAmericanIsolates = 9,
    CreolesPidgins = 10
};

enum class MorphologicalType : uint8_t {
    Isolating = 0,
    Agglutinative = 1,
    Fusional = 2,
    Polysynthetic = 3
};

enum class GrammaticalAlignment : uint8_t {
    NominativeAccusative = 0,
    ErgativeAbsolutive = 1,
    ActiveStative = 2,
    SymmetricalVoice = 3
};

enum class HeadDirectionality : uint8_t {
    HeadInitial = 0,
    HeadFinal = 1
};

struct TypologicalProfile {
    LanguageFamily family{LanguageFamily::IndoEuropean};
    MorphologicalType morph_type{MorphologicalType::Fusional};
    GrammaticalAlignment alignment{GrammaticalAlignment::NominativeAccusative};
    HeadDirectionality directionality{HeadDirectionality::HeadInitial};
    float synthesis_index{2.1f};
    float greenberg_harmony{0.85f};
    std::array<float, 8> pillar_scores{0.85f, 0.80f, 0.85f, 0.88f, 0.90f, 0.86f, 0.82f, 0.80f};
    std::string diagnostic_summary;
    std::vector<std::string> l1_transfer_frictions;
};

class TypologyEngine {
public:
    explicit TypologyEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~TypologyEngine() = default;

    /// Analyzes an utterance or text sample under a target language family/hints
    TypologicalProfile analyze_sample(
        const std::string& text,
        LanguageFamily family_hint = LanguageFamily::Turkic
    );

    /// Synchronizes typological vector into AMSV physical memory (linguistic_embedding 0..15)
    void sync_to_amsv(const TypologicalProfile& profile);

    /// Predicts L1 -> L2 negative transfer friction points
    std::vector<std::string> predict_friction(LanguageFamily l1, LanguageFamily l2);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
};

} // namespace solorock::typology

#endif // GRA_CXX_TYPOLOGY_ENGINE_HPP
