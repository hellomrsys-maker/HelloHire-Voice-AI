// Hindustani Core Engine C++20 Implementation
// Zero-Nanosecond AMSV Memory Layout & Transitive Stem Lookup

#include "hindustani_core_engine.hpp"
#include <algorithm>

namespace hindustani_engine {

bool HindustaniCoreEngine::is_transitive_verb(std::string_view lemma) const {
    constexpr std::array<std::string_view, 16> trans_verbs = {
        "karna", "dekhna", "likhna", "padhna", "khana", "peena",
        "kehna", "sunna", "dena", "lena", "banana", "khareedna",
        "bechna", "dhundhna", "bhejna", "samajhna"
    };

    for (const auto& v : trans_verbs) {
        if (lemma == v) return true;
    }
    return false;
}

void HindustaniCoreEngine::direct_pack_amsv(
    RawAtomicMemoryStateVector* target,
    float syntax_score,
    float phonology_score,
    float register_score
) const {
    if (!target) return;

    // Strict zero-bridge physical memory assignment
    uint16_t syn_q16 = static_cast<uint16_t>(std::clamp(syntax_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t phn_q16 = static_cast<uint16_t>(std::clamp(phonology_score, 0.0f, 1.0f) * 65535.0f);
    uint16_t reg_q16 = static_cast<uint16_t>(std::clamp(register_score, 0.0f, 1.0f) * 65535.0f);

    target->syntax_capability = syn_q16;
    target->structural_score = syn_q16;

    target->phonology_capability = phn_q16;

    target->pragmatic_capability = reg_q16;
    target->register_score = reg_q16;
}

} // namespace hindustani_engine
