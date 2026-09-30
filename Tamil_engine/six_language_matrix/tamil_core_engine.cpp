/**
 * Tamil Core Engine - C++20 Implementation
 * Operating under The Zero-Bridge Synchronous Memory Rule.
 */

#include "tamil_core_engine.hpp"

TamilCoreEngine::TamilCoreEngine(TamilAMSV* shared_memory)
    : amsv_(shared_memory) {}

void TamilCoreEngine::initialize() {
    if (!amsv_) return;
    std::memset(amsv_, 0, sizeof(TamilAMSV));
    amsv_->magic[0] = 'T';
    amsv_->magic[1] = 'A';
    amsv_->magic[2] = 'M';
    amsv_->magic[3] = 'L';
    amsv_->version_major = 1;
    amsv_->version_minor = 0;
    amsv_->engine_mode = 1;
    amsv_->dialect_mode = 1;
    amsv_->register_tier = 1;
}

bool TamilCoreEngine::verify_magic() const {
    if (!amsv_) return false;
    return amsv_->magic[0] == 'T' &&
           amsv_->magic[1] == 'A' &&
           amsv_->magic[2] == 'M' &&
           amsv_->magic[3] == 'L';
}

void TamilCoreEngine::sync_sub_ais() {
    if (!amsv_) return;
    amsv_->sub_ai_syntax_active = 0x01;
    amsv_->sub_ai_phonology_active = 0x01;
    amsv_->sub_ai_pragmatic_active = 0x01;
    amsv_->sub_ai_editorial_active = 0x01;
}

void TamilCoreEngine::set_confidence(float score) {
    if (!amsv_) return;
    amsv_->editorial_confidence = score;
}
