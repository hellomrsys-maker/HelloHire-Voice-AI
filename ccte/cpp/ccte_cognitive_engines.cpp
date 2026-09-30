/**
 * @file ccte_cognitive_engines.cpp
 * @brief Implementation and C ABI exports for the CCTE Cognitive Engines.
 */

#include "ccte_cognitive_engines.hpp"

static solorock::ccte::CognitiveCapabilityCoordinator* g_ccte_instance = nullptr;

extern "C" {

void ccte_init() {
    if (!g_ccte_instance) {
        g_ccte_instance = new solorock::ccte::CognitiveCapabilityCoordinator();
    }
}

void ccte_sync_scores(void* amsv_state_vector, const float* scores_8) {
    if (g_ccte_instance && amsv_state_vector && scores_8) {
        auto* sv = reinterpret_cast<solorock::amsv::AtomicStateVector*>(amsv_state_vector);
        g_ccte_instance->synchronize_to_amsv(sv, scores_8);
    }
}

float ccte_eval_thinking(int steps) {
    if (!g_ccte_instance) ccte_init();
    std::vector<std::string> dummy_steps(steps, "arg_step");
    return g_ccte_instance->thinking.evaluate_reasoning(dummy_steps).composite_score;
}

float ccte_eval_focus(float consistency, float pause_var, float dur) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->concentration.evaluate_focus(consistency, pause_var, dur).composite_score;
}

float ccte_eval_memory(int recalled, int total, float latency) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->memory.evaluate_memory(recalled, total, latency).composite_score;
}

float ccte_eval_creativity(int clusters, float dist) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->creativity.evaluate_creativity(clusters, dist).composite_score;
}

float ccte_eval_imagination(int branches, float sensory) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->imagination.evaluate_imagination(branches, sensory).composite_score;
}

float ccte_eval_analytical(int valid, int fallacies, float evidence) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->analytical.evaluate_critical_thinking(valid != 0, fallacies, evidence).composite_score;
}

float ccte_eval_verbal(int depth, float coherence, int gaps) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->verbal_reasoning.evaluate_verbal_reasoning(depth, coherence, gaps).composite_score;
}

float ccte_eval_emotional(float tremor, float shimmer, float jitter) {
    if (!g_ccte_instance) ccte_init();
    return g_ccte_instance->emotional.evaluate_emotional_state(tremor, shimmer, jitter).composite_score;
}

void ccte_shutdown() {
    delete g_ccte_instance;
    g_ccte_instance = nullptr;
}

}
