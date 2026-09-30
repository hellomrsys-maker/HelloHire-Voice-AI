/**
 * @file ecse_core.cpp — ECSE Implementation
 */

#include "ecse_core.hpp"
#include <sstream>

namespace solorock::ecse {

EmotionalCommunicationSocialEngine::EmotionalCommunicationSocialEngine(solorock::amsv::AtomicStateVector* sv)
    : sv_(sv) {}

static std::string lower_str(const std::string& s) {
    std::string r = s;
    std::transform(r.begin(), r.end(), r.begin(), ::tolower);
    return r;
}

AffectValenceMetrics EmotionalCommunicationSocialEngine::compute_affect(const std::string& text) const {
    AffectValenceMetrics m{};
    std::string l = lower_str(text);

    const std::vector<const char*> pos_cues = {
        "excited", "thrilled", "passionate", "delighted", "love", "genuinely",
        "absolutely", "fantastic", "proud", "confident", "energized"
    };
    const std::vector<const char*> neg_cues = {
        "unfortunately", "difficult", "struggle", "challenging", "frustrat",
        "anxious", "concerned", "worried", "hesitant", "doubt"
    };

    for (const auto* c : pos_cues) if (l.find(c) != std::string::npos) m.positive_affect += 0.12f;
    for (const auto* c : neg_cues) if (l.find(c) != std::string::npos) m.negative_affect += 0.12f;

    m.positive_affect = std::clamp(m.positive_affect, 0.0f, 1.0f);
    m.negative_affect = std::clamp(m.negative_affect, 0.0f, 1.0f);
    m.neutral_affect = std::clamp(1.0f - m.positive_affect - m.negative_affect, 0.0f, 1.0f);
    m.valence_score = std::clamp(m.positive_affect - m.negative_affect, -1.0f, 1.0f);
    m.composite_score = std::clamp(0.5f + m.valence_score * 0.5f, 0.0f, 1.0f);
    return m;
}

RapportBuildingMetrics EmotionalCommunicationSocialEngine::compute_rapport(const std::string& text) const {
    RapportBuildingMetrics m{};
    std::string l = lower_str(text);

    const std::vector<const char*> warmth = {
        "i appreciate", "thank you for", "that's insightful", "i completely agree",
        "great question", "absolutely", "i understand", "i empathize", "that resonates"
    };
    const std::vector<const char*> collective = {
        "we ", "our team", "together", "collectively", "as a group", "collaborat"
    };

    int w = 0, c = 0;
    for (const auto* cue : warmth) if (l.find(cue) != std::string::npos) ++w;
    for (const auto* cue : collective) if (l.find(cue) != std::string::npos) ++c;

    m.warmth_signal_density = std::clamp(w * 0.22f, 0.0f, 1.0f);
    m.shared_identity_markers = std::clamp(c * 0.20f, 0.0f, 1.0f);
    m.social_bonding_score = std::clamp((m.warmth_signal_density + m.shared_identity_markers) * 0.60f + 0.35f, 0.2f, 1.0f);
    m.composite_score = (m.warmth_signal_density * 0.4f) + (m.shared_identity_markers * 0.2f) + (m.social_bonding_score * 0.4f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

MirrorMatchingMetrics EmotionalCommunicationSocialEngine::compute_mirror(
    const std::string& ans, const std::string& prev_q, float c_wpm, float i_wpm
) const {
    MirrorMatchingMetrics m{};
    // Vocabulary mirror: share key words from interviewer's last turn
    std::string al = lower_str(ans), ql = lower_str(prev_q);
    int hits = 0, total = 0;
    std::istringstream iss(ql);
    std::string word;
    while (iss >> word) {
        if (word.size() >= 5) {
            ++total;
            if (al.find(word) != std::string::npos) ++hits;
        }
    }
    m.vocabulary_mirror_rate = (total > 0) ? std::clamp(static_cast<float>(hits) / total * 3.0f, 0.0f, 1.0f) : 0.5f;

    // Rhythm synchrony: WPM difference < 25 = good mirroring
    float wpm_diff = std::abs(c_wpm - i_wpm);
    m.rhythm_synchrony_score = std::clamp(1.0f - (wpm_diff / 60.0f), 0.2f, 1.0f);
    m.composite_score = (m.vocabulary_mirror_rate * 0.55f) + (m.rhythm_synchrony_score * 0.45f);
    return m;
}

MicroDisagreementMetrics EmotionalCommunicationSocialEngine::compute_disagreement(const std::string& text) const {
    MicroDisagreementMetrics m{};
    std::string l = lower_str(text);

    const std::vector<const char*> hedges = {
        "somewhat", "in a way", "to some extent", "kind of", "sort of",
        "i suppose", "arguably", "not entirely", "it's complicated", "depends"
    };
    for (const auto* h : hedges) if (l.find(h) != std::string::npos) ++m.hedge_count;

    m.disagreement_signal = std::clamp(m.hedge_count * 0.20f, 0.0f, 1.0f);
    m.face_saving_score = (m.hedge_count > 0) ? 0.90f : 1.0f; // polite hedgers save face
    m.composite_score = std::clamp((1.0f - m.disagreement_signal * 0.4f) * m.face_saving_score, 0.0f, 1.0f);
    return m;
}

PolitenessRegisterMetrics EmotionalCommunicationSocialEngine::compute_politeness(const std::string& text) const {
    PolitenessRegisterMetrics m{};
    std::string l = lower_str(text);

    const std::vector<const char*> courtesy = {
        "thank you", "appreciate", "grateful", "please", "certainly", "of course",
        "with respect", "i'd like to", "if i may"
    };
    const std::vector<const char*> crude = {
        "whatever", "don't care", "i couldn't care less", "bluntly"
    };

    int ct = 0, cr = 0;
    for (const auto* c : courtesy) if (l.find(c) != std::string::npos) ++ct;
    for (const auto* c : crude)    if (l.find(c) != std::string::npos) ++cr;

    m.courtesy_markers = std::clamp(ct * 0.20f, 0.0f, 1.0f);
    m.formal_compliance = std::clamp(1.0f - cr * 0.35f, 0.0f, 1.0f);
    m.register_appropriateness = (m.courtesy_markers * 0.4f + m.formal_compliance * 0.6f);
    m.composite_score = std::clamp(m.register_appropriateness, 0.0f, 1.0f);
    return m;
}

SocialCalibrationScorecard EmotionalCommunicationSocialEngine::evaluate(
    const std::string& answer,
    const std::string& interviewer_last_turn,
    float candidate_wpm,
    float interviewer_wpm,
    uint16_t turn
) {
    SocialCalibrationScorecard sc{};
    sc.affect        = compute_affect(answer);
    sc.rapport       = compute_rapport(answer);
    sc.mirror        = compute_mirror(answer, interviewer_last_turn, candidate_wpm, interviewer_wpm);
    sc.micro_disagree = compute_disagreement(answer);
    sc.politeness    = compute_politeness(answer);

    sc.global_social_intelligence =
        (sc.affect.composite_score        * 0.22f) +
        (sc.rapport.composite_score       * 0.25f) +
        (sc.mirror.composite_score        * 0.20f) +
        (sc.micro_disagree.composite_score* 0.15f) +
        (sc.politeness.composite_score    * 0.18f);
    sc.global_social_intelligence = std::clamp(sc.global_social_intelligence, 0.0f, 1.0f);

    if      (sc.global_social_intelligence >= 0.80f) sc.social_grade = 1;
    else if (sc.global_social_intelligence >= 0.63f) sc.social_grade = 2;
    else if (sc.global_social_intelligence >= 0.45f) sc.social_grade = 3;
    else                                              sc.social_grade = 4;

    sync_to_amsv(sc, turn);
    return sc;
}

void EmotionalCommunicationSocialEngine::sync_to_amsv(
    const SocialCalibrationScorecard& sc, uint16_t turn
) noexcept {
    if (!sv_) return;
    auto to_q16 = [](float v) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(v, 0.0f, 1.0f) * 65535.0f);
    };
    uint64_t bank = (static_cast<uint64_t>(to_q16(sc.politeness.composite_score)) << 48) |
                    (static_cast<uint64_t>(to_q16(sc.micro_disagree.composite_score)) << 32) |
                    (static_cast<uint64_t>(to_q16(sc.mirror.composite_score)) << 16) |
                    static_cast<uint64_t>(to_q16(sc.rapport.composite_score));
    sv_->ccte_cog_bank_beta.store(bank, std::memory_order_release);
}

} // namespace solorock::ecse

extern "C" {
    int32_t ecse_cpp_evaluate(
        const char* answer, const char* interviewer_turn,
        float c_wpm, float i_wpm, uint16_t turn,
        solorock::ecse::SocialCalibrationScorecard* out
    ) {
        if (!answer || !interviewer_turn || !out) return -1;
        solorock::ecse::EmotionalCommunicationSocialEngine engine(nullptr);
        *out = engine.evaluate(answer, interviewer_turn, c_wpm, i_wpm, turn);
        return 0;
    }
}
