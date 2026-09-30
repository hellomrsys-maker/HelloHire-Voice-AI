// Arabic Engine — C++20 Core Implementation
#include "arabic_core_engine.hpp"

namespace arabic_engine {

ArabicCoreEngine::ArabicCoreEngine() = default;

void ArabicCoreEngine::initialize_buffer(uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    auto* layout = reinterpret_cast<ArabicAmsvLayout*>(raw_buffer);
    std::memset(layout, 0, AMSV_SIZE);
    layout->magic_header = AMSV_MAGIC;
    layout->version = 0x00010000;
    layout->clause_type = 0x0001; // VSO default
    layout->syntax_flags = 0x01;  // VSO verified default
    layout->phonology_flags = 0x04; // Hamza valid
    layout->morphology_flags = 0x01; // Form I
    layout->root_class = 1;       // ktb
    layout->pragmatic_flags = 0x02; // Pure MSA
    layout->sub_ai_confidence = 1.0f;
    layout->syntax_sub_ai_id = 1;
    layout->phonology_sub_ai_id = 1;
    layout->pragmatic_sub_ai_id = 1;
    layout->editorial_sub_ai_id = 1;
}

void ArabicCoreEngine::update_confidence(float confidence, uint8_t* raw_buffer) {
    if (!raw_buffer) return;
    auto* layout = reinterpret_cast<ArabicAmsvLayout*>(raw_buffer);
    layout->sub_ai_confidence = confidence;
}

bool ArabicCoreEngine::check_sun_letter_quick(char32_t utf32_char) const {
    // Check coronal Arabic letters: ت ث د ذ ر ز س ش ص ض ط ظ ل ن
    switch (utf32_char) {
        case 0x062A: case 0x062B: case 0x062F: case 0x0630:
        case 0x0631: case 0x0632: case 0x0633: case 0x0634:
        case 0x0635: case 0x0636: case 0x0637: case 0x0638:
        case 0x0644: case 0x0646:
            return true;
        default:
            return false;
    }
}

} // namespace arabic_engine
