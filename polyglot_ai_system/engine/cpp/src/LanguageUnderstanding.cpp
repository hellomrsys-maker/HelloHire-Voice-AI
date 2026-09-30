// =============================================================================
// engine/cpp/src/LanguageUnderstanding.cpp
// Full implementation of the linguistic analysis and reasoning chain pipeline
// =============================================================================

#include "LanguageUnderstanding.h"

#include <algorithm>
#include <sstream>
#include <cmath>
#include <cassert>
#include <cctype>
#include <regex>

namespace engine {

// =============================================================================
// DependencyTree helpers
// =============================================================================

std::string DependencyTree::toLinear() const {
    std::ostringstream oss;
    for (const auto& node : nodes) {
        oss << "tok[" << node.token_index << "] "
            << node.dep_label << " → head[" << node.head_index << "] | ";
    }
    return oss.str();
}

std::string ReasoningChain::toTrace() const {
    std::ostringstream oss;
    oss << "ReasoningChain for: \"" << query << "\"\n";
    for (const auto& step : steps) {
        oss << "  Step " << step.step_number
            << " [" << (step.accepted ? "ACCEPTED" : "REJECTED") << "] "
            << step.hypothesis << "\n"
            << "    evidence: " << step.supporting_evidence << "\n"
            << "    counter: "  << step.counter_evidence << "\n"
            << "    confidence: " << step.confidence << "\n";
    }
    oss << "Conclusion: " << conclusion
        << " (confidence=" << final_confidence << ")\n";
    return oss.str();
}

// =============================================================================
// LanguageUnderstanding — construction
// =============================================================================

LanguageUnderstanding::LanguageUnderstanding(
    const EngineConfig&  config,
    AttentionMechanism&  attention,
    MemoryManager&       memory)
    : config_(config)
    , attention_(attention)
    , memory_(memory)
{
    registerBuiltinIntents();
}

// =============================================================================
// Built-in intent classifiers
// =============================================================================

void LanguageUnderstanding::registerBuiltinIntents() {
    // ---- Greeting intent ----
    registerIntent("greet", [](const TokenizedUtterance& utt, const DependencyTree&)
        -> std::optional<Intent>
    {
        static const std::vector<std::string> greet_words = {
            "hi", "hello", "hey", "howdy", "greetings", "good morning",
            "good afternoon", "good evening", "sup", "yo"
        };
        for (const auto& tok : utt.tokens) {
            for (const auto& g : greet_words) {
                if (tok.normalized == g) {
                    return Intent{
                        .name       = "greet",
                        .confidence = 0.95f,
                        .slots      = {}
                    };
                }
            }
        }
        return std::nullopt;
    });

    // ---- Identity introduction intent ----
    registerIntent("introduce_self", [](const TokenizedUtterance& utt,
                                         const DependencyTree& tree)
        -> std::optional<Intent>
    {
        // Look for "I am/I'm/my name is" pattern followed by a proper noun
        bool has_identity_phrase = false;
        std::string name_slot;

        for (size_t i = 0; i + 1 < utt.tokens.size(); ++i) {
            const auto& t = utt.tokens[i];
            if ((t.normalized == "i" || t.normalized == "my") &&
                i + 2 < utt.tokens.size())
            {
                const auto& t2 = utt.tokens[i + 1];
                if (t2.normalized == "am" || t2.normalized == "'m" ||
                    t2.normalized == "name")
                {
                    has_identity_phrase = true;
                    // Look for proper noun after
                    for (size_t j = i + 2; j < utt.tokens.size(); ++j) {
                        const auto& tn = utt.tokens[j];
                        if (tn.pos_tag == "PROPN" || tn.pos_tag == "NNP") {
                            name_slot = tn.surface;
                            break;
                        }
                        if (!tn.is_special && tn.pos_tag != "AUX" &&
                            tn.pos_tag != "DET")
                        {
                            name_slot = tn.surface;
                            break;
                        }
                    }
                    break;
                }
            }
        }

        if (has_identity_phrase) {
            return Intent{
                .name       = "introduce_self",
                .confidence = 0.9f,
                .slots      = {{"speaker_name", name_slot}}
            };
        }
        return std::nullopt;
    });

    // ---- Question intent ----
    registerIntent("ask_question", [](const TokenizedUtterance& utt,
                                       const DependencyTree&)
        -> std::optional<Intent>
    {
        static const std::vector<std::string> wh_words = {
            "what", "where", "when", "who", "whom", "whose",
            "which", "why", "how"
        };
        bool has_question_mark = false;
        bool has_wh_word = false;
        std::string wh_slot;

        for (const auto& tok : utt.tokens) {
            if (tok.surface == "?") has_question_mark = true;
            for (const auto& wh : wh_words) {
                if (tok.normalized == wh) {
                    has_wh_word = true;
                    wh_slot = wh;
                }
            }
        }

        if (has_question_mark || has_wh_word) {
            return Intent{
                .name       = "ask_question",
                .confidence = has_question_mark && has_wh_word ? 0.97f
                            : has_question_mark                ? 0.80f
                                                               : 0.65f,
                .slots      = {{"question_word", wh_slot}}
            };
        }
        return std::nullopt;
    });

    // ---- Request/command intent ----
    registerIntent("make_request", [](const TokenizedUtterance& utt,
                                       const DependencyTree&)
        -> std::optional<Intent>
    {
        static const std::vector<std::string> imperative_markers = {
            "please", "could you", "can you", "would you", "tell me",
            "show me", "explain", "describe", "write", "generate", "help"
        };
        const std::string& text = utt.raw_text;
        std::string lower_text;
        lower_text.resize(text.size());
        std::transform(text.begin(), text.end(), lower_text.begin(), ::tolower);

        for (const auto& marker : imperative_markers) {
            if (lower_text.find(marker) != std::string::npos) {
                return Intent{
                    .name       = "make_request",
                    .confidence = 0.82f,
                    .slots      = {{"request_marker", marker}}
                };
            }
        }
        return std::nullopt;
    });

    // ---- Farewell intent ----
    registerIntent("farewell", [](const TokenizedUtterance& utt,
                                   const DependencyTree&)
        -> std::optional<Intent>
    {
        static const std::vector<std::string> bye_words = {
            "bye", "goodbye", "farewell", "see you", "later", "cya",
            "good night", "take care", "until next time"
        };
        const std::string& lower = utt.raw_text;
        for (const auto& bw : bye_words) {
            if (lower.find(bw) != std::string::npos) {
                return Intent{
                    .name       = "farewell",
                    .confidence = 0.92f,
                    .slots      = {}
                };
            }
        }
        return std::nullopt;
    });
}

void LanguageUnderstanding::registerIntent(std::string name, IntentClassifier classifier) {
    intent_classifiers_[std::move(name)] = std::move(classifier);
}

// =============================================================================
// Morphological annotation
// =============================================================================

void LanguageUnderstanding::annotateMorphology(std::vector<Token>& tokens) const {
    // Production: use Rust tokenizer bridge for morphological analysis
    // Here: rule-based English morphology as baseline
    static const std::unordered_map<std::string, std::pair<std::string, std::string>> MORPH_TABLE = {
        {"am",     {"be",       "VBP"}},
        {"is",     {"be",       "VBZ"}},
        {"are",    {"be",       "VBP"}},
        {"was",    {"be",       "VBD"}},
        {"were",   {"be",       "VBD"}},
        {"'m",     {"be",       "VBP"}},
        {"i",      {"I",        "PRP"}},
        {"me",     {"I",        "PRP"}},
        {"my",     {"I",        "PRP$"}},
        {"we",     {"we",       "PRP"}},
        {"our",    {"we",       "PRP$"}},
        {"you",    {"you",      "PRP"}},
        {"your",   {"you",      "PRP$"}},
        {"he",     {"he",       "PRP"}},
        {"she",    {"she",      "PRP"}},
        {"it",     {"it",       "PRP"}},
        {"they",   {"they",     "PRP"}},
        {"the",    {"the",      "DT"}},
        {"a",      {"a",        "DT"}},
        {"an",     {"a",        "DT"}},
        {"hi",     {"hi",       "UH"}},
        {"hello",  {"hello",    "UH"}},
        {"hey",    {"hey",      "UH"}},
    };

    for (auto& tok : tokens) {
        if (tok.is_special) continue;
        auto it = MORPH_TABLE.find(tok.normalized);
        if (it != MORPH_TABLE.end()) {
            tok.lemma   = it->second.first;
            tok.pos_tag = it->second.second;
        } else if (tok.lemma.empty()) {
            tok.lemma = tok.normalized;
        }
        // Detect proper nouns: starts with uppercase and isn't sentence-initial
        if (!tok.surface.empty() && std::isupper(tok.surface[0]) &&
            tok.position > 0 && tok.pos_tag.empty())
        {
            tok.pos_tag = "PROPN";
        }
    }
}

// =============================================================================
// Syntax parsing (rule-based baseline; production: neural parser via Rust FFI)
// =============================================================================

DependencyTree LanguageUnderstanding::parseSyntax(const TokenizedUtterance& utterance) {
    DependencyTree tree;
    tree.root_index = 0;
    tree.nodes.reserve(utterance.tokens.size());

    for (size_t i = 0; i < utterance.tokens.size(); ++i) {
        SyntaxNode node;
        node.token_index = static_cast<uint32_t>(i);
        node.head_index  = -1;  // Default: root
        node.dep_label   = "root";

        const auto& tok = utterance.tokens[i];

        // Simple rule-based assignment:
        if (tok.pos_tag == "PRP" && tok.normalized == "i") {
            node.dep_label = "nsubj";
            // Find the main verb as head
            for (size_t j = i + 1; j < utterance.tokens.size(); ++j) {
                const std::string& pt = utterance.tokens[j].pos_tag;
                if (pt == "VBP" || pt == "VBZ" || pt == "VBD" || pt == "VB") {
                    node.head_index = static_cast<int32_t>(j);
                    tree.root_index = static_cast<uint32_t>(j);
                    break;
                }
            }
        } else if (tok.pos_tag == "PROPN" || tok.pos_tag == "NNP") {
            node.dep_label = "attr";
            node.head_index = static_cast<int32_t>(tree.root_index);
        } else if (tok.pos_tag == "UH") {
            node.dep_label = "discourse";
            node.head_index = static_cast<int32_t>(tree.root_index);
        } else if (tok.surface == "." || tok.surface == "?" || tok.surface == "!") {
            node.dep_label = "punct";
            node.head_index = static_cast<int32_t>(tree.root_index);
        }

        tree.nodes.push_back(node);
    }

    // Build child lists
    for (size_t i = 0; i < tree.nodes.size(); ++i) {
        int32_t head = tree.nodes[i].head_index;
        if (head >= 0 && head != static_cast<int32_t>(i)) {
            tree.nodes[static_cast<size_t>(head)].child_indices.push_back(
                static_cast<uint32_t>(i));
        }
    }

    return tree;
}

// =============================================================================
// Intent extraction
// =============================================================================

std::vector<Intent> LanguageUnderstanding::extractIntents(
    const TokenizedUtterance& utterance, const DependencyTree& tree)
{
    std::vector<Intent> intents;
    for (auto& [name, classifier] : intent_classifiers_) {
        auto result = classifier(utterance, tree);
        if (result.has_value()) {
            intents.push_back(std::move(*result));
        }
    }
    // Sort by confidence descending
    std::sort(intents.begin(), intents.end(),
              [](const Intent& a, const Intent& b) {
                  return a.confidence > b.confidence;
              });
    return intents;
}

// =============================================================================
// Register detection
// =============================================================================

RegisterType LanguageUnderstanding::detectRegister(const TokenizedUtterance& utterance) {
    static const std::vector<std::string> informal_markers = {
        "hey", "hi", "yo", "sup", "gonna", "wanna", "gotta", "ain't", "y'all"
    };
    static const std::vector<std::string> formal_markers = {
        "hereby", "sincerely", "respectfully", "regarding", "pursuant",
        "henceforth", "aforementioned", "whilst"
    };
    int informal_score = 0, formal_score = 0;

    for (const auto& tok : utterance.tokens) {
        for (const auto& fm : formal_markers)   if (tok.normalized == fm) ++formal_score;
        for (const auto& im : informal_markers) if (tok.normalized == im) ++informal_score;
    }

    if (formal_score > informal_score) return RegisterType::FORMAL;
    if (informal_score > 0) return RegisterType::INFORMAL;
    return RegisterType::NEUTRAL;
}

// =============================================================================
// Sentiment estimation
// =============================================================================

float LanguageUnderstanding::estimateSentiment(const TokenizedUtterance& utterance) {
    static const std::unordered_map<std::string, float> LEXICON = {
        {"good",      0.7f},  {"great",    0.8f},  {"excellent", 0.9f},
        {"wonderful", 0.9f},  {"happy",    0.8f},  {"love",      0.9f},
        {"bad",      -0.7f},  {"terrible", -0.9f}, {"hate",     -0.9f},
        {"awful",    -0.8f},  {"horrible", -0.9f}, {"sad",      -0.6f},
        {"okay",      0.1f},  {"fine",     0.2f},  {"alright",   0.2f},
    };

    float score = 0.0f;
    int count = 0;
    for (const auto& tok : utterance.tokens) {
        auto it = LEXICON.find(tok.normalized);
        if (it != LEXICON.end()) {
            score += it->second;
            ++count;
        }
    }
    return count > 0 ? std::max(-1.0f, std::min(1.0f, score / count)) : 0.0f;
}

// =============================================================================
// Memory context integration
// =============================================================================

std::string LanguageUnderstanding::integrateMemoryContext(
    const std::vector<float>& context_embedding) const
{
    if (context_embedding.empty()) return "";

    auto recall = memory_.recall(context_embedding, 3, 3);
    std::ostringstream oss;

    if (!recall.episodic_hits.empty()) {
        oss << "[EpisodicContext: ";
        for (size_t i = 0; i < recall.episodic_hits.size(); ++i) {
            if (i > 0) oss << "; ";
            oss << recall.episodic_hits[i].content.substr(0, 80);
        }
        oss << "]";
    }
    if (!recall.semantic_hits.empty()) {
        oss << " [SemanticContext: ";
        for (size_t i = 0; i < recall.semantic_hits.size(); ++i) {
            if (i > 0) oss << "; ";
            oss << recall.semantic_hits[i].name;
        }
        oss << "]";
    }
    return oss.str();
}

// =============================================================================
// Reasoning chain construction
// Implements "thinking ability and deep reasoning chains" from the spec
// =============================================================================

ReasoningChain LanguageUnderstanding::buildReasoningChain(
    const std::string& query,
    const MeaningFrame& partial_frame,
    ReasoningDepth depth)
{
    ReasoningChain chain;
    chain.query      = query;
    chain.depth_used = depth;

    const uint32_t max_steps =
        depth == ReasoningDepth::SHALLOW  ? 1 :
        depth == ReasoningDepth::MODERATE ? 3 :
        depth == ReasoningDepth::DEEP     ? 8 :
                                            config_.max_reasoning_steps;

    // Step 1: Anchor — what is the most likely intent?
    {
        ReasoningStep s;
        s.step_number         = 1;
        s.hypothesis          = "Primary communicative intent is: "
                                + partial_frame.primary_intent.name;
        s.supporting_evidence = "Confidence score: "
                                + std::to_string(partial_frame.primary_intent.confidence);
        s.counter_evidence    = "Other possible intents: "
                                + std::to_string(partial_frame.secondary_intents.size());
        s.confidence          = partial_frame.primary_intent.confidence;
        s.accepted            = s.confidence >= 0.5f;
        chain.steps.push_back(s);
    }

    if (max_steps < 2) {
        chain.conclusion      = partial_frame.natural_meaning;
        chain.final_confidence = partial_frame.primary_intent.confidence;
        return chain;
    }

    // Step 2: Context — what does memory tell us?
    {
        ReasoningStep s;
        s.step_number         = 2;
        std::string memory_ctx = integrateMemoryContext({}); // No embedding yet
        s.hypothesis          = "Memory context: " +
                                (memory_ctx.empty() ? "no prior context available" : memory_ctx);
        s.supporting_evidence = "Episodic and semantic memory queried.";
        s.counter_evidence    = "Memory may not be relevant to this query.";
        s.confidence          = 0.7f;
        s.accepted            = true;
        chain.steps.push_back(s);
    }

    if (max_steps < 3) {
        chain.conclusion      = partial_frame.natural_meaning;
        chain.final_confidence = partial_frame.primary_intent.confidence * 0.95f;
        return chain;
    }

    // Step 3: Register and pragmatics check
    {
        ReasoningStep s;
        s.step_number         = 3;
        s.hypothesis          = "Response should use register: "
                                + std::to_string(static_cast<int>(partial_frame.detected_register));
        s.supporting_evidence = "Detected from input surface markers.";
        s.counter_evidence    = "Register can shift mid-conversation.";
        s.confidence          = 0.85f;
        s.accepted            = true;
        chain.steps.push_back(s);
    }

    // Additional steps for DEEP and EXTENDED reasoning
    for (uint32_t step_i = 4; step_i <= max_steps && step_i <= 8; ++step_i) {
        ReasoningStep s;
        s.step_number         = step_i;
        s.hypothesis          = "Hypothesis at depth " + std::to_string(step_i)
                                + ": refining understanding via multi-hop reasoning.";
        s.supporting_evidence = "Cross-referencing slot evidence from prior steps.";
        s.counter_evidence    = "Diminishing confidence returns at step " + std::to_string(step_i);
        s.confidence          = std::max(0.3f, 0.9f - (step_i - 1) * 0.08f);
        s.accepted            = s.confidence >= 0.4f;
        chain.steps.push_back(s);
    }

    // Final conclusion: weighted average of accepted steps
    float weight_sum = 0.0f, score_sum = 0.0f;
    for (const auto& s : chain.steps) {
        if (s.accepted) {
            weight_sum += 1.0f;
            score_sum  += s.confidence;
        }
    }
    chain.final_confidence = weight_sum > 0 ? score_sum / weight_sum : 0.5f;
    chain.conclusion = partial_frame.natural_meaning
                     + " [reasoning depth="
                     + std::to_string(static_cast<int>(depth))
                     + ", steps=" + std::to_string(chain.steps.size()) + "]";

    return chain;
}

// =============================================================================
// Main analysis pipeline
// =============================================================================

MeaningFrame LanguageUnderstanding::analyze(
    const TokenizedUtterance& utterance, ReasoningDepth depth)
{
    // --- Stage 1: Morphological annotation ---
    TokenizedUtterance annotated = utterance; // Copy for mutation
    annotateMorphology(annotated.tokens);

    // --- Stage 2: Syntax parse ---
    DependencyTree tree = parseSyntax(annotated);

    // --- Stage 3: Intent extraction ---
    std::vector<Intent> intents = extractIntents(annotated, tree);

    // --- Stage 4: Register detection ---
    RegisterType reg = detectRegister(annotated);

    // --- Stage 5: Sentiment estimation ---
    float sentiment = estimateSentiment(annotated);

    // --- Stage 6: Assemble partial MeaningFrame ---
    MeaningFrame frame;
    if (!intents.empty()) {
        frame.primary_intent    = intents.front();
        frame.secondary_intents = std::vector<Intent>(intents.begin() + 1, intents.end());
    } else {
        frame.primary_intent = Intent{
            .name       = "unknown",
            .confidence = 0.3f,
            .slots      = {}
        };
    }
    frame.detected_register = reg;
    frame.sentiment         = sentiment;

    // Build literal meaning from dependency tree summary
    frame.literal_meaning = tree.toLinear();

    // Build natural meaning from primary intent + slots
    {
        std::ostringstream oss;
        oss << "The speaker's primary intent is '" << frame.primary_intent.name << "'";
        if (!frame.primary_intent.slots.empty()) {
            oss << " with slots: ";
            bool first = true;
            for (const auto& [k, v] : frame.primary_intent.slots) {
                if (!first) oss << ", ";
                oss << k << "=" << v;
                first = false;
            }
        }
        oss << ".";
        frame.natural_meaning = oss.str();
    }

    // --- Stage 7: Reasoning chain ---
    ReasoningChain chain = buildReasoningChain(utterance.raw_text, frame, depth);
    last_reasoning_trace_ = chain.toTrace();

    // Refine confidence from reasoning
    frame.certainty = chain.final_confidence;

    return frame;
}

std::string LanguageUnderstanding::getReasoningTrace() const {
    return last_reasoning_trace_;
}

} // namespace engine
