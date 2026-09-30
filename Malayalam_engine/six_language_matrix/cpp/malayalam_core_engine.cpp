// Malayalam Core Engine C++20 Implementation
#include "malayalam_core_engine.hpp"
#include <algorithm>
#include <cstring>
#include <cctype>

namespace malayalam_engine {

MalayalamCoreEngineCpp::MalayalamCoreEngineCpp(AtomicMemoryStateVector* shared_amsv)
    : root_(std::make_unique<TrieNode>()),
      amsv_(shared_amsv ? shared_amsv : &internal_amsv_) {
    if (!shared_amsv) {
        std::memset(&internal_amsv_, 0, sizeof(AtomicMemoryStateVector));
    }
}

void MalayalamCoreEngineCpp::insert_lexicon_entry(std::string_view word, uint32_t freq) {
    TrieNode* curr = root_.get();
    for (char c : word) {
        char lc = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        if (!curr->children[lc]) curr->children[lc] = std::make_unique<TrieNode>();
        curr = curr->children[lc].get();
    }
    curr->is_terminal = true;
    curr->frequency = freq;
}

bool MalayalamCoreEngineCpp::lookup_word(std::string_view word, uint32_t* out_freq) const {
    const TrieNode* curr = root_.get();
    for (char c : word) {
        char lc = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        auto it = curr->children.find(lc);
        if (it == curr->children.end()) return false;
        curr = it->second.get();
    }
    if (curr->is_terminal) { if (out_freq) *out_freq = curr->frequency; return true; }
    return false;
}

uint32_t MalayalamCoreEngineCpp::compute_edit_distance(std::string_view s1, std::string_view s2) const {
    const size_t m = s1.size(), n = s2.size();
    std::vector<uint32_t> prev(n + 1), curr(n + 1);
    for (size_t j = 0; j <= n; ++j) prev[j] = static_cast<uint32_t>(j);
    for (size_t i = 1; i <= m; ++i) {
        curr[0] = static_cast<uint32_t>(i);
        for (size_t j = 1; j <= n; ++j) {
            curr[j] = (s1[i - 1] == s2[j - 1]) ? prev[j - 1]
                      : 1 + std::min({prev[j], curr[j - 1], prev[j - 1]});
        }
        prev = curr;
    }
    return prev[n];
}

void MalayalamCoreEngineCpp::sync_to_amsv(float structural_score, float register_score) {
    uint16_t s_q16 = static_cast<uint16_t>(std::clamp(structural_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t r_q16 = static_cast<uint16_t>(std::clamp(register_score, 0.0f, 1.0f) * 65535.0f);
    uint64_t packed = (static_cast<uint64_t>(s_q16) << 32) | (static_cast<uint64_t>(r_q16) << 48);
    amsv_->global_structural_state = packed;
}

} // namespace malayalam_engine
