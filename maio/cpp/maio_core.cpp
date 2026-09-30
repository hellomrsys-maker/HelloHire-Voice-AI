/**
 * @file maio_core.cpp
 * @brief Main Artificial Intelligence Orchestrator (MAIO) C++ Implementation.
 */

#include "maio_core.hpp"
#include <cmath>
#include <cstring>
#include <iostream>

namespace solorock::maio {

MaioCore::MaioCore(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {
    if (amsv_) {
        sync_to_amsv(0.70f, 0, INTERVENTION_NONE);
    }
}

MaioCore::~MaioCore() {
    stop_surveillance_loop();
}

void MaioCore::start_surveillance_loop() {
    if (is_running_.exchange(true)) {
        return; // Already running
    }
    worker_thread_ = std::make_unique<std::thread>(&MaioCore::surveillance_thread_entry, this);
}

void MaioCore::stop_surveillance_loop() {
    if (is_running_.exchange(false)) {
        if (worker_thread_ && worker_thread_->joinable()) {
            worker_thread_->join();
        }
        worker_thread_.reset();
    }
}

void MaioCore::surveillance_thread_entry() {
    using clock = std::chrono::steady_clock;
    while (is_running_.load(std::memory_order_relaxed)) {
        auto next_tick = clock::now() + std::chrono::microseconds(1000); // 1000Hz (1ms)
        step_surveillance_tick();
        std::this_thread::sleep_until(next_tick);
    }
}

void MaioCore::step_surveillance_tick() noexcept {
    if (!amsv_) return;

    auto now_ns = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count()
    );

    // 1. Ingest VCE Prosody (Offset 0x08)
    uint64_t vce_pros = amsv_->state_vector.vce_prosody_state.load(std::memory_order_acquire);
    uint16_t fluency_q16 = static_cast<uint16_t>((vce_pros >> 32) & 0xFFFF);
    float fluency = static_cast<float>(fluency_q16) / 65535.0f;

    // 2. Ingest CCTE Cog Bank Beta (Offset 0x18)
    uint64_t ccte_beta = amsv_->state_vector.ccte_cog_bank_beta.load(std::memory_order_acquire);
    uint16_t anal_q16 = static_cast<uint16_t>((ccte_beta >> 16) & 0xFFFF);
    uint16_t emo_q16  = static_cast<uint16_t>((ccte_beta >> 48) & 0xFFFF);
    float analytical = static_cast<float>(anal_q16) / 65535.0f;
    float emotional  = static_cast<float>(emo_q16) / 65535.0f;

    // 3. Ingest RSSE Scenario State (Offset 0x20)
    uint64_t rsse_state = amsv_->state_vector.rsse_scenario_state.load(std::memory_order_acquire);
    uint16_t comp_q16 = static_cast<uint16_t>((rsse_state >> 32) & 0xFFFF);
    float compliance = static_cast<float>(comp_q16) / 65535.0f;

    // 4. Ingest AEEE Examination State (Offset 0x28)
    uint64_t aeee_state = amsv_->state_vector.aeee_examination_state.load(std::memory_order_acquire);
    uint32_t theta_bits = static_cast<uint32_t>(aeee_state & 0xFFFFFFFF);
    float theta = 0.0f;
    std::memcpy(&theta, &theta_bits, sizeof(float));
    float norm_theta = 1.0f / (1.0f + std::exp(-theta)); // Sigmoid map to [0, 1]

    // 5. Compute Global Competency Index
    float global_comp = (fluency * 0.20f) +
                        (analytical * 0.25f) +
                        (emotional * 0.15f) +
                        (compliance * 0.20f) +
                        (norm_theta * 0.20f);
    global_comp = std::clamp(global_comp, 0.0f, 1.0f);

    // 6. Assemble Telemetry Snapshot
    latest_snapshot_.timestamp_ns = now_ns;
    latest_snapshot_.global_competency_index = global_comp;
    latest_snapshot_.vce_fluency = fluency;
    latest_snapshot_.ccte_analytical_thinking = analytical;
    latest_snapshot_.ccte_emotional_regulation = emotional;
    latest_snapshot_.rsse_register_compliance = compliance;
    latest_snapshot_.aeee_irt_theta = theta;

    // 7. Determine Dynamic Intervention Directives
    uint32_t interventions = compute_intervention_directives(latest_snapshot_);
    latest_snapshot_.active_interventions = interventions;

    // 8. Synchronize back to AMSV
    sync_to_amsv(global_comp, 0, interventions);
}

uint32_t MaioCore::compute_intervention_directives(const MaioTelemetrySnapshot& snap) const noexcept {
    uint32_t flags = INTERVENTION_NONE;

    // Stress breakdown detection
    if (snap.ccte_emotional_regulation < 0.35f) {
        flags |= INTERVENTION_DEESCALATE_STRESS;
    }

    // Dysfluent speech or extreme pause detection
    if (snap.vce_fluency < 0.40f) {
        flags |= INTERVENTION_PACE_CORRECTION;
    }

    // Structure failure (rambling or lack of STAR/MECE framing)
    if (snap.rsse_register_compliance < 0.45f) {
        flags |= INTERVENTION_PROMPT_STRUCTURE;
    }

    // Register deficit
    if (snap.rsse_register_compliance > 0.45f && snap.ccte_analytical_thinking > 0.70f && snap.vce_fluency > 0.85f) {
        flags |= INTERVENTION_VOCAB_ELEVATION; // Candidate ready for executive elevation
    }

    return flags;
}

MaioTelemetrySnapshot MaioCore::get_latest_telemetry() const noexcept {
    return latest_snapshot_;
}

void MaioCore::sync_to_amsv(float competency_index, uint32_t health, uint32_t interventions) noexcept {
    if (!amsv_) return;

    // Offset 0x30: maio_global_state_alpha
    // [Bits 0-31: Global Competency Index (float) | Bits 32-63: System Health & Sync Counter]
    uint32_t comp_bits = 0;
    std::memcpy(&comp_bits, &competency_index, sizeof(float));
    uint64_t alpha_word = static_cast<uint64_t>(comp_bits) | (static_cast<uint64_t>(health) << 32);
    amsv_->state_vector.maio_global_state_alpha.store(alpha_word, std::memory_order_release);

    // Offset 0x38: maio_global_state_beta
    // [Bits 0-31: Intervention Directives | Bits 32-63: Attention Weights]
    uint64_t beta_word = static_cast<uint64_t>(interventions);
    amsv_->state_vector.maio_global_state_beta.store(beta_word, std::memory_order_release);
}

} // namespace solorock::maio
