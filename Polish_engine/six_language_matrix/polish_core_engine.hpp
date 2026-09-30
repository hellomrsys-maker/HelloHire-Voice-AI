#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>

namespace polish::core {

constexpr uint32_t POLISH_AMSV_MAGIC = 0x504F4C53; // "POLS"
constexpr uint32_t POLISH_ENGINE_ID  = 0x00000009;

#pragma pack(push, 1)
struct PolishAtomicMemoryStateVector {
    uint32_t magic;               // 0x00 - 0x03
    uint32_t engine_id;           // 0x04 - 0x07
    uint32_t token_count;         // 0x08 - 0x0B
    uint32_t clause_count;        // 0x0C - 0x0F
    uint8_t  genitive_neg_flag;   // 0x10
    uint8_t  aspect_type;         // 0x11
    uint8_t  syntax_score;        // 0x12
    uint8_t  case_score;          // 0x13
    uint8_t  orthography_score;   // 0x14
    uint8_t  honorific_score;     // 0x15
    uint8_t  pragmatic_register;  // 0x16
    uint8_t  mobile_e_flag;       // 0x17
    uint8_t  neg_concord_count;   // 0x18
    uint8_t  vocative_flag;       // 0x19
    uint16_t reserved_flags;      // 0x1A - 0x1B
    uint32_t latency_ns;          // 0x1C - 0x1F
    uint8_t  reserved_bytes[20];  // 0x20 - 0x33
    uint8_t  sub_ai_syntax;       // 0x34
    uint8_t  sub_ai_phonology;    // 0x35
    uint8_t  sub_ai_pragmatic;    // 0x36
    uint8_t  sub_ai_editorial;    // 0x37
    uint64_t state_checksum;      // 0x38 - 0x3F
};
#pragma pack(pop)

static_assert(sizeof(PolishAtomicMemoryStateVector) == 64, "Polish AMSV must be exactly 64 bytes");

class PolishCoreEngine {
public:
    PolishCoreEngine() = default;
    void reset_state(PolishAtomicMemoryStateVector* state) noexcept;
    bool verify_case_and_aspect(PolishAtomicMemoryStateVector* state, std::span<const std::string_view> tokens) noexcept;
};

} // namespace polish::core
