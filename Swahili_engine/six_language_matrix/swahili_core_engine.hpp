// Swahili Engine — C++20 Core Header
// Implements the zero-overhead physical AMSV layout and hardware synchronization functions.

#ifndef SWAHILI_CORE_ENGINE_HPP
#define SWAHILI_CORE_ENGINE_HPP

#include <cstdint>
#include <cstring>
#include <string_view>

namespace swahili_engine {

constexpr uint32_t AMSV_MAGIC = 0x53574148; // "SWAH"
constexpr size_t AMSV_SIZE = 64;

#pragma pack(push, 1)
struct alignas(64) SwahiliAmsvLayout {
    uint32_t magic_header;            // 0..3: 0x53574148
    uint32_t version;                 // 4..7: 0x00010000
    uint32_t token_count;             // 8..11
    uint32_t sentence_count;          // 12..15
    uint16_t clause_type;             // 16..17: Declarative SVO, etc.
    uint8_t  syntax_flags;            // 18: SVO, Pro-drop, Has OP, Relative
    uint8_t  concord_error_flags;     // 19: Adj, Dem, Verb SP, OP errors
    uint8_t  phonology_flags;         // 20: Monosyllabic ku-, Penultimate stress
    uint8_t  verbal_extension_flags;  // 21: Applicative, Causative, Passive, Reciprocal
    uint8_t  noun_class_head;         // 22: Detected noun class (1..18)
    uint8_t  pragmatic_flags;         // 23: Shikamoo, Marahaba, Clash
    float    sub_ai_confidence;       // 24..27: Confidence score
    uint32_t syntax_latency_ns;       // 28..31
    uint32_t morph_latency_ns;        // 32..35
    uint8_t  reserved[12];            // 36..47
    uint32_t crc32_checksum;          // 48..51
    uint8_t  syntax_sub_ai_id;        // 52
    uint8_t  phonology_sub_ai_id;     // 53
    uint8_t  pragmatic_sub_ai_id;     // 54
    uint8_t  editorial_sub_ai_id;     // 55
    uint64_t timestamp_epoch_ns;       // 56..63
};
#pragma pack(pop)

static_assert(sizeof(SwahiliAmsvLayout) == 64, "SwahiliAmsvLayout must be exactly 64 bytes");

class SwahiliCoreEngine {
public:
    SwahiliCoreEngine();
    void initialize_buffer(uint8_t* raw_buffer);
    void update_confidence(float confidence, uint8_t* raw_buffer);
    bool check_concord_quick(uint8_t noun_class, uint8_t verb_sp_class) const;
};

} // namespace swahili_engine

#endif // SWAHILI_CORE_ENGINE_HPP
