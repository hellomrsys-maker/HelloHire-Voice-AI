/**
 * @file dcve_core.cpp
 * @brief DCVE C++ Real-Time Core Implementation.
 */

#include "dcve_core.hpp"
#include <algorithm>
#include <regex>

namespace solorock::dcve {

static bool contains_term(const std::string& str, const std::string& sub) {
    if (sub.empty() || str.length() < sub.length()) return false;
    auto it = std::search(
        str.begin(), str.end(),
        sub.begin(), sub.end(),
        [](char a, char b) { return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b)); }
    );
    return (it != str.end());
}

DomainCompetenceVerbalEngine::DomainCompetenceVerbalEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

float DomainCompetenceVerbalEngine::score_depth(const std::string& text) const {
    const std::vector<std::string> buzzwords = {
        "synergy", "paradigm shift", "disruptive", "cutting-edge", "game-changer",
        "seamless", "ai-driven", "blazing fast", "hyper-growth", "holistic"
    };
    const std::vector<std::string> substance = {
        "idempotency", "linearizability", "two-phase commit", "raft", "paxos",
        "vector clock", "eventual consistency", "bounded queue", "memory-mapped",
        "p99", "tail latency", "b-tree", "lsm tree", "zero-copy", "mutex",
        "ebitda", "wacc", "discounted cash flow", "differential diagnosis", "statute"
    };

    int buzz_hits = 0;
    for (const auto& b : buzzwords) {
        if (contains_term(text, b)) buzz_hits++;
    }
    int sub_hits = 0;
    for (const auto& s : substance) {
        if (contains_term(text, s)) sub_hits++;
    }

    float base = 0.25f + sub_hits * 0.18f;
    float penalty = buzz_hits * 0.12f;
    return std::clamp(base - penalty, 0.05f, 1.0f);
}

float DomainCompetenceVerbalEngine::score_precision(const std::string& text) const {
    std::regex quant_regex(R"(\b\d+(?:\.\d+)?(?:%|ms|gb|mb|req/s|rps|\$)\b)", std::regex::icase);
    auto words_begin = std::sregex_iterator(text.begin(), text.end(), quant_regex);
    auto words_end = std::sregex_iterator();
    int quant_count = static_cast<int>(std::distance(words_begin, words_end));

    const std::vector<std::string> causal = {
        "because", "as a result of", "consequently", "resulting in",
        "due to", "led to", "by replacing", "by implementing"
    };
    int causal_hits = 0;
    for (const auto& c : causal) {
        if (contains_term(text, c)) causal_hits++;
    }

    float prec = 0.25f + quant_count * 0.25f + causal_hits * 0.15f;
    return std::clamp(prec, 0.0f, 1.0f);
}

uint16_t DomainCompetenceVerbalEngine::classify_track(const std::string& text) const {
    int eng = 0, fin = 0, med = 0, leg = 0, exe = 0;
    if (contains_term(text, "distributed") || contains_term(text, "concurrency") || contains_term(text, "latency") || contains_term(text, "database")) eng += 2;
    if (contains_term(text, "ebitda") || contains_term(text, "dcf") || contains_term(text, "valuation") || contains_term(text, "portfolio")) fin += 2;
    if (contains_term(text, "clinical") || contains_term(text, "etiology") || contains_term(text, "pathology") || contains_term(text, "diagnosis")) med += 2;
    if (contains_term(text, "statute") || contains_term(text, "tort") || contains_term(text, "jurisdiction") || contains_term(text, "litigation")) leg += 2;
    if (contains_term(text, "board") || contains_term(text, "stakeholder") || contains_term(text, "roadmap") || contains_term(text, "headcount")) exe += 2;

    int max_val = std::max({eng, fin, med, leg, exe});
    if (max_val == 0) return 1; // default engineering
    if (eng == max_val) return 1;
    if (fin == max_val) return 2;
    if (med == max_val) return 3;
    if (leg == max_val) return 4;
    return 5;
}

float DomainCompetenceVerbalEngine::score_grounding(const std::string& text) const {
    const std::vector<std::pair<std::string, std::string>> relations = {
        {"kafka", "partition"}, {"redis", "cache"}, {"b-tree", "indexing"},
        {"raft", "consensus"}, {"dcf", "cash flow"}, {"clinical", "trial"}
    };
    int hits = 0;
    for (const auto& r : relations) {
        if (contains_term(text, r.first) && contains_term(text, r.second)) hits++;
    }
    return std::clamp(0.35f + hits * 0.25f, 0.0f, 1.0f);
}

DomainCompetenceScorecard DomainCompetenceVerbalEngine::evaluate(const std::string& answer) {
    DomainCompetenceScorecard sc{};
    sc.depth_score     = score_depth(answer);
    sc.precision_score = score_precision(answer);
    sc.track_id        = classify_track(answer);
    sc.grounding_score = score_grounding(answer);

    sc.domain_competence_index =
        (sc.depth_score     * 0.40f) +
        (sc.precision_score * 0.35f) +
        (sc.grounding_score * 0.25f);
    sc.domain_competence_index = std::clamp(sc.domain_competence_index, 0.0f, 1.0f);

    if      (sc.domain_competence_index >= 0.75f) sc.domain_grade = 1; // Expert
    else if (sc.domain_competence_index >= 0.55f) sc.domain_grade = 2; // Proficient
    else if (sc.domain_competence_index >= 0.35f) sc.domain_grade = 3; // Surface Level
    else                                          sc.domain_grade = 4; // Novice

    sync_to_amsv(sc);
    return sc;
}

void DomainCompetenceVerbalEngine::sync_to_amsv(const DomainCompetenceScorecard& sc) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Lower 32 bits of 0x30: [depth_q16 | precision_q16]
    uint64_t current = sv_->maio_global_state_alpha.load(std::memory_order_relaxed);
    uint64_t updated = (current & 0xFFFFFFFF00000000ULL) |
                       (static_cast<uint64_t>(to_q16(sc.precision_score)) << 16) |
                       static_cast<uint64_t>(to_q16(sc.depth_score));

    sv_->maio_global_state_alpha.store(updated, std::memory_order_release);
}

} // namespace solorock::dcve

extern "C" {
    int32_t dcve_cpp_evaluate(
        const char* answer,
        solorock::dcve::DomainCompetenceScorecard* out
    ) {
        if (!answer || !out) return -1;
        solorock::dcve::DomainCompetenceVerbalEngine engine(nullptr);
        *out = engine.evaluate(answer);
        return 0;
    }
}
