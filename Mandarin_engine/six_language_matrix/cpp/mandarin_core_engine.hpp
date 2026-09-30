// Mandarin Core Engine C++20 Header
// Zero-Bridge physical memory synchronization with Atomic Memory State Vector (AMSV)
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <string_view>

namespace mandarin_engine {

#pragma pack(push, 1)
struct alignas(64) AtomicMemoryStateVector {
    uint64_t vce_phoneme_state;      // 0x00: Syllable Tone, Pinyin Tone, Accuracy Q16
    uint64_t vce_prosody_state;      // 0x08: F0 pitch contour, speech rate (chars/s), fluency Q16
    uint16_t cognitive_scores[8];    // 0x10 - 0x1F: 8 Cognitive capabilities
    uint64_t rsse_scenario_state;    // 0x20: Pragmatic scenario, Mianzi (Face), Politeness Q16
    uint64_t aeee_exam_state;        // 0x28: HSK Exam proficiency state Q16
    uint64_t global_structural_state;// 0x30: SVO, Topic-Comment & Aspect particles Q16
    uint64_t attention_directives;   // 0x38: Focus mask & editorial directives
};
#pragma pack(pop)

static_assert(sizeof(AtomicMemoryStateVector) == 64, "AMSV must be exactly 64 bytes");

struct MandarinTrieNode {
    bool is_terminal = false;
    uint32_t frequency = 0;
    std::string pos_tag;
    std::unordered_map<std::string, std::unique_ptr<MandarinTrieNode>> children;
};

class MandarinCoreEngineCpp {
public:
    explicit MandarinCoreEngineCpp(AtomicMemoryStateVector* shared_amsv = nullptr);
    ~MandarinCoreEngineCpp() = default;

    void insert_lexicon_entry(std::string_view surface, std::string_view pos, uint32_t freq);
    bool lookup_lexicon_entry(std::string_view surface, std::string* out_pos = nullptr, uint32_t* out_freq = nullptr) const;

    // SIMD/AVX accelerated character edit distance
    uint32_t compute_edit_distance(std::string_view s1, std::string_view s2) const;

    // Zero-nanosecond AMSV sync
    void sync_to_amsv(float structural_score, float pragmatic_face_score);
    AtomicMemoryStateVector* get_amsv_pointer() const { return amsv_; }

private:
    std::unique_ptr<MandarinTrieNode> root_;
    AtomicMemoryStateVector* amsv_;
    alignas(64) AtomicMemoryStateVector internal_amsv_{};
};

} // namespace mandarin_engine
