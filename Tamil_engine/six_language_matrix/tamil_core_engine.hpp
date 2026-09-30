/**
 * Tamil Core Engine - C++20 Header
 * Direct Physical Memory Layout for 64-byte Atomic Memory State Vector (AMSV)
 * Magic: 0x54414D4C ("TAML")
 */

#pragma once

#include <cstdint>
#include <cstring>
#include <string_view>

#pragma pack(push, 1)
struct alignas(64) TamilAMSV {
    uint8_t magic[4];                // 0x00..0x03: "TAML"
    uint8_t version_major;           // 0x04
    uint8_t version_minor;           // 0x05
    uint8_t engine_mode;             // 0x06
    uint8_t dialect_mode;            // 0x07: 1 = Centamil, 2 = Koduntamil
    uint8_t reserved_head[10];       // 0x08..0x11
    uint8_t syntax_capability;       // 0x12 (Byte 18): Bitfield S, O, V
    uint8_t case_agglutination_flag; // 0x13 (Byte 19): 0x01 = 8-case verified
    uint8_t retroflex_orthography;   // 0x14 (Byte 20): Bitfield Valid, Retroflex, ழ
    uint8_t png_concord_flag;        // 0x15 (Byte 21): 0x01 = PNG concord
    uint8_t register_tier;           // 0x16 (Byte 22): 1 = Centamil, 2 = Koduntamil
    uint8_t sandhi_concord_flag;     // 0x17 (Byte 23): 0x01 = Sandhi plosives
    float   editorial_confidence;    // 0x18..0x1B (Bytes 24..27): Float32 quality score
    uint8_t reserved_mid[24];        // 0x1C..0x33
    uint8_t sub_ai_syntax_active;    // 0x34 (Byte 52)
    uint8_t sub_ai_phonology_active; // 0x35 (Byte 53)
    uint8_t sub_ai_pragmatic_active; // 0x36 (Byte 54)
    uint8_t sub_ai_editorial_active; // 0x37 (Byte 55)
    uint8_t reserved_tail[8];        // 0x38..0x3F (Padding to 64 bytes)
};
#pragma pack(pop)

static_assert(sizeof(TamilAMSV) == 64, "TamilAMSV must be exactly 64 bytes");

class TamilCoreEngine {
public:
    explicit TamilCoreEngine(TamilAMSV* shared_memory);
    void initialize();
    bool verify_magic() const;
    void sync_sub_ais();
    void set_confidence(float score);

private:
    TamilAMSV* amsv_;
};
