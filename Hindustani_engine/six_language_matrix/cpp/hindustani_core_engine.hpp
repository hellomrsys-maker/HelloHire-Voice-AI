// Hindustani Core Engine C++20 Header
// Zero-Nanosecond AMSV Memory Layout & Transitive Stem Lookup

#pragma once

#include <cstdint>
#include <string_view>
#include <array>

namespace hindustani_engine {

#pragma pack(push, 1)
struct RawAtomicMemoryStateVector {
    uint64_t phoneme_state;         // Bytes 0..7
    uint64_t prosody_state;         // Bytes 8..15
    uint16_t semantic_entity_id;    // Bytes 16..17
    uint16_t syntax_capability;     // Bytes 18..19 (Offset 0x12)
    uint16_t discourse_capability;  // Bytes 20..21 (Offset 0x14)
    uint16_t pragmatic_capability;  // Bytes 22..23 (Offset 0x16)
    uint16_t phonology_capability;  // Bytes 24..25 (Offset 0x18)
    uint16_t review_capability;     // Bytes 26..27 (Offset 0x1A)
    uint8_t  reserved_mid[24];      // Bytes 28..51
    uint16_t structural_score;      // Bytes 52..53 (Offset 0x34)
    uint16_t register_score;        // Bytes 54..55 (Offset 0x36)
    uint16_t attention_budget;      // Bytes 56..57 (Offset 0x38)
    uint8_t  reserved_tail[6];      // Bytes 58..63
};
#pragma pack(pop)

static_assert(sizeof(RawAtomicMemoryStateVector) == 64, "RawAtomicMemoryStateVector must be exactly 64 bytes");

class HindustaniCoreEngine {
public:
    HindustaniCoreEngine() = default;

    bool is_transitive_verb(std::string_view lemma) const;
    void direct_pack_amsv(RawAtomicMemoryStateVector* target, float syntax_score, float phonology_score, float register_score) const;
};

} // namespace hindustani_engine
