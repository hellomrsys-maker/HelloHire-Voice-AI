// Korean Engine — C++20 Core Header
// Implements the zero-overhead physical AMSV layout and hardware synchronization functions.

#ifndef KOREAN_CORE_ENGINE_HPP
#define KOREAN_CORE_ENGINE_HPP

#include <cstdint>
#include <cstring>
#include <string_view>

namespace korean_engine {

constexpr uint32_t AMSV_MAGIC = 0x4B4F5245; // "KORE"
constexpr size_t AMSV_SIZE = 64;

#pragma pack(push, 1)
struct alignas(64) KoreanAmsvLayout {
    uint32_t magic_header;            // 0..3: 0x4B4F5245
    uint32_t version;                 // 4..7: 0x00010000
    uint32_t token_count;             // 8..11
    uint32_t sentence_count;          // 12..15
    uint16_t clause_type;             // 16..17: Declarative, Interrogative, etc.
    uint8_t  syntax_flags;            // 18: Head-final, Topic, Subject, Object
    uint8_t  particle_error_flags;    // 19: 은/는, 이/가, 을/를 errors
    uint8_t  phonology_flags;         // 20: Batchim, neutralization applied
    uint8_t  irregular_verb_flags;    // 21: Irregular stem flags
    uint8_t  speech_level_code;       // 22: 1=Hasipsio, 2=Haeyo, etc.
    uint8_t  honorific_concord_flags; // 23: Subject hon, 께서, lexical hon
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

static_assert(sizeof(KoreanAmsvLayout) == 64, "KoreanAmsvLayout must be exactly 64 bytes");

class KoreanCoreEngine {
public:
    KoreanCoreEngine();
    void initialize_buffer(uint8_t* raw_buffer);
    void update_confidence(float confidence, uint8_t* raw_buffer);
    bool check_batchim_quick(char32_t utf32_char) const;
};

} // namespace korean_engine

#endif // KOREAN_CORE_ENGINE_HPP
