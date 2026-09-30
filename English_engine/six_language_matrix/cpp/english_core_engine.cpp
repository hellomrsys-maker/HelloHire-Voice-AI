// English Core Engine C++20 Implementation
#include "english_core_engine.hpp"
#include <algorithm>
#include <cstring>

namespace english_engine {

EnglishCoreEngineCpp::EnglishCoreEngineCpp(AtomicMemoryStateVector* shared_amsv)
    : root_(std::make_unique<TrieNode>()),
      amsv_(shared_amsv ? shared_amsv : &internal_amsv_) {
    if (!shared_amsv) {
        std::memset(&internal_amsv_, 0, sizeof(AtomicMemoryStateVector));
    }
}

void EnglishCoreEngineCpp::insert_lexicon_entry(std::string_view word, uint32_t freq) {
    TrieNode* curr = root_.get();
    for (char c : word) {
        char lower_c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        if (!curr->children[lower_c]) {
            curr->children[lower_c] = std::make_unique<TrieNode>();
        }
        curr = curr->children[lower_c].get();
    }
    curr->is_terminal = true;
    curr->frequency = freq;
}

bool EnglishCoreEngineCpp::lookup_word(std::string_view word, uint32_t* out_freq) const {
    const TrieNode* curr = root_.get();
    for (char c : word) {
        char lower_c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        auto it = curr->children.find(lower_c);
        if (it == curr->children.end()) {
            return false;
        }
        curr = it->second.get();
    }
    if (curr->is_terminal) {
        if (out_freq) *out_freq = curr->frequency;
        return true;
    }
    return false;
}

uint32_t EnglishCoreEngineCpp::compute_edit_distance(std::string_view s1, std::string_view s2) const {
    const size_t m = s1.size();
    const size_t n = s2.size();
    std::vector<uint32_t> prev(n + 1), curr(n + 1);

    for (size_t j = 0; j <= n; ++j) prev[j] = static_cast<uint32_t>(j);

    for (size_t i = 1; i <= m; ++i) {
        curr[0] = static_cast<uint32_t>(i);
        for (size_t j = 1; j <= n; ++j) {
            if (s1[i - 1] == s2[j - 1]) {
                curr[j] = prev[j - 1];
            } else {
                curr[j] = 1 + std::min({prev[j], curr[j - 1], prev[j - 1]});
            }
        }
        prev = curr;
    }
    return prev[n];
}

void EnglishCoreEngineCpp::sync_to_amsv(float structural_score, float register_score) {
    uint16_t struct_q16 = static_cast<uint16_t>(std::clamp(structural_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t reg_q16 = static_cast<uint16_t>(std::clamp(register_score, 0.0f, 1.0f) * 65535.0f);
    
    // Direct zero-nanosecond synchronous memory write
    uint64_t packed = (static_cast<uint64_t>(struct_q16) << 32) | (static_cast<uint64_t>(reg_q16) << 48);
    amsv_->global_structural_state = packed;
}

} // namespace english_engine
