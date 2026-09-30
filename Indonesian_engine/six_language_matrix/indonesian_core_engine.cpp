// Indonesian Engine — C++20 Core Engine Implementation

#include "indonesian_core_engine.hpp"
#include <cstring>

namespace solo_rock::indonesian {

void IndonesianCoreEngine::initialize_buffer(uint8_t* raw_buffer, size_t size) {
    if (!raw_buffer || size < INDONESIAN_AMSV_SIZE) return;
    std::memset(raw_buffer, 0, INDONESIAN_AMSV_SIZE);
    auto* amsv = reinterpret_cast<IndonesianAMSV*>(raw_buffer);
    amsv->magic = INDONESIAN_AMSV_MAGIC;
    amsv->version = 0x00010000;
    amsv->sub_ai_active[0] = 1; // Syntax
    amsv->sub_ai_active[1] = 1; // Phonology
    amsv->sub_ai_active[2] = 1; // Pragmatic
    amsv->sub_ai_active[3] = 1; // Editorial
}

bool IndonesianCoreEngine::is_valid_nasal_deletion(char root_char, std::string_view prefix) {
    switch (root_char) {
        case 'p': return prefix == "mem";
        case 't': return prefix == "men";
        case 's': return prefix == "meny";
        case 'k': return prefix == "meng";
        default: return false;
    }
}

void IndonesianCoreEngine::update_state(uint8_t* buffer, uint32_t tokens, uint32_t sentences, float conf) {
    if (!buffer) return;
    auto* amsv = reinterpret_cast<IndonesianAMSV*>(buffer);
    amsv->token_count = tokens;
    amsv->sentence_count = sentences;
    amsv->confidence_score = conf;
}

} // namespace solo_rock::indonesian
