/**
 * @file lsce_core.cpp
 * @brief LSCE C++ Real-Time Core Implementation.
 */

#include "lsce_core.hpp"
#include <algorithm>
#include <unordered_set>
#include <sstream>

namespace solorock::lsce {

CognitiveEnduranceEngine::CognitiveEnduranceEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

float CognitiveEnduranceEngine::score_lexical(const std::string& text) const {
    std::unordered_set<std::string> unique_words;
    std::istringstream iss(text);
    std::string token;
    int total = 0;
    while (iss >> token) {
        std::string clean;
        for (char c : token) {
            if (std::isalnum(static_cast<unsigned char>(c))) clean += std::tolower(static_cast<unsigned char>(c));
        }
        if (!clean.empty()) {
            unique_words.insert(clean);
            total++;
        }
    }
    if (total == 0) return 0.5f;
    float ttr = static_cast<float>(unique_words.size()) / static_cast<float>(total);
    return std::clamp(ttr * 1.25f, 0.20f, 1.0f);
}

float CognitiveEnduranceEngine::score_concentration(const std::string& q, const std::string& a) const {
    int q_marks = 0;
    for (char c : q) if (c == '?') q_marks++;
    int sub_prompts = std::max(1, q_marks);

    int words = 0;
    std::istringstream iss(a);
    std::string token;
    while (iss >> token) words++;

    float ratio = static_cast<float>(words) / static_cast<float>(sub_prompts * 25);
    return std::clamp(0.40f + ratio * 0.50f, 0.20f, 1.0f);
}

EnduranceScorecard CognitiveEnduranceEngine::evaluate(const std::string& question, const std::string& answer, uint16_t turn) {
    (void)turn;
    EnduranceScorecard sc{};
    sc.stamina_score    = 0.90f; // Turn-level baseline
    sc.lexical_richness = score_lexical(answer);
    sc.resilience_score = score_concentration(question, answer);
    sc.recovery_score   = 0.85f;

    sc.endurance_index =
        (sc.stamina_score    * 0.35f) +
        (sc.lexical_richness * 0.25f) +
        (sc.resilience_score * 0.25f) +
        (sc.recovery_score   * 0.15f);
    sc.endurance_index = std::clamp(sc.endurance_index, 0.0f, 1.0f);

    if      (sc.endurance_index >= 0.78f) sc.endurance_grade = 1; // Ironclad
    else if (sc.endurance_index >= 0.60f) sc.endurance_grade = 2; // Resilient
    else if (sc.endurance_index >= 0.40f) sc.endurance_grade = 3; // Mild Fatigue
    else                                  sc.endurance_grade = 4; // Exhausted

    sync_to_amsv(sc);
    return sc;
}

void CognitiveEnduranceEngine::sync_to_amsv(const EnduranceScorecard& sc) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };

    // Offset 0x3C: Cross-module attention slot bits [32-47]
    uint64_t current = sv_->maio_global_state_beta.load(std::memory_order_relaxed);
    uint64_t mask = ~(0xFFFFULL << 32);
    uint64_t updated = (current & mask) | (static_cast<uint64_t>(to_q16(sc.stamina_score)) << 32);
    sv_->maio_global_state_beta.store(updated, std::memory_order_release);
}

} // namespace solorock::lsce

extern "C" {
    int32_t lsce_cpp_evaluate(
        const char* question, const char* answer, uint16_t turn,
        solorock::lsce::EnduranceScorecard* out
    ) {
        if (!question || !answer || !out) return -1;
        solorock::lsce::CognitiveEnduranceEngine engine(nullptr);
        *out = engine.evaluate(question, answer, turn);
        return 0;
    }
}
