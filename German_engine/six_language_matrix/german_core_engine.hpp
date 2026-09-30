// German Engine — C++20 Core Header
// Implements the zero-overhead physical AMSV layout and hardware synchronization functions.

#ifndef GERMAN_CORE_ENGINE_HPP
#define GERMAN_CORE_ENGINE_HPP

#include <cstdint>
#include <cstring>
#include <string_view>
#include <array>

namespace german_engine {

constexpr uint32_t AMSV_MAGIC = 0x4745524D; // "GERM"
constexpr size_t AMSV_SIZE = 64;

#pragma pack(push, 1)
struct alignas(64) GermanAmsvLayout {
    uint32_t magic_header;       // 0..3: 0x4745524D
    uint32_t version;            // 4..7: 0x00010000
    uint32_t token_count;        // 8..11
    uint32_t sentence_count;     // 12..15
    uint16_t clause_type;        // 16..17: 0x01=V2, 0x02=V-End, 0x04=V1
    uint8_t  satzklammer_flags;   // 18: VF, LK, MF, RK, NF bits
    uint8_t  case_error_flags;    // 19: Nom, Akk, Dat, Gen errors
    uint8_t  orthography_flags;   // 20: Substantive capitalization, ss/ß
    uint8_t  adjective_decl_flags;// 21: Declension errors
    uint8_t  register_type;       // 22: 0=Neutral, 1=Duzen, 2=Siezen, 3=Mixed
    uint8_t  modal_particle_count;// 23: Count of Abtönungspartikeln
    float    sub_ai_confidence;   // 24..27: Confidence score
    uint32_t syntax_latency_ns;   // 28..31
    uint32_t morph_latency_ns;    // 32..35
    uint8_t  reserved[12];        // 36..47
    uint32_t crc32_checksum;      // 48..51
    uint8_t  syntax_sub_ai_id;    // 52
    uint8_t  phonology_sub_ai_id; // 53
    uint8_t  pragmatic_sub_ai_id; // 54
    uint8_t  editorial_sub_ai_id; // 55
    uint64_t timestamp_epoch_ns;  // 56..63
};
#pragma pack(pop)

static_assert(sizeof(GermanAmsvLayout) == 64, "GermanAmsvLayout must be exactly 64 bytes");

class GermanCoreEngine {
public:
    GermanCoreEngine();
    void initialize_buffer(uint8_t* raw_buffer);
    bool validate_satzklammer(std::string_view clause_type, uint8_t* raw_buffer);
    void update_confidence(float confidence, uint8_t* raw_buffer);
};

} // namespace german_engine

#endif // GERMAN_CORE_ENGINE_HPP
