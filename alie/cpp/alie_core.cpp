/**
 * @file alie_core.cpp
 * @brief Implementation of Active Listening Intelligence Engine (ALIE).
 */

#include "alie_core.hpp"
#include <sstream>
#include <set>
#include <numeric>

namespace solorock::alie {

ActiveListeningIntelligenceEngine::ActiveListeningIntelligenceEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

// ─── Helper: tokenise lowercase ────────────────────────────────────────────
static std::vector<std::string> tokenise(const std::string& text) {
    std::vector<std::string> tokens;
    std::istringstream iss(text);
    std::string word;
    while (iss >> word) {
        std::string w;
        for (char c : word)
            if (std::isalpha(static_cast<unsigned char>(c)))
                w += std::tolower(static_cast<unsigned char>(c));
        if (!w.empty()) tokens.push_back(w);
    }
    return tokens;
}

// ─── Helper: Jaccard overlap ───────────────────────────────────────────────
static float jaccard(const std::vector<std::string>& a, const std::vector<std::string>& b) {
    std::set<std::string> sa(a.begin(), a.end()), sb(b.begin(), b.end());
    int intersect = 0;
    for (const auto& w : sa)
        if (sb.count(w)) ++intersect;
    int uni = static_cast<int>(sa.size() + sb.size()) - intersect;
    return (uni == 0) ? 0.0f : static_cast<float>(intersect) / static_cast<float>(uni);
}

ReferentialAlignmentMetrics ActiveListeningIntelligenceEngine::compute_alignment(
    const std::string& q, const std::string& a
) const {
    ReferentialAlignmentMetrics m{};
    auto qtok = tokenise(q);
    auto atok = tokenise(a);

    // Lexical mirroring: Jaccard similarity between question and answer vocabulary
    m.lexical_mirror_score = std::clamp(jaccard(qtok, atok) * 3.0f, 0.0f, 1.0f);

    // Pronoun echo: question uses "you/your" → answer uses "I/my/we"
    bool q_has_you = (q.find("you") != std::string::npos || q.find("your") != std::string::npos);
    bool a_has_i   = (a.find(" I ") != std::string::npos || a.find("my ") != std::string::npos || a.find("we ") != std::string::npos);
    m.pronoun_echo_rate = (q_has_you && a_has_i) ? 0.95f : 0.40f;

    // Topic frame retention: key content words from question appear in answer
    std::vector<std::string> stopwords = {"the","a","an","is","was","were","in","of","to","and","for","that"};
    int key_hits = 0;
    for (const auto& w : qtok) {
        if (w.size() > 4 && std::find(stopwords.begin(), stopwords.end(), w) == stopwords.end()) {
            if (std::find(atok.begin(), atok.end(), w) != atok.end()) ++key_hits;
        }
    }
    m.topic_frame_retention = std::clamp(0.30f + (key_hits * 0.15f), 0.2f, 1.0f);

    m.composite_score = (m.pronoun_echo_rate * 0.35f) +
                        (m.lexical_mirror_score * 0.35f) +
                        (m.topic_frame_retention * 0.30f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

QARelevanceMetrics ActiveListeningIntelligenceEngine::compute_relevance(
    const std::string& q, const std::string& a
) const {
    QARelevanceMetrics m{};
    auto qtok = tokenise(q);
    auto atok = tokenise(a);

    // On-topic ratio: what fraction of answer tokens share question topics
    std::set<std::string> qtopic(qtok.begin(), qtok.end());
    int on_topic = 0;
    for (const auto& w : atok)
        if (qtopic.count(w)) ++on_topic;
    m.on_topic_ratio = std::clamp(static_cast<float>(on_topic) / static_cast<float>(std::max(1, static_cast<int>(atok.size()))) * 4.0f, 0.1f, 1.0f);

    // Answer completeness: heuristic based on answer length relative to question
    m.answer_completeness = std::clamp(static_cast<float>(atok.size()) / std::max(1.0f, static_cast<float>(qtok.size()) * 3.0f), 0.2f, 1.0f);

    // Specificity: presence of numbers, percentages, proper nouns as specificity proxies
    int spec_markers = 0;
    for (char c : a) if (std::isdigit(static_cast<unsigned char>(c))) { ++spec_markers; break; }
    if (a.find('%') != std::string::npos) ++spec_markers;
    if (a.find("specifically") != std::string::npos || a.find("exactly") != std::string::npos) ++spec_markers;
    m.specificity_score = std::clamp(0.35f + (spec_markers * 0.25f), 0.2f, 1.0f);

    m.composite_score = (m.on_topic_ratio * 0.45f) +
                        (m.answer_completeness * 0.30f) +
                        (m.specificity_score * 0.25f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

float ActiveListeningIntelligenceEngine::compute_latency_score(float latency_ms) const {
    // Optimal thoughtful pause: 800ms – 2200ms
    if (latency_ms >= 800.0f && latency_ms <= 2200.0f) return 1.0f;
    if (latency_ms < 300.0f) return 0.40f; // Rehearsed, not listening
    if (latency_ms < 800.0f) return std::clamp(0.40f + (latency_ms / 800.0f) * 0.60f, 0.4f, 1.0f);
    float excess = latency_ms - 2200.0f;
    return std::clamp(std::exp(-0.00045f * excess), 0.1f, 1.0f);
}

DiscourseRepairMetrics ActiveListeningIntelligenceEngine::compute_repair(const std::string& a) const {
    DiscourseRepairMetrics m{};
    std::string lower = a;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    const std::vector<std::string> repair_cues = {
        "could you clarify", "what do you mean by", "did you mean",
        "can you elaborate", "just to confirm", "are you asking about",
        "let me make sure i understood"
    };
    for (const auto& c : repair_cues) {
        if (lower.find(c) != std::string::npos) ++m.repair_attempts;
    }

    m.comprehension_signal_rate = std::clamp(m.repair_attempts * 0.35f, 0.0f, 1.0f);
    // 1-2 repairs = appropriate; 0 = passive; 3+ = confused
    if (m.repair_attempts == 0) {
        m.repair_appropriateness = 0.60f; // Not probing, not necessarily bad
    } else if (m.repair_attempts <= 2) {
        m.repair_appropriateness = 0.95f; // Ideal active listening signal
    } else {
        m.repair_appropriateness = std::clamp(0.95f - (m.repair_attempts - 2) * 0.20f, 0.3f, 0.95f);
    }

    m.composite_score = (m.repair_appropriateness * 0.6f) + (m.comprehension_signal_rate * 0.4f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

CoReferenceMetrics ActiveListeningIntelligenceEngine::compute_coreference(
    const std::string& a, const std::vector<std::string>& history
) const {
    CoReferenceMetrics m{};
    if (history.empty()) {
        m.cross_turn_entity_fidelity = 0.88f;
        m.narrative_continuity_score = 0.85f;
        m.composite_score = 0.86f;
        return m;
    }

    auto atok = tokenise(a);
    int carried = 0, total_prev = 0;
    for (const auto& prev : history) {
        auto ptok = tokenise(prev);
        for (const auto& w : ptok) {
            if (w.size() >= 5) {
                ++total_prev;
                if (std::find(atok.begin(), atok.end(), w) != atok.end()) ++carried;
            }
        }
    }
    m.entities_carried_forward = carried;
    float retention = (total_prev > 0) ? std::clamp(static_cast<float>(carried) / static_cast<float>(total_prev) * 6.0f, 0.2f, 1.0f) : 0.85f;
    m.cross_turn_entity_fidelity = retention;
    m.narrative_continuity_score = std::clamp(0.40f + retention * 0.55f, 0.3f, 1.0f);

    m.composite_score = (m.cross_turn_entity_fidelity * 0.55f) + (m.narrative_continuity_score * 0.45f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

ListeningIntelligenceScorecard ActiveListeningIntelligenceEngine::evaluate(
    const std::string& question,
    const std::string& answer,
    const std::vector<std::string>& history,
    float latency_ms,
    uint16_t turn
) {
    ListeningIntelligenceScorecard sc{};
    sc.alignment        = compute_alignment(question, answer);
    sc.qa_relevance     = compute_relevance(question, answer);
    sc.latency_to_insight_ms = latency_ms;
    sc.latency_score    = compute_latency_score(latency_ms);
    sc.discourse_repair = compute_repair(answer);
    sc.co_reference     = compute_coreference(answer, history);

    sc.global_listening_index =
        (sc.alignment.composite_score     * 0.25f) +
        (sc.qa_relevance.composite_score  * 0.30f) +
        (sc.latency_score                 * 0.15f) +
        (sc.discourse_repair.composite_score * 0.15f) +
        (sc.co_reference.composite_score  * 0.15f);
    sc.global_listening_index = std::clamp(sc.global_listening_index, 0.0f, 1.0f);

    if (sc.global_listening_index >= 0.80f)      sc.listening_grade = 1;
    else if (sc.global_listening_index >= 0.62f) sc.listening_grade = 2;
    else if (sc.global_listening_index >= 0.44f) sc.listening_grade = 3;
    else                                          sc.listening_grade = 4;

    sync_to_amsv(sc, turn);
    return sc;
}

void ActiveListeningIntelligenceEngine::sync_to_amsv(
    const ListeningIntelligenceScorecard& sc, uint16_t turn
) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };
    // Pack alignment | relevance | latency | repair into ccte_cog_bank_alpha
    uint64_t bank_a = (static_cast<uint64_t>(to_q16(sc.co_reference.composite_score))  << 48) |
                      (static_cast<uint64_t>(to_q16(sc.discourse_repair.composite_score)) << 32) |
                      (static_cast<uint64_t>(to_q16(sc.latency_score))                  << 16) |
                      static_cast<uint64_t>(to_q16(sc.qa_relevance.composite_score));
    sv_->ccte_cog_bank_alpha.store(bank_a, std::memory_order_release);

    // Global listening index into verbal reasoning slot of cog_bank_beta
    uint64_t bank_b = sv_->ccte_cog_bank_beta.load(std::memory_order_relaxed);
    bank_b &= ~0xFFFFULL;
    bank_b |= to_q16(sc.global_listening_index);
    sv_->ccte_cog_bank_beta.store(bank_b, std::memory_order_release);
}

} // namespace solorock::alie

extern "C" {
    int32_t alie_cpp_evaluate(
        const char* question, const char* answer,
        float latency_ms, uint16_t turn,
        solorock::alie::ListeningIntelligenceScorecard* out
    ) {
        if (!question || !answer || !out) return -1;
        solorock::alie::ActiveListeningIntelligenceEngine engine(nullptr);
        std::vector<std::string> empty_hist;
        *out = engine.evaluate(question, answer, empty_hist, latency_ms, turn);
        return 0;
    }
}
