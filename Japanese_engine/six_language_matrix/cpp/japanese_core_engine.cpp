// Japanese Core Engine C++20 Implementation
#include "japanese_core_engine.hpp"
#include <algorithm>
#include <cstring>
#include <cmath>

namespace japanese_engine {

JapaneseCoreEngineCpp::JapaneseCoreEngineCpp(AtomicMemoryStateVector* shared_amsv)
    : root_(std::make_unique<JapaneseTrieNode>()),
      amsv_(shared_amsv ? shared_amsv : &internal_amsv_) {
    // Populate baseline UniDic/IPA core vocabulary
    insert_morpheme("私", "Meishi", 50000);
    insert_morpheme("日本", "Meishi", 85000);
    insert_morpheme("は", "Joshi", 120000);
    insert_morpheme("が", "Joshi", 110000);
    insert_morpheme("を", "Joshi", 95000);
    insert_morpheme("に", "Joshi", 90000);
    insert_morpheme("で", "Joshi", 75000);
    insert_morpheme("です", "Jodoushi", 80000);
    insert_morpheme("ます", "Jodoushi", 82000);
    insert_morpheme("だ", "Jodoushi", 70000);
    insert_morpheme("である", "Jodoushi", 65000);
    insert_morpheme("食べる", "Doushi", 40000);
    insert_morpheme("行く", "Doushi", 45000);
}

void JapaneseCoreEngineCpp::insert_morpheme(std::string_view surface, std::string_view pos, uint32_t freq) {
    JapaneseTrieNode* curr = root_.get();
    std::string key(surface);
    // Simple UTF-8 character insertion
    size_t i = 0;
    while (i < key.size()) {
        size_t char_len = 1;
        unsigned char c = static_cast<unsigned char>(key[i]);
        if ((c & 0x80) == 0) char_len = 1;
        else if ((c & 0xE0) == 0xC0) char_len = 2;
        else if ((c & 0xF0) == 0xE0) char_len = 3;
        else if ((c & 0xF8) == 0xF0) char_len = 4;

        std::string ch = key.substr(i, char_len);
        if (!curr->children[ch]) {
            curr->children[ch] = std::make_unique<JapaneseTrieNode>();
        }
        curr = curr->children[ch].get();
        i += char_len;
    }
    curr->is_terminal = true;
    curr->pos_tag = std::string(pos);
    curr->frequency = freq;
}

bool JapaneseCoreEngineCpp::lookup_morpheme(std::string_view surface, std::string* out_pos, uint32_t* out_freq) const {
    const JapaneseTrieNode* curr = root_.get();
    std::string key(surface);
    size_t i = 0;
    while (i < key.size()) {
        size_t char_len = 1;
        unsigned char c = static_cast<unsigned char>(key[i]);
        if ((c & 0x80) == 0) char_len = 1;
        else if ((c & 0xE0) == 0xC0) char_len = 2;
        else if ((c & 0xF0) == 0xE0) char_len = 3;
        else if ((c & 0xF8) == 0xF0) char_len = 4;

        std::string ch = key.substr(i, char_len);
        auto it = curr->children.find(ch);
        if (it == curr->children.end()) {
            return false;
        }
        curr = it->second.get();
        i += char_len;
    }
    if (curr->is_terminal) {
        if (out_pos) *out_pos = curr->pos_tag;
        if (out_freq) *out_freq = curr->frequency;
        return true;
    }
    return false;
}

uint32_t JapaneseCoreEngineCpp::compute_edit_distance(std::string_view s1, std::string_view s2) const {
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

void JapaneseCoreEngineCpp::sync_to_amsv(float structural_score, float formality_score) {
    if (!amsv_) return;
    // Pack Q16 fixed point values
    uint16_t struct_q16 = static_cast<uint16_t>(std::clamp(structural_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t form_q16 = static_cast<uint16_t>(std::clamp(formality_score, 0.0f, 1.0f) * 65535.0f);

    uint64_t packed = (static_cast<uint64_t>(struct_q16) << 32) | static_cast<uint64_t>(form_q16);
    amsv_->global_structural_state = packed;

    // Capability 1: Grammar/Syntax
    amsv_->cognitive_scores[1] = struct_q16;
}

} // namespace japanese_engine
