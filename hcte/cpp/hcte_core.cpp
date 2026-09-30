/**
 * @file hcte_core.cpp
 * @brief HCTE C++ Real-Time Core Implementation.
 */

#include "hcte_core.hpp"
#include <algorithm>
#include <regex>

namespace solorock::hcte {

static bool contains_term(const std::string& str, const std::string& sub) {
    if (sub.empty() || str.length() < sub.length()) return false;
    auto it = std::search(
        str.begin(), str.end(),
        sub.begin(), sub.end(),
        [](char a, char b) { return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b)); }
    );
    return (it != str.end());
}

HumanCognitiveThinkingEngine::HumanCognitiveThinkingEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

float HumanCognitiveThinkingEngine::score_optimism(const std::string& text) const {
    const std::vector<std::string> markers = {
        "opportunity", "growth", "potential", "strength", "upside",
        "thrive", "success", "leverage", "promising", "breakthrough"
    };
    int hits = 0;
    for (const auto& m : markers) {
        if (contains_term(text, m)) hits++;
    }
    return std::clamp(0.20f + hits * 0.15f, 0.0f, 1.0f);
}

float HumanCognitiveThinkingEngine::score_pessimism(const std::string& text) const {
    const std::vector<std::string> markers = {
        "risk", "failure", "bottleneck", "vulnerability", "threat",
        "downside", "cascade", "collapse", "outage", "flaw", "debt"
    };
    int hits = 0;
    for (const auto& m : markers) {
        if (contains_term(text, m)) hits++;
    }
    return std::clamp(0.20f + hits * 0.15f, 0.0f, 1.0f);
}

void HumanCognitiveThinkingEngine::score_premortem(
    const std::string& text, float& rpn, float& solutions
) const {
    const std::vector<std::string> failure_modes = {
        "root cause", "cascade failure", "single point of failure",
        "memory leak", "race condition", "data corruption", "deadlock"
    };
    const std::vector<std::string> mitigations = {
        "mitigation", "circuit breaker", "fallback", "redundancy",
        "rollback", "remediation", "monitoring", "recovery plan"
    };

    int fail_hits = 0;
    for (const auto& f : failure_modes) {
        if (contains_term(text, f)) fail_hits++;
    }
    int sol_hits = 0;
    for (const auto& s : mitigations) {
        if (contains_term(text, s)) sol_hits++;
    }

    rpn = std::clamp(0.30f + fail_hits * 0.20f, 0.0f, 1.0f);
    solutions = std::clamp(0.25f + sol_hits * 0.22f, 0.0f, 1.0f);
}

float HumanCognitiveThinkingEngine::score_systems(const std::string& text) const {
    const std::vector<std::string> systems_markers = {
        "feedback loop", "second-order", "trade-off", "equilibrium",
        "interconnected", "dependency graph", "holistic", "dynamic"
    };
    int hits = 0;
    for (const auto& m : systems_markers) {
        if (contains_term(text, m)) hits++;
    }
    return std::clamp(0.25f + hits * 0.18f, 0.0f, 1.0f);
}

float HumanCognitiveThinkingEngine::score_tension(float optimism, float pessimism) const {
    // Cognitive tension is maximized when both risks and opportunities are recognized
    float min_val = std::min(optimism, pessimism);
    return std::clamp(min_val * 1.5f, 0.10f, 1.0f);
}

CognitiveScorecard HumanCognitiveThinkingEngine::evaluate(const std::string& scenario) {
    CognitiveScorecard sc{};
    sc.optimism_charge = score_optimism(scenario);
    sc.pessimism_index = score_pessimism(scenario);
    score_premortem(scenario, sc.premortem_rpn_norm, sc.solution_density);
    sc.systems_score = score_systems(scenario);
    sc.cognitive_tension = score_tension(sc.optimism_charge, sc.pessimism_index);
    sc.devils_advocate_score = std::clamp(sc.pessimism_index * 1.1f, 0.0f, 1.0f);
    sc.analyst_score = std::clamp((sc.systems_score + sc.premortem_rpn_norm) * 0.5f, 0.0f, 1.0f);

    // Global Cognitive Index: Pre-mortem gets 2x weight (0.30)
    sc.global_cognitive_index =
        (sc.optimism_charge        * 0.12f) +
        (sc.pessimism_index        * 0.15f) +
        (sc.premortem_rpn_norm     * 0.20f) + // Pre-Mortem risk
        (sc.solution_density       * 0.18f) + // Pre-Mortem solution
        (sc.systems_score          * 0.15f) +
        (sc.cognitive_tension      * 0.20f);
    sc.global_cognitive_index = std::clamp(sc.global_cognitive_index, 0.0f, 1.0f);

    if      (sc.global_cognitive_index >= 0.72f) sc.cognitive_grade = 1; // Highly Insightful
    else if (sc.global_cognitive_index >= 0.55f) sc.cognitive_grade = 2; // Insightful
    else if (sc.global_cognitive_index >= 0.38f) sc.cognitive_grade = 3; // Adequate
    else                                         sc.cognitive_grade = 4; // Shallow

    sync_to_amsv(sc);
    return sc;
}

void HumanCognitiveThinkingEngine::sync_to_amsv(const CognitiveScorecard& sc) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Offset 0x38: maio_global_state_beta:
    // [Bits 0-15: Optimism | Bits 16-31: Pessimism | Bits 32-47: Tension | Bits 48-63: Solutions & Grade]
    uint64_t state = (static_cast<uint64_t>(sc.cognitive_grade & 0xFF) << 56) |
                     (static_cast<uint64_t>(to_q16(sc.solution_density) >> 8) << 48) |
                     (static_cast<uint64_t>(to_q16(sc.cognitive_tension)) << 32) |
                     (static_cast<uint64_t>(to_q16(sc.pessimism_index)) << 16) |
                     static_cast<uint64_t>(to_q16(sc.optimism_charge));

    sv_->maio_global_state_beta.store(state, std::memory_order_release);
}

} // namespace solorock::hcte

extern "C" {
    int32_t hcte_cpp_evaluate(
        const char* scenario,
        solorock::hcte::CognitiveScorecard* out
    ) {
        if (!scenario || !out) return -1;
        solorock::hcte::HumanCognitiveThinkingEngine engine(nullptr);
        *out = engine.evaluate(scenario);
        return 0;
    }
}
