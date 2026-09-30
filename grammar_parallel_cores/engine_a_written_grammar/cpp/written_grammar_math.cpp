/**
 * written_grammar_math.cpp - Engine A Sub-Core A3 (C++20)
 * Implementation of fast syntax metrics and zero-bridge AMSV mapping.
 */

#include "written_grammar_math.hpp"
#include <algorithm>
#include <cmath>
#include <unordered_set>

namespace solorock::grammar::engine_a {

WrittenGrammarMetrics WrittenGrammarMathEngine::compute_syntax_metrics(std::string_view text) noexcept {
    if (text.empty()) {
        return WrittenGrammarMetrics{0, 0, 0.0f, 0.0f, 0, 0};
    }

    uint32_t words = 0;
    uint32_t sentences = 0;
    bool in_word = false;
    uint32_t commas = 0;
    uint32_t semicolons = 0;

    for (char c : text) {
        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
            if (in_word) {
                words++;
                in_word = false;
            }
        } else {
            in_word = true;
        }

        if (c == '.' || c == '!' || c == '?') {
            sentences++;
        } else if (c == ',') {
            commas++;
        } else if (c == ';') {
            semicolons++;
        }
    }

    if (in_word) {
        words++;
    }
    if (sentences == 0 && words > 0) {
        sentences = 1;
    }

    // Syntactic depth heuristic based on clausal punctuation density
    float words_per_sent = (sentences > 0) ? static_cast<float>(words) / sentences : 0.0f;
    float clause_density = (sentences > 0) ? static_cast<float>(commas + semicolons * 2) / sentences : 0.0f;
    float depth = std::min(10.0f, 1.0f + 0.1f * words_per_sent + 0.3f * clause_density);

    // Approximate Type-Token Ratio
    float ttr = (words > 0) ? std::min(1.0f, 2.5f / std::sqrt(static_cast<float>(words))) : 0.0f;

    // Normalization to Q16
    float struct_norm = std::clamp((depth / 6.0f) * 0.5f + (words_per_sent / 25.0f) * 0.5f, 0.0f, 1.0f);
    float reg_norm = std::clamp(0.4f + ttr * 0.6f, 0.0f, 1.0f);

    uint16_t struct_q16 = static_cast<uint16_t>(struct_norm * 65535.0f);
    uint16_t reg_q16 = static_cast<uint16_t>(reg_norm * 65535.0f);

    return WrittenGrammarMetrics{
        words,
        sentences,
        ttr,
        depth,
        struct_q16,
        reg_q16
    };
}

void WrittenGrammarMathEngine::sync_to_amsv(void* amsv_base_ptr, const WrittenGrammarMetrics& metrics) noexcept {
    if (!amsv_base_ptr) return;

    // Direct physical write to Offset 0x30 (maio_global_state_alpha)
    // Offset 0x34: structural score Q16 (bits 32..47)
    // Offset 0x36: register score Q16 (bits 48..63)
    uint8_t* raw = static_cast<uint8_t*>(amsv_base_ptr);
    std::atomic_ref<uint16_t> struct_ref(*reinterpret_cast<uint16_t*>(raw + 0x34));
    std::atomic_ref<uint16_t> reg_ref(*reinterpret_cast<uint16_t*>(raw + 0x36));

    struct_ref.store(metrics.structure_score_q16, std::memory_order_relaxed);
    reg_ref.store(metrics.register_score_q16, std::memory_order_relaxed);
}

} // namespace solorock::grammar::engine_a
