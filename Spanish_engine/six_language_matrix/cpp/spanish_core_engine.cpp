// Spanish Core Engine C++20 Implementation
#include "spanish_core_engine.hpp"
#include <algorithm>
#include <cstring>
#include <cmath>

namespace spanish_engine {

SpanishCoreEngineCpp::SpanishCoreEngineCpp(AtomicMemoryStateVector* shared_amsv)
    : root_(std::make_unique<SpanishTrieNode>()),
      amsv_(shared_amsv ? shared_amsv : &internal_amsv_) {
    // Populate high-frequency Spanish baseline lexicon
    insert_lexicon_entry("el", "DET", 300000);
    insert_lexicon_entry("la", "DET", 280000);
    insert_lexicon_entry("los", "DET", 150000);
    insert_lexicon_entry("las", "DET", 140000);
    insert_lexicon_entry("un", "DET", 160000);
    insert_lexicon_entry("una", "DET", 155000);
    insert_lexicon_entry("de", "ADP", 320000);
    insert_lexicon_entry("en", "ADP", 240000);
    insert_lexicon_entry("a", "ADP", 220000);
    insert_lexicon_entry("al", "ADP", 90000);
    insert_lexicon_entry("del", "ADP", 95000);
    insert_lexicon_entry("por", "ADP", 130000);
    insert_lexicon_entry("para", "ADP", 125000);
    insert_lexicon_entry("con", "ADP", 110000);
    insert_lexicon_entry("que", "SCONJ", 290000);
    insert_lexicon_entry("no", "ADV", 200000);
    insert_lexicon_entry("si", "SCONJ", 100000);
    insert_lexicon_entry("y", "CCONJ", 210000);
    insert_lexicon_entry("pero", "CCONJ", 95000);
    insert_lexicon_entry("es", "AUX", 250000);
    insert_lexicon_entry("son", "AUX", 120000);
    insert_lexicon_entry("está", "AUX", 140000);
    insert_lexicon_entry("están", "AUX", 85000);
    insert_lexicon_entry("ser", "AUX", 115000);
    insert_lexicon_entry("estar", "AUX", 105000);
    insert_lexicon_entry("haber", "AUX", 95000);
    insert_lexicon_entry("tener", "VERB", 98000);
    insert_lexicon_entry("hacer", "VERB", 92000);
    insert_lexicon_entry("hablar", "VERB", 60000);
    insert_lexicon_entry("estudiar", "VERB", 50000);
    insert_lexicon_entry("escribir", "VERB", 48000);
    insert_lexicon_entry("yo", "PRON", 110000);
    insert_lexicon_entry("tú", "PRON", 75000);
    insert_lexicon_entry("él", "PRON", 85000);
    insert_lexicon_entry("ella", "PRON", 80000);
    insert_lexicon_entry("nosotros", "PRON", 65000);
    insert_lexicon_entry("ellos", "PRON", 70000);
    insert_lexicon_entry("usted", "PRON", 72000);
    insert_lexicon_entry("ustedes", "PRON", 68000);
    insert_lexicon_entry("se", "PRON", 180000);
    insert_lexicon_entry("me", "PRON", 130000);
    insert_lexicon_entry("te", "PRON", 90000);
    insert_lexicon_entry("lo", "PRON", 125000);
    insert_lexicon_entry("la", "PRON", 120000);
    insert_lexicon_entry("le", "PRON", 115000);
}

void SpanishCoreEngineCpp::insert_lexicon_entry(std::string_view surface, std::string_view pos, uint32_t freq) {
    SpanishTrieNode* curr = root_.get();
    for (char c : surface) {
        if (!curr->children[c]) {
            curr->children[c] = std::make_unique<SpanishTrieNode>();
        }
        curr = curr->children[c].get();
    }
    curr->is_terminal = true;
    curr->pos_tag = std::string(pos);
    curr->frequency = freq;
}

bool SpanishCoreEngineCpp::lookup_lexicon_entry(std::string_view surface, std::string* out_pos, uint32_t* out_freq) const {
    const SpanishTrieNode* curr = root_.get();
    for (char c : surface) {
        auto it = curr->children.find(c);
        if (it == curr->children.end()) {
            return false;
        }
        curr = it->second.get();
    }
    if (curr->is_terminal) {
        if (out_pos) *out_pos = curr->pos_tag;
        if (out_freq) *out_freq = curr->frequency;
        return true;
    }
    return false;
}

uint32_t SpanishCoreEngineCpp::compute_edit_distance(std::string_view s1, std::string_view s2) const {
    const size_t m = s1.size();
    const size_t n = s2.size();
    std::vector<std::vector<uint32_t>> dp(m + 1, std::vector<uint32_t>(n + 1, 0));

    for (size_t i = 0; i <= m; ++i) dp[i][0] = static_cast<uint32_t>(i);
    for (size_t j = 0; j <= n; ++j) dp[0][j] = static_cast<uint32_t>(j);

    for (size_t i = 1; i <= m; ++i) {
        for (size_t j = 1; j <= n; ++j) {
            uint32_t cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            dp[i][j] = std::min({
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            });
        }
    }
    return dp[m][n];
}

void SpanishCoreEngineCpp::sync_to_amsv(float structural_score, float mood_score) {
    if (!amsv_) return;
    // Pack Q16 fixed point values
    uint16_t struct_q16 = static_cast<uint16_t>(std::clamp(structural_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t mood_q16 = static_cast<uint16_t>(std::clamp(mood_score, 0.0f, 1.0f) * 65535.0f);

    uint64_t packed = (static_cast<uint64_t>(struct_q16) << 32) | static_cast<uint64_t>(mood_q16);
    amsv_->global_structural_state = packed;

    // Capability 1: Grammar/Syntax
    amsv_->cognitive_scores[1] = struct_q16;
}

} // namespace spanish_engine
