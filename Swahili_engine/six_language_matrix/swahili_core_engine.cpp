// Swahili Engine — C++20 Core Implementation
#include "swahili_core_engine.hpp"

namespace swahili_engine {

SwahiliCoreEngine::SwahiliCoreEngine() = default;

void SwahiliCoreEngine::initialize_buffer(uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    auto* layout = reinterpret_cast<SwahiliAmsvLayout*>(raw_buffer);
    std::memset(layout, 0, AMSV_SIZE);
    layout->magic_header = AMSV_MAGIC;
    layout->version = 0x00010000;
    layout->clause_type = 0x0001; // Declarative SVO
    layout->syntax_flags = 0x01;  // SVO default
    layout->phonology_flags = 0x02; // Penultimate stress satisfied
    layout->noun_class_head = 1;  // Default Class 1
    layout->sub_ai_confidence = 1.0f;
    layout->syntax_sub_ai_id = 1;
    layout->phonology_sub_ai_id = 1;
    layout->pragmatic_sub_ai_id = 1;
    layout->editorial_sub_ai_id = 1;
}

void SwahiliCoreEngine::update_confidence(float confidence, uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    auto* layout = reinterpret_cast<SwahiliAmsvLayout*>(raw_buffer);
    layout->sub_ai_confidence = confidence;
}

bool SwahiliCoreEngine::check_concord_quick(uint8_t noun_class, uint8_t verb_sp_class) const {
    // Semantic agreement: animate nouns (e.g. Cl 9 simba) take Cl 1/2 SP
    if (noun_class == verb_sp_class) return true;
    if ((noun_class == 9 || noun_class == 5) && (verb_sp_class == 1 || verb_sp_class == 2)) {
        return true; // Animate exception
    }
    return false;
}

} // namespace swahili_engine
