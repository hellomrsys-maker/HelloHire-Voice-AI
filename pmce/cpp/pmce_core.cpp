/**
 * @file pmce_core.cpp
 * @brief PMCE C++ Real-Time Core Implementation.
 */

#include "pmce_core.hpp"
#include <regex>

namespace solorock::pmce {

static bool contains_ignore_case(const std::string& str, const std::string& sub) {
    if (sub.empty() || str.length() < sub.length()) return false;
    auto it = std::search(
        str.begin(), str.end(),
        sub.begin(), sub.end(),
        [](char ch1, char ch2) { return std::tolower(static_cast<unsigned char>(ch1)) == std::tolower(static_cast<unsigned char>(ch2)); }
    );
    return (it != str.end());
}

PersuasionMessageConstructionEngine::PersuasionMessageConstructionEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

LogosMetrics PersuasionMessageConstructionEngine::compute_logos(const std::string& text) const {
    LogosMetrics m{};
    const std::vector<std::string> connectors = {
        "because", "therefore", "consequently", "hence", "it follows that",
        "given that", "evidence suggests", "data shows", "specifically", "in contrast"
    };
    const std::vector<std::string> fallacies = {
        "everyone knows", "it's obvious", "you can't deny", "always", "never"
    };

    for (const auto& c : connectors) {
        if (contains_ignore_case(text, c)) m.logic_connectors++;
    }
    for (const auto& f : fallacies) {
        if (contains_ignore_case(text, f)) m.fallacy_count++;
    }

    std::regex data_regex(R"(\d+\s*%|\$\d+|\d+x\b|\bROI\b|\bp99\b)", std::regex::icase);
    m.data_backed = std::regex_search(text, data_regex);

    float base = 0.30f + m.logic_connectors * 0.14f + (m.data_backed ? 0.20f : 0.0f);
    float penalty = std::min(0.40f, m.fallacy_count * 0.15f);
    m.composite_score = std::clamp(base - penalty, 0.0f, 1.0f);
    return m;
}

EthosMetrics PersuasionMessageConstructionEngine::compute_ethos(const std::string& text) const {
    EthosMetrics m{};
    const std::vector<std::string> credentials = {
        "in my experience", "as a", "having led", "when i architected", "my track record",
        "i've successfully", "i have delivered", "i managed", "i built"
    };
    const std::vector<std::string> expert_vocab = {
        "roi", "kpi", "okr", "p99 latency", "consensus protocol", "architecture",
        "differential diagnosis", "monte carlo", "concurrency", "stakeholder"
    };

    for (const auto& c : credentials) {
        if (contains_ignore_case(text, c)) m.credential_signals++;
    }
    for (const auto& e : expert_vocab) {
        if (contains_ignore_case(text, e)) m.expertise_markers++;
    }

    float cred_score = std::min(1.0f, m.credential_signals * 0.25f);
    float expert_score = std::min(1.0f, m.expertise_markers * 0.18f);
    m.composite_score = std::clamp(cred_score * 0.55f + expert_score * 0.45f, 0.0f, 1.0f);
    return m;
}

PathosMetrics PersuasionMessageConstructionEngine::compute_pathos(const std::string& text) const {
    PathosMetrics m{};
    const std::vector<std::string> emotional = {
        "imagine", "feel", "matter", "believe", "care", "passionate", "impact",
        "inspire", "transform", "empower", "vision", "mission", "human", "story"
    };
    const std::vector<std::string> empathy = {
        "i understand your concern", "from your perspective", "team's view", "customer's experience"
    };

    for (const auto& c : emotional) {
        if (contains_ignore_case(text, c)) m.emotional_cues++;
    }
    for (const auto& e : empathy) {
        if (contains_ignore_case(text, e)) m.empathy_cues++;
    }

    float emo_score = std::min(1.0f, m.emotional_cues * 0.12f);
    float emp_score = std::min(1.0f, 0.40f + m.empathy_cues * 0.25f);
    m.composite_score = std::clamp(emo_score * 0.55f + emp_score * 0.45f, 0.0f, 1.0f);
    return m;
}

KairosMetrics PersuasionMessageConstructionEngine::compute_kairos(const std::string& text, uint16_t turn) const {
    KairosMetrics m{};
    const std::vector<std::string> transitions = {
        "building on that", "given what you just mentioned", "in light of your question",
        "that's exactly why", "which connects to", "now more than ever", "at this stage"
    };
    const std::vector<std::string> anchors = {
        "as you mentioned", "referring to your point", "going back to what you said"
    };

    for (const auto& c : transitions) {
        if (contains_ignore_case(text, c)) m.transition_cues++;
    }
    for (const auto& a : anchors) {
        if (contains_ignore_case(text, a)) m.context_anchors++;
    }

    float expected = static_cast<float>(std::max<int>(1, turn / 3));
    float raw = std::min(1.0f, (m.transition_cues + m.context_anchors * 1.5f) / expected);
    m.composite_score = std::clamp(0.35f + raw * 0.65f, 0.20f, 1.0f);
    return m;
}

CTAMetrics PersuasionMessageConstructionEngine::compute_cta(const std::string& text) const {
    CTAMetrics m{};
    const std::vector<std::string> strong_cta = {
        "i propose", "my recommendation is", "we should move forward with",
        "the next step is", "i suggest we", "let's agree on", "i plan to"
    };
    const std::vector<std::string> weak_endings = {
        "i think maybe", "could potentially", "might possibly", "something like that"
    };

    for (const auto& c : strong_cta) {
        if (contains_ignore_case(text, c)) m.strong_cta_signals++;
    }
    for (const auto& w : weak_endings) {
        if (contains_ignore_case(text, w)) m.weak_ending_count++;
    }

    float cta_score = std::min(1.0f, 0.30f + m.strong_cta_signals * 0.28f);
    float weak_penalty = std::min(0.35f, m.weak_ending_count * 0.15f);
    m.composite_score = std::clamp(cta_score - weak_penalty, 0.0f, 1.0f);
    return m;
}

PersuasionScorecard PersuasionMessageConstructionEngine::evaluate(const std::string& text, uint16_t turn) {
    PersuasionScorecard sc{};
    sc.logos  = compute_logos(text);
    sc.ethos  = compute_ethos(text);
    sc.pathos = compute_pathos(text);
    sc.kairos = compute_kairos(text, turn);
    sc.cta    = compute_cta(text);

    sc.global_persuasion_index =
        (sc.logos.composite_score  * 0.25f) +
        (sc.ethos.composite_score  * 0.20f) +
        (sc.pathos.composite_score * 0.18f) +
        (sc.kairos.composite_score * 0.20f) +
        (sc.cta.composite_score    * 0.17f);
    sc.global_persuasion_index = std::clamp(sc.global_persuasion_index, 0.0f, 1.0f);

    if      (sc.global_persuasion_index >= 0.80f) sc.persuasion_grade = 1; // Highly Persuasive
    else if (sc.global_persuasion_index >= 0.65f) sc.persuasion_grade = 2; // Persuasive
    else if (sc.global_persuasion_index >= 0.48f) sc.persuasion_grade = 3; // Adequate
    else                                          sc.persuasion_grade = 4; // Weak

    sync_to_amsv(sc, turn);
    return sc;
}

void PersuasionMessageConstructionEngine::sync_to_amsv(const PersuasionScorecard& sc, uint16_t turn) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Offset 0x28: aeee_examination_state packed as:
    // [Bits 0-15: Logos | Bits 16-31: Ethos | Bits 32-47: Pathos | Bits 48-63: CTA & Grade]
    uint64_t state = (static_cast<uint64_t>(sc.persuasion_grade & 0xFF) << 56) |
                     (static_cast<uint64_t>(to_q16(sc.cta.composite_score) >> 8) << 48) |
                     (static_cast<uint64_t>(to_q16(sc.pathos.composite_score)) << 32) |
                     (static_cast<uint64_t>(to_q16(sc.ethos.composite_score)) << 16) |
                     static_cast<uint64_t>(to_q16(sc.logos.composite_score));

    sv_->aeee_examination_state.store(state, std::memory_order_release);
}

} // namespace solorock::pmce

extern "C" {
    int32_t pmce_cpp_evaluate(
        const char* text, uint16_t turn,
        solorock::pmce::PersuasionScorecard* out
    ) {
        if (!text || !out) return -1;
        solorock::pmce::PersuasionMessageConstructionEngine engine(nullptr);
        *out = engine.evaluate(text, turn);
        return 0;
    }
}
