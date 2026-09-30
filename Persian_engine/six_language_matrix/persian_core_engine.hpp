// Persian Core Engine C++20 Header
// Zero-Bridge physical memory vector layout & 0-ns real-time loop

#pragma once

#include <cstdint>
#include <cstring>
#include <string_view>
#include <array>

namespace PersianEngine {

constexpr uint32_t PERSIAN_AMSV_MAGIC = 0x46415253; // "FARS"

#pragma pack(push, 1)
struct alignas(64) PersianAtomicMemoryStateVector {
    char magic[4];                   // 0x00..0x03: "FARS"
    uint8_t version_major;           // 0x04: 0x01
    uint8_t version_minor;           // 0x05: 0x00
    uint8_t engine_mode;             // 0x06: 0=Init, 1=Inference, 2=RealTime
    uint8_t script_mode;             // 0x07: 1=Perso-Arabic RTL
    uint64_t phonology_bitfield;     // 0x08..0x0F
    uint16_t syntactic_flags;        // 0x10..0x11: SOV, Ezafe, etc.
    uint8_t syntax_sub_ai_status;    // 0x12: Syntax capability
    uint8_t dom_accuracy;            // 0x13: DOM rā flag
    uint8_t zwnj_orthography;        // 0x14: ZWNJ flag
    uint8_t light_verb_flag;         // 0x15: Complex predicate flag
    uint8_t taarof_register;         // 0x16: 1=Informal, 2=Formal, 3=High Ta'arof
    uint8_t deference_flag;          // 0x17: Deference concord
    float confidence_score;          // 0x18..0x1B: Float32 quality score
    uint32_t reserved_hardware;      // 0x1C..0x1F
    uint8_t semantic_vector[16];     // 0x20..0x2F
    uint32_t task_status;            // 0x30..0x33
    uint8_t sub_ai_active_syntax;    // 0x34
    uint8_t sub_ai_active_phonology; // 0x35
    uint8_t sub_ai_active_pragmatic; // 0x36
    uint8_t sub_ai_active_editorial; // 0x37
    uint8_t attention_vector[8];     // 0x38..0x3F
};
#pragma pack(pop)

static_assert(sizeof(PersianAtomicMemoryStateVector) == 64, "Persian AMSV must be exactly 64 bytes");

class PersianCoreEngine {
public:
    explicit PersianCoreEngine(PersianAtomicMemoryStateVector* shared_memory);
    void initialize_vector();
    void update_syntax_state(bool is_head_final, bool ezafe_valid);
    void update_dom_state(bool dom_valid);
    void update_taarof_state(uint8_t tier, bool deference_aligned);
    void update_confidence(float score);
    [[nodiscard]] bool verify_magic() const;

private:
    PersianAtomicMemoryStateVector* m_vector;
};

} // namespace PersianEngine
