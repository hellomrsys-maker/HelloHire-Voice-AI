// =============================================================================
// engine/cpp/include/LanguageUnderstanding.h
// Language understanding: tokenization → morphology → syntax → semantics
// → pragmatics → intent extraction → reasoning chains
// =============================================================================

#pragma once

#include "EngineCore.h"
#include "AttentionMechanism.h"
#include "MemoryManager.h"
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <functional>

namespace engine {

// =============================================================================
// SyntaxNode — a node in the dependency parse tree
// =============================================================================

struct SyntaxNode {
    uint32_t token_index;
    std::string dep_label;
    int32_t     head_index;   ///< -1 for root
    std::vector<uint32_t> child_indices;
};

struct DependencyTree {
    std::vector<SyntaxNode> nodes;
    uint32_t root_index;

    std::string toLinear() const;
};

// =============================================================================
// ReasoningChain — explicit multi-step thought process
// Implements "thinking ability and deep reasoning chains"
// =============================================================================

struct ReasoningStep {
    uint32_t    step_number;
    std::string hypothesis;
    std::string supporting_evidence;
    std::string counter_evidence;
    float       confidence;
    bool        accepted;
};

struct ReasoningChain {
    std::string             query;
    std::vector<ReasoningStep> steps;
    std::string             conclusion;
    float                   final_confidence;
    ReasoningDepth          depth_used;

    std::string toTrace() const;
};

// =============================================================================
// LanguageUnderstanding
// Processes TokenizedUtterance → MeaningFrame via linguistic analysis pipeline
// =============================================================================

class LanguageUnderstanding {
public:
    LanguageUnderstanding(const EngineConfig& config,
                          AttentionMechanism& attention,
                          MemoryManager& memory);

    // -------------------------------------------------------------------------
    // Main pipeline entry point
    // -------------------------------------------------------------------------

    /**
     * @brief Runs the full linguistic analysis pipeline on a tokenized utterance.
     *
     * Pipeline stages:
     *   1. Morphological analysis  — inflection, derivation, lemmatization
     *   2. Syntax analysis         — dependency parse
     *   3. Semantic analysis       — word sense, semantic roles, frames
     *   4. Pragmatic analysis      — speech acts, implicature, register
     *   5. Intent extraction       — classify communicative intent + slots
     *   6. Reasoning               — chain-of-thought (depth-controlled)
     *   7. Memory integration      — recall relevant episodic/semantic memory
     *
     * @param utterance  Tokenized utterance from the input processor.
     * @param depth      Desired reasoning depth.
     * @returns          MeaningFrame capturing the full understanding.
     */
    MeaningFrame analyze(const TokenizedUtterance& utterance, ReasoningDepth depth);

    /**
     * @brief Returns the reasoning trace from the most recent analyze() call.
     */
    std::string getReasoningTrace() const;

    // -------------------------------------------------------------------------
    // Individual analysis stages (also callable independently for testing)
    // -------------------------------------------------------------------------

    DependencyTree parseSyntax(const TokenizedUtterance& utterance);
    std::vector<Intent> extractIntents(const TokenizedUtterance& utterance,
                                        const DependencyTree& tree);
    RegisterType detectRegister(const TokenizedUtterance& utterance);
    float estimateSentiment(const TokenizedUtterance& utterance);

    ReasoningChain buildReasoningChain(
        const std::string& query,
        const MeaningFrame& partial_frame,
        ReasoningDepth depth);

    // -------------------------------------------------------------------------
    // Intent registry — register custom intent classifiers
    // -------------------------------------------------------------------------

    using IntentClassifier = std::function<
        std::optional<Intent>(const TokenizedUtterance&, const DependencyTree&)
    >;

    void registerIntent(std::string name, IntentClassifier classifier);

private:
    const EngineConfig&   config_;
    AttentionMechanism&   attention_;
    MemoryManager&        memory_;

    // Registered intent classifiers (loaded from engine training file)
    std::unordered_map<std::string, IntentClassifier> intent_classifiers_;

    // Last reasoning trace
    mutable std::string last_reasoning_trace_;

    // Core linguistic analysis helpers
    void annotateMorphology(std::vector<Token>& tokens) const;
    std::string inferWordSense(const Token& token,
                                const std::vector<Token>& context) const;
    std::string classifySpeechAct(const DependencyTree& tree,
                                   const std::vector<Token>& tokens) const;
    float computeContextualCertainty(const MeaningFrame& frame,
                                      const ReasoningChain& chain) const;

    // Memory-augmented reasoning: retrieves relevant memories to inform analysis
    std::string integrateMemoryContext(const std::vector<float>& context_embedding) const;

    // Built-in intent classifiers (greeting, identity, question, command, etc.)
    void registerBuiltinIntents();
};

} // namespace engine
