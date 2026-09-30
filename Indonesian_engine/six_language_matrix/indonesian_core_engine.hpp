// Indonesian Engine — C++20 Core Engine Header
// High-throughput surveillance loop, voice affixation, and 64-byte AMSV alignment.

#pragma once

#include <cstdint>
#include <cstddef>
#include <string_view>

namespace solo_rock::indonesian {

constexpr uint32_t INDONESIAN_AMSV_MAGIC = 0x494E444F; // "INDO"
constexpr size_t INDONESIAN_AMSV_SIZE = 64;

#pragma pack(push, 1)
struct alignas(64) IndonesianAMSV {
    uint32_t magic;             // 0..3: 0x494E444F
    uint32_t version;           // 4..7: 0x00010000
    uint32_t token_count;       // 8..11
    uint32_t sentence_count;    // 12..15
    uint16_t clause_type_mask;  // 16..17
    uint8_t  syntax_flags;      // 18
    uint8_t  morphology_flags;  // 19
    uint8_t  phonology_flags;   // 20
    uint8_t  aspect_flags;      // 21
    uint8_t  register_tier;     // 22
    uint8_t  pragmatic_flags;   // 23
    float    confidence_score;  // 24..27
    uint8_t  reserved[24];      // 28..51
    uint8_t  sub_ai_active[4];  // 52..55: Syntax, Phonology, Pragmatic, Editorial
    uint64_t tail_checksum;     // 56..63
};
#pragma pack(pop)

static_assert(sizeof(IndonesianAMSV) == 64, "IndonesianAMSV must be strictly 64 bytes");

class IndonesianCoreEngine {
public:
    IndonesianCoreEngine() = default;
    ~IndonesianCoreEngine() = default;

    void initialize_buffer(uint8_t* raw_buffer, size_t size);
    bool is_valid_nasal_deletion(char root_char, std::string_view prefix);
    void update_state(uint8_t* buffer, uint32_t tokens, uint32_t sentences, float conf);
};

} // namespace solo_rock::indonesian
