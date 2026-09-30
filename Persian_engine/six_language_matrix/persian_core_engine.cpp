// Persian Core Engine C++20 Implementation
// Zero-Bridge Physical Memory Mutations

#include "persian_core_engine.hpp"

namespace PersianEngine {

PersianCoreEngine::PersianCoreEngine(PersianAtomicMemoryStateVector* shared_memory)
    : m_vector(shared_memory) {
    if (m_vector) {
        initialize_vector();
    }
}

void PersianCoreEngine::initialize_vector() {
    if (!m_vector) return;
    std::memset(m_vector, 0, sizeof(PersianAtomicMemoryStateVector));
    m_vector->magic[0] = 'F';
    m_vector->magic[1] = 'A';
    m_vector->magic[2] = 'R';
    m_vector->magic[3] = 'S';
    m_vector->version_major = 0x01;
    m_vector->version_minor = 0x00;
    m_vector->engine_mode = 0x01;  // Inference
    m_vector->script_mode = 0x01;  // Perso-Arabic RTL
}

bool PersianCoreEngine::verify_magic() const {
    if (!m_vector) return false;
    return m_vector->magic[0] == 'F' &&
           m_vector->magic[1] == 'A' &&
           m_vector->magic[2] == 'R' &&
           m_vector->magic[3] == 'S';
}

void PersianCoreEngine::update_syntax_state(bool is_head_final, bool ezafe_valid) {
    if (!m_vector) return;
    uint8_t flags = 0;
    if (is_head_final) flags |= 0x01;
    if (ezafe_valid) flags |= 0x02;
    m_vector->syntax_sub_ai_status = flags;
    m_vector->sub_ai_active_syntax = 0x01;
}

void PersianCoreEngine::update_dom_state(bool dom_valid) {
    if (!m_vector) return;
    m_vector->dom_accuracy = dom_valid ? 0x01 : 0x00;
}

void PersianCoreEngine::update_taarof_state(uint8_t tier, bool deference_aligned) {
    if (!m_vector) return;
    m_vector->taarof_register = tier;
    m_vector->deference_flag = deference_aligned ? 0x01 : 0x00;
    m_vector->sub_ai_active_pragmatic = 0x01;
}

void PersianCoreEngine::update_confidence(float score) {
    if (!m_vector) return;
    m_vector->confidence_score = score;
    m_vector->sub_ai_active_editorial = 0x01;
}

} // namespace PersianEngine
