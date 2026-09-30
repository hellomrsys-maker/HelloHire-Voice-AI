// Mandarin Core Engine C++20 Implementation
#include "mandarin_core_engine.hpp"
#include <algorithm>
#include <cstring>
#include <cmath>

namespace mandarin_engine {

MandarinCoreEngineCpp::MandarinCoreEngineCpp(AtomicMemoryStateVector* shared_amsv)
    : root_(std::make_unique<MandarinTrieNode>()),
      amsv_(shared_amsv ? shared_amsv : &internal_amsv_) {
    // Populate high-frequency Mandarin baseline lexicon
    insert_lexicon_entry("我", "PN", 150000);
    insert_lexicon_entry("你", "PN", 130000);
    insert_lexicon_entry("他", "PN", 120000);
    insert_lexicon_entry("是", "VC", 200000);
    insert_lexicon_entry("在", "P", 160000);
    insert_lexicon_entry("有", "VE", 140000);
    insert_lexicon_entry("个", "M", 180000);
    insert_lexicon_entry("本", "M", 60000);
    insert_lexicon_entry("张", "M", 55000);
    insert_lexicon_entry("只", "M", 50000);
    insert_lexicon_entry("条", "M", 45000);
    insert_lexicon_entry("了", "AS", 190000);
    insert_lexicon_entry("着", "AS", 70000);
    insert_lexicon_entry("过", "AS", 65000);
    insert_lexicon_entry("的", "DEG", 250000);
    insert_lexicon_entry("地", "DEV", 80000);
    insert_lexicon_entry("得", "SP", 75000);
    insert_lexicon_entry("吗", "SP", 90000);
    insert_lexicon_entry("好", "VA", 110000);
    insert_lexicon_entry("老师", "NN", 85000);
    insert_lexicon_entry("学生", "NN", 80000);
    insert_lexicon_entry("中国", "NR", 95000);
    insert_lexicon_entry("北京", "NR", 70000);
    insert_lexicon_entry("谢谢", "VV", 90000);
    insert_lexicon_entry("请", "VV", 88000);
    insert_lexicon_entry("把", "BA", 60000);
    insert_lexicon_entry("被", "LB", 50000);
}

void MandarinCoreEngineCpp::insert_lexicon_entry(std::string_view surface, std::string_view pos, uint32_t freq) {
    MandarinTrieNode* curr = root_.get();
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
        if (!curr->children[ch]) {
            curr->children[ch] = std::make_unique<MandarinTrieNode>();
        }
        curr = curr->children[ch].get();
        i += char_len;
    }
    curr->is_terminal = true;
    curr->pos_tag = std::string(pos);
    curr->frequency = freq;
}

bool MandarinCoreEngineCpp::lookup_lexicon_entry(std::string_view surface, std::string* out_pos, uint32_t* out_freq) const {
    const MandarinTrieNode* curr = root_.get();
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

uint32_t MandarinCoreEngineCpp::compute_edit_distance(std::string_view s1, std::string_view s2) const {
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

void MandarinCoreEngineCpp::sync_to_amsv(float structural_score, float pragmatic_face_score) {
    if (!amsv_) return;
    // Pack Q16 fixed point values
    uint16_t struct_q16 = static_cast<uint16_t>(std::clamp(structural_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t face_q16 = static_cast<uint16_t>(std::clamp(pragmatic_face_score, 0.0f, 1.0f) * 65535.0f);

    uint64_t packed = (static_cast<uint64_t>(struct_q16) << 32) | static_cast<uint64_t>(face_q16);
    amsv_->global_structural_state = packed;

    // Capability 1: Grammar/Syntax
    amsv_->cognitive_scores[1] = struct_q16;
    // Capability 3: Pragmatic / Face preservation
    amsv_->cognitive_scores[3] = face_q16;
}

} // namespace mandarin_engine
