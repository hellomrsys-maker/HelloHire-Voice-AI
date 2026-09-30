/**
 * Cantonese Core Engine - C++20 Implementation
 * Operating under The Zero-Bridge Synchronous Memory Rule.
 */

#include "cantonese_core_engine.hpp"

CantoneseCoreEngine::CantoneseCoreEngine(CantoneseAMSV* shared_memory)
    : amsv_(shared_memory) {}

void CantoneseCoreEngine::initialize() {
    if (!amsv_) return;
    std::memset(amsv_, 0, sizeof(CantoneseAMSV));
    amsv_->magic[0] = 'Y';
    amsv_->magic[1] = 'U';
    amsv_->magic[2] = 'E';
    amsv_->magic[3] = 'T';
    amsv_->version_major = 1;
    amsv_->version_minor = 0;
    amsv_->engine_mode = 1;
    amsv_->dialect_mode = 1;
    amsv_->register_tier = 1;
}

bool CantoneseCoreEngine::verify_magic() const {
    if (!amsv_) return false;
    return amsv_->magic[0] == 'Y' &&
           amsv_->magic[1] == 'U' &&
           amsv_->magic[2] == 'E' &&
           amsv_->magic[3] == 'T';
}

void CantoneseCoreEngine::sync_sub_ais() {
    if (!amsv_) return;
    amsv_->sub_ai_syntax_active = 0x01;
    amsv_->sub_ai_phonology_active = 0x01;
    amsv_->sub_ai_pragmatic_active = 0x01;
    amsv_->sub_ai_editorial_active = 0x01;
}

void CantoneseCoreEngine::set_confidence(float score) {
    if (!amsv_) return;
    amsv_->editorial_confidence = score;
}
