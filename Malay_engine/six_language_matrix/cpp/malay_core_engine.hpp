// Malay Core Engine C++20 Header
// Zero-Bridge physical memory synchronization with the 64-byte Atomic State Vector.
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <string_view>

namespace malay_engine {

#pragma pack(push, 1)
struct alignas(64) AtomicMemoryStateVector {
    uint64_t vce_phoneme_state;       // 0x00
    uint64_t vce_prosody_state;       // 0x08
    uint16_t cognitive_scores[8];     // 0x10 - 0x1F
    uint64_t rsse_scenario_state;     // 0x20
    uint64_t aeee_exam_state;         // 0x28
    uint64_t global_structural_state; // 0x30
    uint64_t attention_directives;    // 0x38
};
#pragma pack(pop)

static_assert(sizeof(AtomicMemoryStateVector) == 64, "AMSV must be exactly 64 bytes");

struct TrieNode {
    bool is_terminal = false;
    uint32_t frequency = 0;
    std::unordered_map<char, std::unique_ptr<TrieNode>> children;
};

class MalayCoreEngineCpp {
public:
    explicit MalayCoreEngineCpp(AtomicMemoryStateVector* shared_amsv = nullptr);
    ~MalayCoreEngineCpp() = default;

    void insert_lexicon_entry(std::string_view word, uint32_t freq);
    bool lookup_word(std::string_view word, uint32_t* out_freq = nullptr) const;
    uint32_t compute_edit_distance(std::string_view s1, std::string_view s2) const;
    void sync_to_amsv(float structural_score, float register_score);
    AtomicMemoryStateVector* get_amsv_pointer() const { return amsv_; }

private:
    std::unique_ptr<TrieNode> root_;
    AtomicMemoryStateVector* amsv_;
    alignas(64) AtomicMemoryStateVector internal_amsv_{};
};

} // namespace malay_engine
