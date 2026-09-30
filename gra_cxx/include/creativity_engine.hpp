/**
 * @file creativity_engine.hpp
 * @brief Creative Language Generation & Rhetorical Device Engine (C++20 Core).
 *
 * Implements poetic form synthesis (Shakespearean sonnet meter, Haiku 5-7-5),
 * rhetorical figure detection, and cross-register style transformation.
 */

#ifndef GRA_CXX_CREATIVITY_ENGINE_HPP
#define GRA_CXX_CREATIVITY_ENGINE_HPP

#include <string>
#include <vector>
#include <array>
#include <memory>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::creativity {

enum class CreativeGenre {
    ShakespeareanSonnet,
    Haiku,
    PersuasiveOration,
    DramaticDialogue,
    NarrativeFiction
};

enum class StylisticRegister {
    Academic,
    CorporateExecutive,
    VictorianElevated,
    PoeticLyrical,
    CasualConversational
};

struct RhetoricalProfile {
    float metaphor_density{0.0f};
    float antithesis_score{0.0f};
    float parallelism_score{0.0f};
    float metric_regularity{0.0f};
    std::vector<std::string> detected_figures;
};

struct CreativeArtifact {
    CreativeGenre genre{CreativeGenre::Haiku};
    StylisticRegister target_register{StylisticRegister::PoeticLyrical};
    std::string generated_text;
    RhetoricalProfile rhetoric;
    float novelty_index{0.85f};
};

class CreativityEngine {
public:
    explicit CreativityEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment = nullptr);
    ~CreativityEngine() = default;

    /// Generates structured literary artifact in specified genre and register
    CreativeArtifact generate_creative_artifact(CreativeGenre genre, const std::string& theme, StylisticRegister reg);

    /// Synthesizes cross-register style transfer preserving semantic invariants
    std::string transform_register(const std::string& input, StylisticRegister target);

    /// Analyzes text for classical rhetorical devices (Chiasmus, Anaphora, Tricolon, Antithesis)
    RhetoricalProfile analyze_rhetoric(const std::string& text);

    /// Synchronizes generated text to AMSV creative_generation_buffer
    void sync_to_amsv(const CreativeArtifact& artifact);

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};

    std::string compose_sonnet(const std::string& theme);
    std::string compose_haiku(const std::string& theme);
    std::string compose_oration(const std::string& theme);
};

} // namespace solorock::creativity

#endif // GRA_CXX_CREATIVITY_ENGINE_HPP
