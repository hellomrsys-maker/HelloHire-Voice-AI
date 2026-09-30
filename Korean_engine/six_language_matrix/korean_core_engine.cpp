// Korean Engine — C++20 Core Implementation
#include "korean_core_engine.hpp"
#include <chrono>

namespace korean_engine {

KoreanCoreEngine::KoreanCoreEngine() {}

void KoreanCoreEngine::initialize_buffer(uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    
    auto* amsv = reinterpret_cast<KoreanAmsvLayout*>(raw_buffer);
    std::memset(raw_buffer, 0, AMSV_SIZE);
    
    amsv->magic_header = AMSV_MAGIC;
    amsv->version = 0x00010000;
    amsv->clause_type = 0x0001; // Declarative
    amsv->syntax_flags = 0x01;  // Head-final
    amsv->speech_level_code = 2; // Haeyo-che
    amsv->sub_ai_confidence = 1.0f;
    amsv->syntax_sub_ai_id = 1;
    amsv->phonology_sub_ai_id = 1;
    amsv->pragmatic_sub_ai_id = 1;
    amsv->editorial_sub_ai_id = 1;
    
    auto now = std::chrono::system_clock::now().time_since_epoch();
    amsv->timestamp_epoch_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
}

void KoreanCoreEngine::update_confidence(float confidence, uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    auto* amsv = reinterpret_cast<KoreanAmsvLayout*>(raw_buffer);
    amsv->sub_ai_confidence = confidence;
}

bool KoreanCoreEngine::check_batchim_quick(char32_t utf32_char) const {
    if (utf32_char < 0xAC00 || utf32_char > 0xD7A3) return false;
    uint32_t s_index = utf32_char - 0xAC00;
    return (s_index % 28) != 0;
}

} // namespace korean_engine
