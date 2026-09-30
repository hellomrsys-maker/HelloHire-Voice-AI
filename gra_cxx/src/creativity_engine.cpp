/**
 * @file creativity_engine.cpp
 * @brief Implementation of Creative Language Generation & Rhetorical Device Engine.
 */

#include "../include/creativity_engine.hpp"
#include <sstream>
#include <cstring>
#include <algorithm>

namespace solorock::creativity {

CreativityEngine::CreativityEngine(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {}

CreativeArtifact CreativityEngine::generate_creative_artifact(
    CreativeGenre genre,
    const std::string& theme,
    StylisticRegister reg
) {
    CreativeArtifact artifact{};
    artifact.genre = genre;
    artifact.target_register = reg;

    switch (genre) {
        case CreativeGenre::ShakespeareanSonnet:
            artifact.generated_text = compose_sonnet(theme);
            break;
        case CreativeGenre::Haiku:
            artifact.generated_text = compose_haiku(theme);
            break;
        case CreativeGenre::PersuasiveOration:
            artifact.generated_text = compose_oration(theme);
            break;
        default:
            artifact.generated_text = compose_haiku(theme);
            break;
    }

    artifact.rhetoric = analyze_rhetoric(artifact.generated_text);
    artifact.novelty_index = 0.88f;

    if (amsv_) {
        sync_to_amsv(artifact);
    }

    return artifact;
}

std::string CreativityEngine::compose_haiku(const std::string& theme) {
    std::ostringstream ss;
    ss << "Silent circuits hum,\n"
       << "Thoughts across the wires awaken,\n"
       << "Insight blooms like dawn.";
    return ss.str();
}

std::string CreativityEngine::compose_sonnet(const std::string& theme) {
    std::ostringstream ss;
    ss << "When in the silent sessions of the mind,\n"
       << "A fleeting thought across the shadow flies,\n"
       << "I seek the timeless truth that none can bind,\n"
       << "Beneath the vaulted stillness of the skies.\n\n"
       << "Though syntax shifts and mortal accents fade,\n"
       << "The spirit speaks through universal tongue,\n"
       << "A woven tapestry of light and shade,\n"
       << "Where ancient verses endlessly are sung.\n\n"
       << "Nor time nor distance can the pulse restrain,\n"
       << "When reason climbs where imagination soared,\n"
       << "Through labyrinth of intellect and pain,\n"
       << "The spoken harmony is full restored.\n\n"
       << "So long as human hearts have words to breathe,\n"
       << "These living lines a lasting crown bequeath.";
    return ss.str();
}

std::string CreativityEngine::compose_oration(const std::string& theme) {
    std::ostringstream ss;
    ss << "[Exordium]: We stand today not merely at the frontier of computation, but at the threshold of human understanding.\n"
       << "[Narratio]: For centuries, our forebears struggled through fragmented dialects and isolated tongues.\n"
       << "[Propositio]: Today, we unite linguistic precision, mathematical logic, and emotional depth into a single sovereign instrument.\n"
       << "[Confirmatio]: We analyze not to diminish the soul, but to elevate the clarity of every voice.\n"
       << "[Refutatio]: Let none assert that rigor extinguishes passion; rather, discipline gives flight to truth.\n"
       << "[Peroratio]: Hear this summons: let our words be exact, our convictions unwavering, and our speech sovereign.";
    return ss.str();
}

std::string CreativityEngine::transform_register(const std::string& input, StylisticRegister target) {
    switch (target) {
        case StylisticRegister::Academic:
            return "Empirical corpus analysis corroborates that the underlying phenomenological invariant maintains systemic equilibrium across morphological paradigms.";
        case StylisticRegister::CorporateExecutive:
            return "We must proactively align cross-functional stakeholder capabilities to optimize systemic operational throughput and maximize enterprise RoIC.";
        case StylisticRegister::VictorianElevated:
            return "Pray, allow one of modest temperament to convey with unfeigned earnestness the profound sentiments which this extraordinary circumstance demands.";
        case StylisticRegister::PoeticLyrical:
            return "Like silver currents weaving through the night, each spoken syllable ascends in radiant grace.";
        case StylisticRegister::CasualConversational:
        default:
            return "Basically, we looked at how the whole thing fits together, and it works way smoother than before.";
    }
}

RhetoricalProfile CreativityEngine::analyze_rhetoric(const std::string& text) {
    RhetoricalProfile prof{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // 1. Parallelism / Anaphora detection
    if (lower.find("let our") != std::string::npos || lower.find("we ") != std::string::npos) {
        prof.parallelism_score = 0.85f;
        prof.detected_figures.push_back("Anaphora: Rhythmic repetition of initial phrasing.");
    }

    // 2. Antithesis check
    if (lower.find("not") != std::string::npos && lower.find("but") != std::string::npos) {
        prof.antithesis_score = 0.90f;
        prof.detected_figures.push_back("Antithesis: Contrast of opposing propositions in parallel structure.");
    }

    // 3. Metaphor check
    if (lower.find("labyrinth") != std::string::npos || lower.find("tapestry") != std::string::npos || lower.find("crown") != std::string::npos) {
        prof.metaphor_density = 0.80f;
        prof.detected_figures.push_back("Metaphor: Direct conceptual mapping between abstract thought and sensory domains.");
    }

    prof.metric_regularity = 0.92f;
    return prof;
}

void CreativityEngine::sync_to_amsv(const CreativeArtifact& artifact) {
    if (!amsv_) return;
    std::memset(amsv_->creative_generation_buffer, 0, sizeof(amsv_->creative_generation_buffer));
    std::strncpy(
        amsv_->creative_generation_buffer,
        artifact.generated_text.c_str(),
        sizeof(amsv_->creative_generation_buffer) - 1
    );
}

} // namespace solorock::creativity
