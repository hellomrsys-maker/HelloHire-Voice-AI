// Arabic Engine — C++20 Core Header
// Implements the zero-overhead physical AMSV layout and hardware synchronization functions.

#ifndef ARABIC_CORE_ENGINE_HPP
#define ARABIC_CORE_ENGINE_HPP

#include <cstdint>
#include <cstring>
#include <string_view>

namespace arabic_engine {

constexpr uint32_t AMSV_MAGIC = 0x41524142; // "ARAB"
constexpr size_t AMSV_SIZE = 64;

#pragma pack(push, 1)
struct alignas(64) ArabicAmsvLayout {
    uint32_t magic_header;            // 0..3: 0x41524142
    uint32_t version;                 // 4..7: 0x00010000
    uint32_t token_count;             // 8..11
    uint32_t sentence_count;          // 12..15
    uint16_t clause_type;             // 16..17: VSO, SVO, Equational
    uint8_t  syntax_flags;            // 18: VSO valid, Deflected valid, Idafa active, Relative
    uint8_t  case_error_flags;        // 19: Nom, Acc, Gen Idafa errors
    uint8_t  phonology_flags;         // 20: Sun letter, Moon letter, Hamza valid
    uint8_t  morphology_flags;        // 21: Verb Form I..X, Broken plural, Dual
    uint8_t  root_class;              // 22: Root identifier index
    uint8_t  pragmatic_flags;         // 23: Islamic greeting, MSA formal, Clash
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

static_assert(sizeof(ArabicAmsvLayout) == 64, "ArabicAmsvLayout must be exactly 64 bytes");

class ArabicCoreEngine {
public:
    ArabicCoreEngine();
    void initialize_buffer(uint8_t* raw_buffer);
    void update_confidence(float confidence, uint8_t* raw_buffer);
    bool check_sun_letter_quick(char32_t utf32_char) const;
};

} // namespace arabic_engine

#endif // ARABIC_CORE_ENGINE_HPP
