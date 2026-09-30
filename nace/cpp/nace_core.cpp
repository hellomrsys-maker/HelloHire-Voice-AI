/**
 * @file nace_core.cpp
 * @brief NACE C++ Real-Time Core Implementation.
 */

#include "nace_core.hpp"
#include <algorithm>
#include <regex>

namespace solorock::nace {

static bool contains_term(const std::string& str, const std::string& sub) {
    if (sub.empty() || str.length() < sub.length()) return false;
    auto it = std::search(
        str.begin(), str.end(),
        sub.begin(), sub.end(),
        [](char a, char b) { return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b)); }
    );
    return (it != str.end());
}

NarrativeArcCoherenceEngine::NarrativeArcCoherenceEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

float NarrativeArcCoherenceEngine::score_climax(const std::string& text) const {
    bool sit  = contains_term(text, "problem was") || contains_term(text, "facing") || contains_term(text, "outage");
    bool task = contains_term(text, "my role was") || contains_term(text, "goal was") || contains_term(text, "needed to");
    bool act  = contains_term(text, "i implemented") || contains_term(text, "we built") || contains_term(text, "i designed");
    bool res  = contains_term(text, "as a result") || contains_term(text, "achieved") || contains_term(text, "reduced");

    int count = (sit ? 1 : 0) + (task ? 1 : 0) + (act ? 1 : 0) + (res ? 1 : 0);
    return std::clamp(count * 0.25f, 0.0f, 1.0f);
}

float NarrativeArcCoherenceEngine::score_momentum(const std::string& text) const {
    const std::vector<std::string> forward = {
        "first", "then", "next", "subsequently", "finally", "to summarize"
    };
    const std::vector<std::string> stagnation = {
        "you know", "like i said", "as i mentioned before", "stuff like that"
    };

    int f_hits = 0;
    for (const auto& f : forward) {
        if (contains_term(text, f)) f_hits++;
    }
    int s_hits = 0;
    for (const auto& s : stagnation) {
        if (contains_term(text, s)) s_hits++;
    }

    float base = 0.40f + f_hits * 0.18f - s_hits * 0.15f;
    return std::clamp(base, 0.0f, 1.0f);
}

NarrativeScorecard NarrativeArcCoherenceEngine::evaluate(const std::string& answer, uint16_t turn) {
    (void)turn;
    NarrativeScorecard sc{};
    sc.coherence_score = 1.0f; // clean within single turn context
    sc.theme_stability = 0.85f;
    sc.climax_score    = score_climax(answer);
    sc.momentum_score  = score_momentum(answer);

    sc.narrative_coherence_index =
        (sc.coherence_score * 0.35f) +
        (sc.theme_stability * 0.25f) +
        (sc.climax_score    * 0.25f) +
        (sc.momentum_score  * 0.15f);
    sc.narrative_coherence_index = std::clamp(sc.narrative_coherence_index, 0.0f, 1.0f);

    if      (sc.narrative_coherence_index >= 0.75f) sc.narrative_grade = 1; // Exemplary
    else if (sc.narrative_coherence_index >= 0.58f) sc.narrative_grade = 2; // Coherent
    else if (sc.narrative_coherence_index >= 0.40f) sc.narrative_grade = 3; // Fragmented
    else                                            sc.narrative_grade = 4; // Contradictory

    sync_to_amsv(sc);
    return sc;
}

void NarrativeArcCoherenceEngine::sync_to_amsv(const NarrativeScorecard& sc) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Upper 32 bits of 0x30 (Offset 0x34): [coherence_q16 | climax_q16]
    uint64_t current = sv_->maio_global_state_alpha.load(std::memory_order_relaxed);
    uint64_t updated = (current & 0x00000000FFFFFFFFULL) |
                       (static_cast<uint64_t>(to_q16(sc.climax_score)) << 48) |
                       (static_cast<uint64_t>(to_q16(sc.coherence_score)) << 32);

    sv_->maio_global_state_alpha.store(updated, std::memory_order_release);
}

} // namespace solorock::nace

extern "C" {
    int32_t nace_cpp_evaluate(
        const char* answer, uint16_t turn,
        solorock::nace::NarrativeScorecard* out
    ) {
        if (!answer || !out) return -1;
        solorock::nace::NarrativeArcCoherenceEngine engine(nullptr);
        *out = engine.evaluate(answer, turn);
        return 0;
    }
}
