// =============================================================================
// engine/cpp/src/ResponseGenerator.cpp
// Full implementation of response planning, realization, creativity engine,
// component families, and sentence templates
// =============================================================================

#include "ResponseGenerator.h"

#include <algorithm>
#include <sstream>
#include <cassert>
#include <cmath>
#include <numeric>
#include <regex>
#include <cctype>

namespace engine {

// =============================================================================
// ComponentFamily
// =============================================================================

const ComponentEntry& ComponentFamily::selectEntry(
    RegisterType target_register,
    float creativity_level,
    std::mt19937& rng) const
{
    assert(!entries.empty());

    // Score each entry: 1.0 for perfect register match, 0.5 for adjacent match
    std::vector<float> weights(entries.size());
    for (size_t i = 0; i < entries.size(); ++i) {
        float score = 1.0f;
        if (entries[i].register_type != target_register) {
            // Penalize register mismatch, but allow creative selection
            score = 0.3f + 0.4f * creativity_level;
        }
        // Scale by creativity weight
        score *= entries[i].creativity_weight;
        weights[i] = score;
    }

    // If creativity is high, flatten the distribution
    if (creativity_level > 0.7f) {
        float max_w = *std::max_element(weights.begin(), weights.end());
        for (auto& w : weights) w = max_w * (1.0f - creativity_level * 0.5f) + w * creativity_level;
    }

    // Weighted random selection
    std::discrete_distribution<size_t> dist(weights.begin(), weights.end());
    return entries[dist(rng)];
}

// =============================================================================
// SentenceTemplate::realize
// =============================================================================

std::string SentenceTemplate::realize(
    const std::unordered_map<std::string, ComponentFamily>& families,
    RegisterType target_register,
    float creativity_level,
    std::mt19937& rng) const
{
    std::string result;

    for (size_t slot_i = 0; slot_i < slot_order.size(); ++slot_i) {
        const std::string& slot_name = slot_order[slot_i];
        auto it = families.find(slot_name);

        if (it == families.end()) {
            if (!families.count(slot_name)) continue; // Optional slot
            continue;
        }

        const ComponentFamily& family = it->second;
        if (family.entries.empty()) continue;

        const ComponentEntry& entry = family.selectEntry(
            target_register, creativity_level, rng);

        // Select a random form from the entry
        std::uniform_int_distribution<size_t> form_dist(0, entry.forms.size() - 1);
        const std::string& form = entry.forms[form_dist(rng)];

        // Apply spacing rules:
        // No space before punctuation; add space between words
        if (!result.empty() &&
            form != "." && form != "," && form != "?" && form != "!" &&
            form != ";" && form != ":" && form != "'" && form != "\"" &&
            result.back() != ' ' && result.back() != '-')
        {
            // Check if form is a contraction continuation (e.g. "'m")
            if (form[0] != '\'') result += ' ';
        }
        result += form;
    }

    // Capitalize first letter
    if (!result.empty() && std::islower(result[0])) {
        result[0] = static_cast<char>(std::toupper(result[0]));
    }

    return result;
}

// =============================================================================
// CreativityEngine
// =============================================================================

CreativityEngine::CreativityEngine() {
    initMetaphorBank();
    initAnalogyBank();
}

void CreativityEngine::initMetaphorBank() {
    metaphor_bank_["time"]    = {"time is a river", "time is money",
                                  "time is a thief", "time is a healer"};
    metaphor_bank_["mind"]    = {"the mind is a garden", "the mind is a computer",
                                  "the mind is a muscle", "the mind is an ocean"};
    metaphor_bank_["idea"]    = {"ideas are seeds", "ideas are light",
                                  "ideas are bridges", "ideas are sparks"};
    metaphor_bank_["language"] = {"language is a tool", "language is a window",
                                   "language is music", "language is code"};
    metaphor_bank_["memory"]  = {"memory is a library", "memory is a photograph",
                                  "memory is a palimpsest", "memory is a stage"};
}

void CreativityEngine::initAnalogyBank() {
    analogy_bank_["learning"]["education"] = {
        "learning is like building a house, brick by brick",
        "learning is like planting seeds that bloom later",
        "learning is like tuning a musical instrument"
    };
    analogy_bank_["reasoning"]["engineering"] = {
        "reasoning is like debugging code — you trace each step",
        "reasoning is like structural analysis — load-bearing conclusions",
    };
    analogy_bank_["memory"]["architecture"] = {
        "memory is like a filing cabinet with millions of drawers",
        "memory is like a vast library where some shelves are dusty"
    };
}

std::vector<std::string> CreativityEngine::generateVariants(
    const std::string& base_text,
    const CreativeOptions& options,
    size_t n_variants) const
{
    std::vector<std::string> variants;
    variants.reserve(n_variants);

    // Variant 1: Paraphrase via synonym substitution (simplified)
    if (n_variants >= 1) {
        static const std::unordered_map<std::string, std::string> SYNONYMS = {
            {"happy",     "pleased"},  {"good",   "great"},    {"bad",    "poor"},
            {"say",       "mention"},  {"think",  "believe"},  {"know",   "understand"},
            {"important", "crucial"},  {"use",    "employ"},   {"start",  "begin"},
            {"end",       "conclude"}, {"help",   "assist"},   {"big",    "large"},
            {"small",     "tiny"},     {"fast",   "quick"},    {"slow",   "gradual"},
        };
        std::string paraphrase = base_text;
        // Simple word-level synonym substitution
        for (const auto& [word, synonym] : SYNONYMS) {
            std::regex word_re("\\b" + word + "\\b", std::regex_constants::icase);
            paraphrase = std::regex_replace(paraphrase, word_re, synonym,
                                            std::regex_constants::format_first_only);
        }
        if (paraphrase != base_text) {
            variants.push_back(std::move(paraphrase));
        } else {
            variants.push_back(base_text + " Indeed.");
        }
    }

    // Variant 2: Metaphor injection
    if (n_variants >= 2 && options.allow_metaphor) {
        std::string meta_variant = base_text;
        // Find a relevant concept and inject a metaphor
        for (const auto& [concept, metaphors] : metaphor_bank_) {
            std::string lower_base = base_text;
            std::transform(lower_base.begin(), lower_base.end(),
                           lower_base.begin(), ::tolower);
            if (lower_base.find(concept) != std::string::npos) {
                std::uniform_int_distribution<size_t> d(0, metaphors.size() - 1);
                meta_variant += " (" + metaphors[d(rng_)] + ")";
                break;
            }
        }
        variants.push_back(meta_variant);
    }

    // Variant 3: Structural rewrite (active ↔ passive, question form, etc.)
    if (n_variants >= 3 && options.allow_novel_structures) {
        // Simplified: reverse sentence into a question
        std::string question_form = "Did you know that " + base_text;
        if (!question_form.empty() && question_form.back() == '.') {
            question_form.back() = '?';
        } else {
            question_form += '?';
        }
        variants.push_back(question_form);
    }

    // Pad remaining with tonal variations
    while (variants.size() < n_variants) {
        static const std::array<std::string, 4> TONAL_SUFFIXES = {
            " Let me elaborate.", " That's quite interesting.",
            " Worth considering.", " Fascinating, isn't it?"
        };
        std::uniform_int_distribution<size_t> d(0, TONAL_SUFFIXES.size() - 1);
        variants.push_back(base_text + TONAL_SUFFIXES[d(rng_)]);
    }

    return variants;
}

std::string CreativityEngine::generateMetaphor(const std::string& concept) const {
    auto it = metaphor_bank_.find(concept);
    if (it == metaphor_bank_.end()) {
        return concept + " is like many things — its nature depends on perspective.";
    }
    std::uniform_int_distribution<size_t> d(0, it->second.size() - 1);
    return it->second[d(rng_)];
}

std::string CreativityEngine::generateAnalogy(
    const std::string& concept, const std::string& target_domain) const
{
    auto it = analogy_bank_.find(concept);
    if (it == analogy_bank_.end()) {
        return concept + " is analogous to many structures in " + target_domain + ".";
    }
    auto domain_it = it->second.find(target_domain);
    if (domain_it == it->second.end()) {
        // Return first available domain
        const auto& first_domain = it->second.begin()->second;
        std::uniform_int_distribution<size_t> d(0, first_domain.size() - 1);
        return first_domain[d(rng_)];
    }
    std::uniform_int_distribution<size_t> d(0, domain_it->second.size() - 1);
    return domain_it->second[d(rng_)];
}

std::string CreativityEngine::applyStyleTransfer(
    const std::string& text, const std::string& target_style) const
{
    if (target_style == "formal") {
        // Expand contractions
        std::string result = text;
        static const std::vector<std::pair<std::string, std::string>> EXPANSIONS = {
            {"I'm",   "I am"}, {"I've", "I have"}, {"I'll", "I will"},
            {"can't", "cannot"}, {"won't", "will not"}, {"don't", "do not"},
            {"it's",  "it is"}, {"that's", "that is"}, {"we're", "we are"},
        };
        for (const auto& [contraction, expansion] : EXPANSIONS) {
            std::regex re(contraction, std::regex_constants::icase);
            result = std::regex_replace(result, re, expansion);
        }
        return result;
    }
    if (target_style == "informal") {
        // Contract phrases
        std::string result = text;
        static const std::vector<std::pair<std::string, std::string>> CONTRACTIONS = {
            {"I am",   "I'm"}, {"I have", "I've"}, {"I will", "I'll"},
            {"cannot", "can't"}, {"will not", "won't"}, {"do not", "don't"},
        };
        for (const auto& [expansion, contraction] : CONTRACTIONS) {
            std::regex re(expansion, std::regex_constants::icase);
            result = std::regex_replace(result, re, contraction);
        }
        return result;
    }
    // Default: return unchanged
    return text;
}

float CreativityEngine::checkOriginality(
    const std::string& candidate,
    const std::vector<std::string>& recent_responses) const
{
    if (recent_responses.empty()) return 1.0f;

    // Compute character-level Jaccard similarity against each recent response
    auto word_set = [](const std::string& s) -> std::unordered_map<std::string, int> {
        std::unordered_map<std::string, int> ws;
        std::istringstream iss(s);
        std::string word;
        while (iss >> word) {
            std::transform(word.begin(), word.end(), word.begin(), ::tolower);
            ws[word]++;
        }
        return ws;
    };

    auto cand_ws = word_set(candidate);
    float min_originality = 1.0f;

    for (const auto& recent : recent_responses) {
        auto rec_ws = word_set(recent);

        // Compute Jaccard
        int intersection = 0, union_count = 0;
        for (const auto& [w, cnt] : cand_ws) {
            auto it = rec_ws.find(w);
            intersection += it != rec_ws.end() ? std::min(cnt, it->second) : 0;
            union_count  += cnt;
        }
        for (const auto& [w, cnt] : rec_ws) {
            if (!cand_ws.count(w)) union_count += cnt;
        }

        float similarity = union_count > 0 ?
            static_cast<float>(intersection) / static_cast<float>(union_count) : 0.0f;
        min_originality = std::min(min_originality, 1.0f - similarity);
    }
    return min_originality;
}

// =============================================================================
// ResponseGenerator — construction and initialization
// =============================================================================

ResponseGenerator::ResponseGenerator(
    const EngineConfig& config,
    LanguageUnderstanding& understanding,
    MemoryManager& memory)
    : config_(config)
    , understanding_(understanding)
    , memory_(memory)
{
    loadBuiltinTemplatesAndFamilies();
}

// =============================================================================
// Built-in templates and families (English baseline, per the spec architecture)
// =============================================================================

void ResponseGenerator::loadBuiltinTemplatesAndFamilies() {
    // ---- COMPONENT FAMILIES ----

    // Greeting family
    families_["greeting_family"] = ComponentFamily{
        "greeting_family",
        {
            {"hi",         {"Hi"},                 RegisterType::NEUTRAL,  1.0f},
            {"hey",        {"Hey"},                RegisterType::INFORMAL, 1.0f},
            {"hello",      {"Hello"},              RegisterType::NEUTRAL,  1.0f},
            {"hey_there",  {"Hey there"},          RegisterType::INFORMAL, 0.8f},
            {"good_day",   {"Good day"},           RegisterType::FORMAL,   0.9f},
            {"greetings",  {"Greetings"},          RegisterType::FORMAL,   0.8f},
        },
        false
    };

    // Identity family
    families_["identity_family"] = ComponentFamily{
        "identity_family",
        {
            {"i_am",        {"I am"},        RegisterType::NEUTRAL,  1.0f},
            {"contracted",  {"I'm"},         RegisterType::INFORMAL, 1.0f},
            {"my_name_is",  {"my name is"},  RegisterType::FORMAL,   0.9f},
            {"they_call_me",{"they call me"},RegisterType::NEUTRAL,  0.6f},
        },
        false
    };

    // Acknowledgement family
    families_["ack_family"] = ComponentFamily{
        "ack_family",
        {
            {"understood",   {"Understood."},         RegisterType::FORMAL,   1.0f},
            {"got_it",       {"Got it."},              RegisterType::INFORMAL, 1.0f},
            {"i_see",        {"I see."},               RegisterType::NEUTRAL,  1.0f},
            {"very_good",    {"Very well."},           RegisterType::FORMAL,   0.9f},
            {"noted",        {"Noted."},               RegisterType::NEUTRAL,  0.9f},
            {"alright",      {"Alright."},             RegisterType::INFORMAL, 0.8f},
        },
        false
    };

    // Response greeting family
    families_["response_greeting_family"] = ComponentFamily{
        "response_greeting_family",
        {
            {"nice_to_meet", {"Nice to meet you"},    RegisterType::NEUTRAL,  1.0f},
            {"pleasure",     {"A pleasure to meet you"}, RegisterType::FORMAL, 0.9f},
            {"good_to_meet", {"Good to meet you"},    RegisterType::NEUTRAL,  0.9f},
            {"hey_back",     {"Hey!"},                RegisterType::INFORMAL, 0.8f},
        },
        false
    };

    // Name family (per spec: name_family with approved person names + slot)
    families_["name_family"] = ComponentFamily{
        "name_family",
        {
            {"engine_name",  {"the Verbal Engine"},    RegisterType::NEUTRAL,  1.0f},
            {"assistant",    {"your AI assistant"},    RegisterType::NEUTRAL,  0.9f},
        },
        false
    };

    // Punctuation family
    families_["punctuation_family"] = ComponentFamily{
        "punctuation_family",
        {
            {"period",    {"."},  RegisterType::NEUTRAL,  1.0f},
            {"exclaim",   {"!"}, RegisterType::INFORMAL, 0.7f},
            {"comma",     {","}, RegisterType::NEUTRAL,  0.5f},
        },
        false
    };

    // Question response family
    families_["question_ack_family"] = ComponentFamily{
        "question_ack_family",
        {
            {"great_q",    {"That's a great question."},         RegisterType::NEUTRAL, 1.0f},
            {"let_me",     {"Let me think about that."},         RegisterType::NEUTRAL, 0.9f},
            {"interesting",{"Interesting question."},            RegisterType::NEUTRAL, 0.8f},
        },
        false
    };

    // Farewell family
    families_["farewell_family"] = ComponentFamily{
        "farewell_family",
        {
            {"goodbye",    {"Goodbye"},          RegisterType::NEUTRAL, 1.0f},
            {"bye",        {"Bye"},              RegisterType::INFORMAL,1.0f},
            {"farewell",   {"Farewell"},         RegisterType::FORMAL,  0.9f},
            {"see_you",    {"See you later"},    RegisterType::INFORMAL,0.9f},
            {"take_care",  {"Take care"},        RegisterType::NEUTRAL, 0.8f},
        },
        false
    };

    // ---- SENTENCE TEMPLATES ----

    // Template: respond to greeting + identity introduction
    templates_["greet_and_identify_response"] = SentenceTemplate{
        "greet_and_identify_response",
        "greet",
        {"response_greeting_family", "punctuation_family"},
        {},
        RegisterType::NEUTRAL
    };

    // Template: introduce self
    templates_["self_introduction"] = SentenceTemplate{
        "self_introduction",
        "introduce_self",
        {"greeting_family", "identity_family", "name_family", "punctuation_family"},
        {"identity_family_without_name_family"},
        RegisterType::NEUTRAL
    };

    // Template: acknowledge + greet back
    templates_["acknowledge_greeting"] = SentenceTemplate{
        "acknowledge_greeting",
        "greet",
        {"response_greeting_family", "punctuation_family"},
        {},
        RegisterType::NEUTRAL
    };

    // Template: answer a question
    templates_["answer_question"] = SentenceTemplate{
        "answer_question",
        "ask_question",
        {"question_ack_family"},
        {},
        RegisterType::NEUTRAL
    };

    // Template: farewell response
    templates_["farewell_response"] = SentenceTemplate{
        "farewell_response",
        "farewell",
        {"farewell_family", "punctuation_family"},
        {},
        RegisterType::NEUTRAL
    };

    // Template: general acknowledgement
    templates_["general_ack"] = SentenceTemplate{
        "general_ack",
        "unknown",
        {"ack_family"},
        {},
        RegisterType::NEUTRAL
    };
}

// =============================================================================
// Response planning
// =============================================================================

ResponsePlan ResponseGenerator::planResponse(
    const MeaningFrame& frame, ReasoningDepth depth)
{
    ResponsePlan plan;
    plan.communicative_goal = frame.primary_intent.name;
    plan.target_register    = frame.detected_register;
    plan.language_code      = config_.default_language;

    // Set creativity level based on intent and depth
    if (frame.primary_intent.name == "greet" ||
        frame.primary_intent.name == "introduce_self") {
        plan.creativity_level = 0.4f; // Moderate creativity for greetings
    } else if (frame.primary_intent.name == "ask_question") {
        plan.creativity_level = 0.6f;
    } else {
        plan.creativity_level = 0.5f;
    }

    // Boost creativity for deep reasoning depth
    if (depth == ReasoningDepth::DEEP || depth == ReasoningDepth::EXTENDED) {
        plan.creativity_level = std::min(1.0f, plan.creativity_level + 0.2f);
    }

    plan.depth = depth;

    // Fill content slots from intent slots
    for (const auto& [slot_name, slot_value] : frame.primary_intent.slots) {
        plan.content_slots.push_back(slot_name + "=" + slot_value);
    }

    return plan;
}

// =============================================================================
// Response realization
// =============================================================================

std::string ResponseGenerator::realize(const ResponsePlan& plan) {
    // Find matching template by communicative goal
    SentenceTemplate* tmpl = nullptr;
    for (auto& [tid, t] : templates_) {
        if (t.communication_intent == plan.communicative_goal) {
            tmpl = &t;
            break;
        }
    }

    if (!tmpl) {
        // Fallback: use general_ack
        auto it = templates_.find("general_ack");
        if (it != templates_.end()) tmpl = &it->second;
    }

    std::string realized;
    if (tmpl) {
        realized = tmpl->realize(families_,
                                  plan.target_register,
                                  plan.creativity_level,
                                  rng_);
    } else {
        realized = "I understand."; // Ultimate fallback
    }

    // Apply creativity variants if creativity is high
    if (plan.creativity_level > 0.6f) {
        CreativityEngine::CreativeOptions opts;
        opts.creativity_level = plan.creativity_level;
        opts.allow_metaphor   = plan.creativity_level > 0.7f;

        auto variants = creativity_.generateVariants(realized, opts, 2);
        if (!variants.empty()) {
            // Select the most original variant
            std::vector<std::string> recent(
                recent_responses_.begin(), recent_responses_.end());

            float best_score = creativity_.checkOriginality(realized, recent);
            std::string best  = realized;

            for (const auto& variant : variants) {
                float score = creativity_.checkOriginality(variant, recent);
                if (score > best_score) {
                    best_score = score;
                    best = variant;
                }
            }
            realized = best;
        }
    }

    // Style transfer if needed
    if (plan.target_register == RegisterType::FORMAL) {
        realized = creativity_.applyStyleTransfer(realized, "formal");
    } else if (plan.target_register == RegisterType::INFORMAL) {
        realized = creativity_.applyStyleTransfer(realized, "informal");
    }

    // Validate
    if (!validate(realized, plan)) {
        realized = generateFallbackResponse(MeaningFrame{
            .primary_intent = Intent{plan.communicative_goal, 0.5f, {}},
            .natural_meaning = plan.communicative_goal
        });
    }

    // Record in recent responses
    recent_responses_.push_back(realized);
    if (recent_responses_.size() > MAX_RECENT) {
        recent_responses_.pop_front();
    }

    return realized;
}

// =============================================================================
// Validation
// =============================================================================

bool ResponseGenerator::validate(const std::string& sentence,
                                   const ResponsePlan& plan) const
{
    if (sentence.empty()) return false;

    // Safety filter
    if (!passesFilterChecks(sentence)) return false;

    // Basic grammar check: must have at least one alphabetic character
    bool has_alpha = std::any_of(sentence.begin(), sentence.end(), ::isalpha);
    if (!has_alpha) return false;

    // Max length check
    if (sentence.size() > 4096) return false;

    return true;
}

bool ResponseGenerator::passesFilterChecks(const std::string& text) const {
    if (!config_.enable_safety_filter) return true;

    // Block obvious profanity or harmful content (simplified blocklist)
    static const std::vector<std::string> BLOCKED = {
        // This list is intentionally minimal for a production base;
        // full implementation would use a trained safety classifier via CUDA kernel.
        "__BLOCKED_CONTENT__"
    };
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    for (const auto& blocked : BLOCKED) {
        if (lower.find(blocked) != std::string::npos) return false;
    }
    return true;
}

std::string ResponseGenerator::generateFallbackResponse(const MeaningFrame& frame) const {
    (void)frame;
    return "I understand. How can I help you further?";
}

void ResponseGenerator::registerTemplate(SentenceTemplate tmpl) {
    templates_[tmpl.template_id] = std::move(tmpl);
}

void ResponseGenerator::registerFamily(ComponentFamily family) {
    families_[family.family_name] = std::move(family);
}

} // namespace engine
