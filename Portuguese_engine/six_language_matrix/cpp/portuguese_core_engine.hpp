// Portuguese C++20 Core Engine Header
// High-throughput personal infinitive dispatch, irregular verb lookup, and 0-ns AMSV memory sync.

#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <memory>
#include <unordered_map>

namespace gra::portuguese {

#pragma pack(push, 1)
struct PortugueseAMSRecord {
    uint64_t phoneme_state;          // 0x00..0x07 (Bytes 0..7)
    uint64_t prosody_state;          // 0x08..0x0F (Bytes 8..15)
    uint8_t  capability_scores[16];  // 0x10..0x1F (Bytes 16..31)
    uint8_t  reserved_runtime[20];   // 0x20..0x33 (Bytes 32..51)
    float    global_structural_score;// 0x34..0x35 (Bytes 52..53 as half/float)
    float    global_register_score;  // 0x36..0x37 (Bytes 54..55 as half/float)
    uint8_t  padding[8];             // 0x38..0x3F (Bytes 56..63)
};
#pragma pack(pop)

static_assert(sizeof(PortugueseAMSRecord) == 64, "PortugueseAMSRecord must be exactly 64 bytes for AMSV zero-bridge.");

struct AnalysisResult {
    bool has_valid_svo;
    bool has_clitic;
    bool has_crase;
    float syntactic_score;
    float register_score;
};

class PortugueseCoreEngine {
public:
    PortugueseCoreEngine();
    ~PortugueseCoreEngine() = default;

    AnalysisResult analyze(std::string_view sentence);
    void sync_to_amsv(const AnalysisResult& res, PortugueseAMSRecord* out_amsv);

private:
    std::unordered_map<std::string, std::string> irregular_verbs_;
};

} // namespace gra::portuguese
