// =============================================================================
// engine/cpp/include/ResponseGenerator.h
// Response planning, word selection, grammar realization, style control,
// creativity control, and final validation
// Implements: imagination, creativity, divergent thinking, and generative synthesis
// =============================================================================

#pragma once

#include "EngineCore.h"
#include "LanguageUnderstanding.h"
#include "MemoryManager.h"
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <functional>
#include <random>

namespace engine {

// =============================================================================
// ComponentFamily — the core compositional sentence building block
// Per the spec: engine learns to communicate by composing branches,
// not by memorizing thousands of nearly identical full sentences.
// =============================================================================

struct ComponentEntry {
    std::string id;
    std::vector<std::string> forms;
    RegisterType register_type;
    float creativity_weight = 1.0f;
};

struct ComponentFamily {
    std::string                  family_name;
    std::vector<ComponentEntry>  entries;
    bool                         is_optional = false;

    /// Returns a random entry weighted by register match and creativity level.
    const ComponentEntry& selectEntry(RegisterType target_register,
                                       float creativity_level,
                                       std::mt19937& rng) const;
};

// =============================================================================
// SentenceTemplate — a slot-order template that combines component families
// =============================================================================

struct SentenceTemplate {
    std::string                          template_id;
    std::string                          communication_intent;
    std::vector<std::string>             slot_order;      ///< family names in order
    std::vector<std::string>             blocked_combos;  ///< combination constraints
    RegisterType                         default_register = RegisterType::NEUTRAL;

    /// Realizes the template by selecting entries from each family.
    std::string realize(
        const std::unordered_map<std::string, ComponentFamily>& families,
        RegisterType target_register,
        float creativity_level,
        std::mt19937& rng) const;
};

// =============================================================================
// CreativityEngine — implements imagination, divergent thinking, and
// generative synthesis modules
// =============================================================================

class CreativityEngine {
public:
    struct CreativeOptions {
        float creativity_level = 0.5f;   ///< [0,1]: 0=conservative, 1=maximally creative
        bool  allow_metaphor   = true;
        bool  allow_analogy    = true;
        bool  allow_style_transfer = false;
        bool  allow_novel_structures = false;
    };

    CreativityEngine();

    /**
     * @brief Generates creative variations of a base response.
     * Implements "controlled variation" and "divergent thinking" from the spec.
     *
     * @param base_text     The baseline realized text.
     * @param options       Creativity parameters.
     * @param n_variants    Number of variations to produce.
     * @returns             Vector of creative variant strings.
     */
    std::vector<std::string> generateVariants(
        const std::string& base_text,
        const CreativeOptions& options,
        size_t n_variants = 3) const;

    /**
     * @brief Generates a metaphor for a given concept.
     * Implements "metaphor_generation" from the spec.
     */
    std::string generateMetaphor(const std::string& concept) const;

    /**
     * @brief Generates an analogy for a concept.
     */
    std::string generateAnalogy(const std::string& concept,
                                  const std::string& target_domain) const;

    /**
     * @brief Applies style transfer to a base text.
     */
    std::string applyStyleTransfer(const std::string& text,
                                    const std::string& target_style) const;

    /**
     * @brief Checks for originality — returns score [0,1] where 1 = highly original.
     * Compares against recently generated responses to avoid repetition.
     */
    float checkOriginality(const std::string& candidate,
                            const std::vector<std::string>& recent_responses) const;

private:
    mutable std::mt19937 rng_{std::random_device{}()};

    // Metaphor bank: concept → possible metaphors
    std::unordered_map<std::string, std::vector<std::string>> metaphor_bank_;

    // Analogy bank: concept → domain → analogies
    std::unordered_map<std::string,
        std::unordered_map<std::string, std::vector<std::string>>> analogy_bank_;

    void initMetaphorBank();
    void initAnalogyBank();
};

// =============================================================================
// ResponseGenerator — plans and realizes responses
// =============================================================================

class ResponseGenerator {
public:
    ResponseGenerator(const EngineConfig& config,
                      LanguageUnderstanding& understanding,
                      MemoryManager& memory);

    // -------------------------------------------------------------------------
    // Response planning
    // -------------------------------------------------------------------------

    /**
     * @brief Plans a response given a MeaningFrame.
     * Determines communicative goal, content slots, register, and creativity level.
     *
     * @param frame   Fully analyzed meaning frame from language understanding.
     * @param depth   Reasoning depth (affects planning quality).
     * @returns       A ResponsePlan ready for realization.
     */
    ResponsePlan planResponse(const MeaningFrame& frame, ReasoningDepth depth);

    // -------------------------------------------------------------------------
    // Response realization
    // -------------------------------------------------------------------------

    /**
     * @brief Realizes (surface-generates) a ResponsePlan into text.
     *
     * Realization pipeline:
     *   1. Select appropriate sentence template for the intent
     *   2. Select component families for each slot
     *   3. Apply register and style constraints
     *   4. Apply creativity engine if creativity > 0.3
     *   5. Validate grammar and meaning accuracy
     *   6. Originality check against recent responses
     *   7. Return final text
     *
     * @param plan  The response plan.
     * @returns     Final realized response text.
     */
    std::string realize(const ResponsePlan& plan);

    // -------------------------------------------------------------------------
    // Template and family registry
    // -------------------------------------------------------------------------

    /// Registers a sentence template.
    void registerTemplate(SentenceTemplate tmpl);

    /// Registers a component family.
    void registerFamily(ComponentFamily family);

    // -------------------------------------------------------------------------
    // Validation
    // -------------------------------------------------------------------------

    /**
     * @brief Validates a realized sentence for grammar, meaning, and safety.
     * @returns true if the sentence passes all validation checks.
     */
    bool validate(const std::string& sentence, const ResponsePlan& plan) const;

private:
    const EngineConfig&    config_;
    LanguageUnderstanding& understanding_;
    MemoryManager&         memory_;

    CreativityEngine       creativity_;
    mutable std::mt19937   rng_{std::random_device{}()};

    // Template and family registries
    std::unordered_map<std::string, SentenceTemplate>  templates_;
    std::unordered_map<std::string, ComponentFamily>   families_;

    // Recent responses (for originality checking)
    std::deque<std::string>  recent_responses_;
    static constexpr size_t  MAX_RECENT = 100;

    // Safety and privacy filter
    bool passesFilterChecks(const std::string& text) const;

    // Built-in templates and families (loaded from language engine training file)
    void loadBuiltinTemplatesAndFamilies();

    // Fallback response when no template matches
    std::string generateFallbackResponse(const MeaningFrame& frame) const;
};

} // namespace engine
