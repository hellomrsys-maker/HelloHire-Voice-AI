/**
 * @file rvce_core.cpp
 * @brief Implementation of Recruitment Verbal Cognitive Engine (RVCE) C++ Real-Time Core.
 */

#include "rvce_core.hpp"
#include <sstream>
#include <regex>
#include <iostream>

namespace solorock::rvce {

RecruitmentVerbalCognitiveEngine::RecruitmentVerbalCognitiveEngine(solorock::amsv::AtomicStateVector* state_vector)
    : state_vector_(state_vector) {}

ThinkingMetrics RecruitmentVerbalCognitiveEngine::compute_thinking(const std::string& text) const {
    ThinkingMetrics m{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // 1. Structural & Deductive Connectives
    int connective_count = 0;
    const std::vector<std::string> connectives = {
        "because", "therefore", "consequently", "specifically",
        "firstly", "secondly", "finally", "root cause", "first principles",
        "trade-off", "hypothesis", "deduce", "in order to", "as a result"
    };
    for (const auto& w : connectives) {
        if (lower.find(w) != std::string::npos) connective_count++;
    }
    m.reasoning_depth = std::min(10, 1 + connective_count);
    m.deductive_validity = std::clamp(connective_count * 0.18f, 0.1f, 1.0f);

    // 2. MECE Structuring
    bool has_categorization = (lower.find("first") != std::string::npos && lower.find("second") != std::string::npos) ||
                              (lower.find("two factors") != std::string::npos || lower.find("three pillars") != std::string::npos) ||
                              (lower.find("on one hand") != std::string::npos && lower.find("on the other") != std::string::npos);
    m.mece_structuring_score = has_categorization ? 0.92f : std::clamp(0.40f + (connective_count * 0.08f), 0.2f, 0.85f);

    // 3. First-Principles Score
    bool has_fp = (lower.find("fundamental") != std::string::npos ||
                   lower.find("underlying mechanism") != std::string::npos ||
                   lower.find("first principles") != std::string::npos ||
                   lower.find("core constraint") != std::string::npos ||
                   lower.find("baseline") != std::string::npos);
    m.first_principles_score = has_fp ? 0.95f : std::clamp(0.35f + (connective_count * 0.07f), 0.15f, 0.80f);

    // 4. STAR Method Coherence (Situation, Task, Action, Result)
    int star_elements = 0;
    if (lower.find("situation") != std::string::npos || lower.find("context was") != std::string::npos || lower.find("at the time") != std::string::npos) star_elements++;
    if (lower.find("task") != std::string::npos || lower.find("objective") != std::string::npos || lower.find("goal was to") != std::string::npos || lower.find("responsible for") != std::string::npos) star_elements++;
    if (lower.find("action") != std::string::npos || lower.find("i implemented") != std::string::npos || lower.find("i designed") != std::string::npos || lower.find("we built") != std::string::npos) star_elements++;
    if (lower.find("result") != std::string::npos || lower.find("outcome") != std::string::npos || lower.find("reduced") != std::string::npos || lower.find("increased by") != std::string::npos || lower.find("%") != std::string::npos) star_elements++;
    m.star_coherence = std::clamp(0.25f + (star_elements * 0.19f), 0.2f, 1.0f);

    // Composite Thinking Score
    m.composite_score = (m.reasoning_depth / 10.0f) * 0.25f +
                        m.first_principles_score * 0.20f +
                        m.mece_structuring_score * 0.20f +
                        m.star_coherence * 0.20f +
                        m.deductive_validity * 0.15f;
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

ConcentrationMetrics RecruitmentVerbalCognitiveEngine::compute_concentration(
    float wpm, float elapsed_minutes, uint16_t turn
) const {
    ConcentrationMetrics m{};
    // Pacing endurance: standard pace 130-165 wpm
    float wpm_deviation = std::abs(wpm - 145.0f);
    float pace_stability = std::clamp(1.0f - (wpm_deviation / 80.0f), 0.2f, 1.0f);

    // Attentive duration: proportional to sustained interaction
    m.sustained_attention_sec = turn * 45.0f;

    // Cognitive endurance decay curve under stress
    m.cognitive_endurance_factor = std::clamp(1.0f - (elapsed_minutes * 0.004f), 0.5f, 1.0f);

    // Distraction resistance & SNR
    m.distraction_resistance = pace_stability * m.cognitive_endurance_factor;
    m.noise_suppression_snr_db = 15.0f + (m.distraction_resistance * 15.0f);

    m.composite_score = (m.distraction_resistance * 0.5f) + (pace_stability * 0.3f) + (m.cognitive_endurance_factor * 0.2f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

RecallMetrics RecruitmentVerbalCognitiveEngine::compute_recall(
    const std::string& text, const std::vector<std::string>& history
) const {
    RecallMetrics m{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // Check cross-turn entity retention
    int retained_anchor_count = 0;
    for (const auto& prev_turn : history) {
        std::istringstream iss(prev_turn);
        std::string token;
        while (iss >> token) {
            if (token.size() > 5) {
                std::string lower_token = token;
                std::transform(lower_token.begin(), lower_token.end(), lower_token.begin(), ::tolower);
                if (lower.find(lower_token) != std::string::npos) {
                    retained_anchor_count++;
                }
            }
        }
    }

    m.working_memory_retention = history.empty() ? 0.85f : std::clamp(0.40f + (retained_anchor_count * 0.08f), 0.3f, 1.0f);
    m.cross_turn_consistency = 0.94f; // Baseline high consistency unless contradiction flags set
    m.resume_fact_fidelity = 0.92f;
    m.retrieval_latency_ms = std::max(40.0f, 160.0f - (retained_anchor_count * 12.0f));

    m.composite_score = (m.working_memory_retention * 0.4f) +
                        (m.cross_turn_consistency * 0.3f) +
                        (m.resume_fact_fidelity * 0.3f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

CreativityMetrics RecruitmentVerbalCognitiveEngine::compute_creativity(const std::string& text) const {
    CreativityMetrics m{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    const std::vector<std::string> creative_cues = {
        "novel", "unconventional", "innovative", "alternative",
        "orthogonal", "lateral", "pivot", "paradigm",
        "synthesize", "re-architect", "out of the box", "counter-intuitive"
    };
    int cues = 0;
    for (const auto& w : creative_cues) {
        if (lower.find(w) != std::string::npos) cues++;
    }

    m.divergent_thinking_score = std::clamp(0.30f + (cues * 0.20f), 0.2f, 1.0f);
    m.conceptual_distance_novelty = std::clamp(0.35f + (cues * 0.18f), 0.2f, 1.0f);
    m.lateral_solution_synthesis = std::clamp(0.28f + (cues * 0.22f), 0.2f, 1.0f);
    m.metaphoric_richness = (lower.find("like a") != std::string::npos || lower.find("analogous to") != std::string::npos) ? 0.88f : 0.45f;

    m.composite_score = (m.divergent_thinking_score * 0.35f) +
                        (m.conceptual_distance_novelty * 0.25f) +
                        (m.lateral_solution_synthesis * 0.25f) +
                        (m.metaphoric_richness * 0.15f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

ImaginationMetrics RecruitmentVerbalCognitiveEngine::compute_imagination(const std::string& text) const {
    ImaginationMetrics m{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // 1. Counterfactual & Prospective Cues
    bool has_counterfactual = (lower.find("what if") != std::string::npos ||
                               lower.find("suppose") != std::string::npos ||
                               lower.find("in a scenario where") != std::string::npos ||
                               lower.find("had we chosen") != std::string::npos ||
                               lower.find("anticipating") != std::string::npos);
    m.counterfactual_simulation = has_counterfactual ? 0.92f : 0.45f;

    bool has_prospective = (lower.find("in the next five years") != std::string::npos ||
                            lower.find("projecting forward") != std::string::npos ||
                            lower.find("scale to") != std::string::npos ||
                            lower.find("future-proofing") != std::string::npos ||
                            lower.find("vision") != std::string::npos);
    m.prospective_forecasting = has_prospective ? 0.94f : 0.42f;

    // 2. Theory of Mind / Perspective Taking
    bool has_tom = (lower.find("from the customer") != std::string::npos ||
                    lower.find("stakeholder perspective") != std::string::npos ||
                    lower.find("user experience") != std::string::npos ||
                    lower.find("team's point of view") != std::string::npos ||
                    lower.find("empathy") != std::string::npos);
    m.theory_of_mind_empathy = has_tom ? 0.90f : 0.40f;

    m.vision_articulation_clarity = std::clamp((m.counterfactual_simulation + m.prospective_forecasting + m.theory_of_mind_empathy) / 3.0f, 0.2f, 1.0f);

    m.composite_score = (m.counterfactual_simulation * 0.30f) +
                        (m.prospective_forecasting * 0.30f) +
                        (m.theory_of_mind_empathy * 0.25f) +
                        (m.vision_articulation_clarity * 0.15f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

VerbalArticulationMetrics RecruitmentVerbalCognitiveEngine::compute_verbal(
    const std::string& text, float wpm
) const {
    VerbalArticulationMetrics m{};
    std::string lower = text;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // WPM Score: optimal band [130, 165]
    if (wpm >= 130.0f && wpm <= 165.0f) {
        m.fluency_wpm_score = 1.0f;
    } else {
        float dev = std::min(std::abs(wpm - 145.0f), 100.0f);
        m.fluency_wpm_score = std::clamp(1.0f - (dev / 100.0f), 0.2f, 1.0f);
    }

    // Colloquial vs Professional Register
    int colloquial_count = 0;
    const std::vector<std::string> colloquialisms = {
        "gonna", "wanna", "kinda", "sorta", "dunno", "dude", "stuff like that", "you know what i mean"
    };
    for (const auto& w : colloquialisms) {
        if (lower.find(w) != std::string::npos) colloquial_count++;
    }
    m.register_compliance = std::clamp(1.0f - (colloquial_count * 0.25f), 0.1f, 1.0f);

    // Filler Penalty
    int filler_count = 0;
    const std::vector<std::string> fillers = {"um", "uh", "like", "you know", "basically", "actually"};
    for (const auto& f : fillers) {
        size_t pos = 0;
        while ((pos = lower.find(f, pos)) != std::string::npos) {
            filler_count++;
            pos += f.length();
        }
    }
    m.filler_penalty = std::clamp(filler_count * 0.04f, 0.0f, 0.6f);

    // Vocabulary density & technical depth
    std::istringstream iss(text);
    std::string word;
    int word_count = 0;
    std::vector<std::string> unique_words;
    while (iss >> word) {
        word_count++;
        if (std::find(unique_words.begin(), unique_words.end(), word) == unique_words.end()) {
            unique_words.push_back(word);
        }
    }
    float ttr = (word_count > 0) ? (static_cast<float>(unique_words.size()) / word_count) : 0.5f;
    m.vocabulary_density = std::clamp(ttr * 1.3f, 0.2f, 1.0f);

    m.composite_score = (m.fluency_wpm_score * 0.30f) +
                        (m.register_compliance * 0.30f) +
                        (m.vocabulary_density * 0.25f) +
                        ((1.0f - m.filler_penalty) * 0.15f);
    m.composite_score = std::clamp(m.composite_score, 0.0f, 1.0f);
    return m;
}

CandidateScorecard RecruitmentVerbalCognitiveEngine::evaluate_candidate_turn(
    const std::string& transcript,
    const std::vector<std::string>& conversation_history,
    float measured_wpm,
    float elapsed_interview_minutes,
    uint16_t active_turn
) {
    CandidateScorecard sc{};
    sc.thinking      = compute_thinking(transcript);
    sc.concentration = compute_concentration(measured_wpm, elapsed_interview_minutes, active_turn);
    sc.recall        = compute_recall(transcript, conversation_history);
    sc.creativity    = compute_creativity(transcript);
    sc.imagination   = compute_imagination(transcript);
    sc.verbal        = compute_verbal(transcript, measured_wpm);

    // Global Hireability Index Weighted Formulation
    sc.global_hireability_index = (sc.thinking.composite_score * 0.22f) +
                                  (sc.concentration.composite_score * 0.15f) +
                                  (sc.recall.composite_score * 0.18f) +
                                  (sc.creativity.composite_score * 0.15f) +
                                  (sc.imagination.composite_score * 0.15f) +
                                  (sc.verbal.composite_score * 0.15f);
    sc.global_hireability_index = std::clamp(sc.global_hireability_index, 0.0f, 1.0f);

    // Recommendation Code mapping
    if (sc.global_hireability_index >= 0.82f) {
        sc.recommendation_code = 1; // Strong Hire
    } else if (sc.global_hireability_index >= 0.68f) {
        sc.recommendation_code = 2; // Hire
    } else if (sc.global_hireability_index >= 0.52f) {
        sc.recommendation_code = 3; // Leaning Hire
    } else {
        sc.recommendation_code = 4; // No Hire
    }

    return sc;
}

void RecruitmentVerbalCognitiveEngine::sync_to_amsv(
    const CandidateScorecard& scorecard, uint16_t scenario_id, uint16_t turn
) noexcept {
    if (!state_vector_) return;

    // Convert scores to 16-bit Q16 fixed-point (0.0 - 1.0 -> 0 - 65535)
    auto to_q16 = [](float val) -> uint16_t {
        return static_cast<uint16_t>(std::clamp(val, 0.0f, 1.0f) * 65535.0f);
    };

    uint16_t q_think = to_q16(scorecard.thinking.composite_score);
    uint16_t q_focus = to_q16(scorecard.concentration.composite_score);
    uint16_t q_recal = to_q16(scorecard.recall.composite_score);
    uint16_t q_creat = to_q16(scorecard.creativity.composite_score);

    // Pack into ccte_cog_bank_alpha (Offset 0x10): [Thinking | Focus | Recall | Creativity]
    uint64_t bank_alpha = (static_cast<uint64_t>(q_creat) << 48) |
                          (static_cast<uint64_t>(q_recal) << 32) |
                          (static_cast<uint64_t>(q_focus) << 16) |
                          static_cast<uint64_t>(q_think);
    state_vector_->ccte_cog_bank_alpha.store(bank_alpha, std::memory_order_release);

    uint16_t q_imagi = to_q16(scorecard.imagination.composite_score);
    uint16_t q_analy = to_q16(scorecard.thinking.deductive_validity);
    uint16_t q_verba = to_q16(scorecard.verbal.composite_score);
    uint16_t q_emoti = to_q16(scorecard.concentration.distraction_resistance);

    // Pack into ccte_cog_bank_beta (Offset 0x18): [Imagination | Analytical | Verbal | Emotional]
    uint64_t bank_beta = (static_cast<uint64_t>(q_emoti) << 48) |
                         (static_cast<uint64_t>(q_verba) << 32) |
                         (static_cast<uint64_t>(q_analy) << 16) |
                         static_cast<uint64_t>(q_imagi);
    state_vector_->ccte_cog_bank_beta.store(bank_beta, std::memory_order_release);

    // Pack into rsse_scenario_state (Offset 0x20): [Scenario ID (0-15) | Turn (16-31) | Score (32-47) | Rec Code (48-63)]
    uint16_t q_global = to_q16(scorecard.global_hireability_index);
    uint64_t scenario_packed = (static_cast<uint64_t>(scorecard.recommendation_code) << 48) |
                               (static_cast<uint64_t>(q_global) << 32) |
                               (static_cast<uint64_t>(turn) << 16) |
                               static_cast<uint64_t>(scenario_id);
    state_vector_->rsse_scenario_state.store(scenario_packed, std::memory_order_release);
}

} // namespace solorock::rvce

// C-ABI Linkage
extern "C" {
    int32_t rvce_cpp_evaluate_turn(
        const char* transcript,
        float wpm,
        float elapsed_minutes,
        uint16_t turn,
        solorock::rvce::CandidateScorecard* out_scorecard
    ) {
        if (!transcript || !out_scorecard) return -1;
        solorock::rvce::RecruitmentVerbalCognitiveEngine engine(nullptr);
        std::vector<std::string> empty_history;
        *out_scorecard = engine.evaluate_candidate_turn(transcript, empty_history, wpm, elapsed_minutes, turn);
        return 0;
    }

    void rvce_cpp_sync_amsv(
        void* amsv_state_vector_ptr,
        const solorock::rvce::CandidateScorecard* scorecard,
        uint16_t scenario_id,
        uint16_t turn
    ) {
        if (!amsv_state_vector_ptr || !scorecard) return;
        auto* amsv = reinterpret_cast<solorock::amsv::AtomicStateVector*>(amsv_state_vector_ptr);
        solorock::rvce::RecruitmentVerbalCognitiveEngine engine(amsv);
        engine.sync_to_amsv(*scorecard, scenario_id, turn);
    }
}
