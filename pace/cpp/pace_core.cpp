/**
 * @file pace_core.cpp
 * @brief PACE C++ Real-Time Core Implementation.
 */

#include "pace_core.hpp"
#include <algorithm>
#include <sstream>

namespace solorock::pace {

static bool contains_term(const std::string& str, const std::string& sub) {
    if (sub.empty() || str.length() < sub.length()) return false;
    auto it = std::search(
        str.begin(), str.end(),
        sub.begin(), sub.end(),
        [](char a, char b) { return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b)); }
    );
    return (it != str.end());
}

PacingAdaptationEngine::PacingAdaptationEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

float PacingAdaptationEngine::score_vocab_adaptation(const std::string& prompt, const std::string& resp) const {
    bool wants_simple = contains_term(prompt, "in simple terms") || contains_term(prompt, "eli5") || contains_term(prompt, "layman");
    bool wants_deep   = contains_term(prompt, "deep dive") || contains_term(prompt, "technical specifics") || contains_term(prompt, "exact algorithm");

    bool has_jargon = contains_term(resp, "idempotency") || contains_term(resp, "linearizability") || contains_term(resp, "raft") || contains_term(resp, "byzantine");

    if (wants_simple) {
        return has_jargon ? 0.40f : 0.95f;
    } else if (wants_deep) {
        return has_jargon ? 0.95f : 0.45f;
    }
    return 0.85f;
}

float PacingAdaptationEngine::score_length(const std::string& prompt, const std::string& resp) const {
    bool wants_brief = contains_term(prompt, "in one sentence") || contains_term(prompt, "briefly") || contains_term(prompt, "quick check");
    int words = 0;
    std::istringstream iss(resp);
    std::string token;
    while (iss >> token) words++;

    if (wants_brief) {
        return (words <= 30) ? 1.0f : (words <= 50 ? 0.70f : 0.35f);
    }
    return (words >= 15 && words <= 200) ? 0.90f : 0.65f;
}

PacingScorecard PacingAdaptationEngine::evaluate(const std::string& prompt, const std::string& response) {
    PacingScorecard sc{};
    sc.vocab_compliance  = score_vocab_adaptation(prompt, response);
    sc.length_compliance = score_length(prompt, response);
    sc.register_match    = 0.85f;
    sc.composure_score   = 0.90f;

    sc.adaptation_index =
        (sc.length_compliance * 0.30f) +
        (sc.vocab_compliance  * 0.30f) +
        (sc.register_match    * 0.20f) +
        (sc.composure_score   * 0.20f);
    sc.adaptation_index = std::clamp(sc.adaptation_index, 0.0f, 1.0f);

    if      (sc.adaptation_index >= 0.78f) sc.pacing_grade = 1; // Seamless
    else if (sc.adaptation_index >= 0.60f) sc.pacing_grade = 2; // Adaptive
    else if (sc.adaptation_index >= 0.40f) sc.pacing_grade = 3; // Rigid
    else                                   sc.pacing_grade = 4; // Oblivious

    sync_to_amsv(sc);
    return sc;
}

void PacingAdaptationEngine::sync_to_amsv(const PacingScorecard& sc) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Offset 0x3E: Cross-module attention slot bits [48-63]
    uint64_t current = sv_->maio_global_state_beta.load(std::memory_order_relaxed);
    uint64_t mask = ~(0xFFFFULL << 48);
    uint64_t updated = (current & mask) | (static_cast<uint64_t>(to_q16(sc.adaptation_index)) << 48);
    sv_->maio_global_state_beta.store(updated, std::memory_order_release);
}

} // namespace solorock::pace

extern "C" {
    int32_t pace_cpp_evaluate(
        const char* prompt, const char* response,
        solorock::pace::PacingScorecard* out
    ) {
        if (!prompt || !response || !out) return -1;
        solorock::pace::PacingAdaptationEngine engine(nullptr);
        *out = engine.evaluate(prompt, response);
        return 0;
    }
}
