// Italian Engine — C++20 Core Engine Implementation

#include "italian_core_engine.hpp"
#include <cstring>
#include <unordered_set>
#include <string>

namespace solo_rock::italian {

static const std::unordered_set<std::string_view> ESSERE_VERBS = {
    "andare", "venire", "partire", "arrivare", "uscire", "entrare",
    "nascere", "morire", "cadere", "diventare", "rimanere", "stare", "essere"
};

void ItalianCoreEngine::initialize_buffer(uint8_t* raw_buffer, size_t size) {
    if (!raw_buffer || size < ITALIAN_AMSV_SIZE) return;
    std::memset(raw_buffer, 0, ITALIAN_AMSV_SIZE);
    auto* amsv = reinterpret_cast<ItalianAMSV*>(raw_buffer);
    amsv->magic = ITALIAN_AMSV_MAGIC;
    amsv->version = 0x00010000;
    amsv->sub_ai_active[0] = 1; // Syntax
    amsv->sub_ai_active[1] = 1; // Phonology
    amsv->sub_ai_active[2] = 1; // Pragmatic
    amsv->sub_ai_active[3] = 1; // Editorial
}

bool ItalianCoreEngine::validate_auxiliary(std::string_view verb, std::string_view aux) {
    bool requires_essere = ESSERE_VERBS.contains(verb);
    if (requires_essere) {
        return (aux == "essere" || aux == "sono" || aux == "è" || aux == "siamo");
    }
    return (aux == "avere" || aux == "ho" || aux == "ha" || aux == "abbiamo");
}

void ItalianCoreEngine::update_state(uint8_t* buffer, uint32_t tokens, uint32_t sentences, float conf) {
    if (!buffer) return;
    auto* amsv = reinterpret_cast<ItalianAMSV*>(buffer);
    amsv->token_count = tokens;
    amsv->sentence_count = sentences;
    amsv->confidence_score = conf;
}

} // namespace solo_rock::italian
