/**
 * Thai Core Engine - C++20 Header
 * Direct Physical Memory Layout for 64-byte Atomic Memory State Vector (AMSV)
 * Magic: 0x54484149 ("THAI")
 */

#pragma once

#include <cstdint>
#include <cstring>
#include <string_view>

#pragma pack(push, 1)
struct alignas(64) ThaiAMSV {
    uint8_t magic[4];                // 0x00..0x03: "THAI"
    uint8_t version_major;           // 0x04
    uint8_t version_minor;           // 0x05
    uint8_t engine_mode;             // 0x06
    uint8_t dialect_mode;            // 0x07: 1 = Central Standard Thai
    uint8_t reserved_head[10];       // 0x08..0x11
    uint8_t syntax_capability;       // 0x12 (Byte 18): Bitfield
    uint8_t classifier_syntax;       // 0x13 (Byte 19): 0x01 = Noun + Num + Clf
    uint8_t five_tone_conformity;    // 0x14 (Byte 20): Bitfield
    uint8_t politeness_concord;      // 0x15 (Byte 21): 0x01 = Politeness particles
    uint8_t register_tier;           // 0x16 (Byte 22): 1=Colloquial, 2=Formal, 3=Monk, 4=Rachasap
    uint8_t segmentation_flag;       // 0x17 (Byte 23): 0x01 = Segmented
    float   editorial_confidence;    // 0x18..0x1B (Bytes 24..27): Float32 quality score
    uint8_t reserved_mid[24];        // 0x1C..0x33
    uint8_t sub_ai_syntax_active;    // 0x34 (Byte 52)
    uint8_t sub_ai_phonology_active; // 0x35 (Byte 53)
    uint8_t sub_ai_pragmatic_active; // 0x36 (Byte 54)
    uint8_t sub_ai_editorial_active; // 0x37 (Byte 55)
    uint8_t reserved_tail[8];        // 0x38..0x3F (Padding to 64 bytes)
};
#pragma pack(pop)

static_assert(sizeof(ThaiAMSV) == 64, "ThaiAMSV must be exactly 64 bytes");

class ThaiCoreEngine {
public:
    explicit ThaiCoreEngine(ThaiAMSV* shared_memory);
    void initialize();
    bool verify_magic() const;
    void sync_sub_ais();
    void set_confidence(float score);

private:
    ThaiAMSV* amsv_;
};
