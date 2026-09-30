/**
 * @file maio_core.hpp
 * @brief Main Artificial Intelligence Orchestrator (MAIO) C++ Core.
 *
 * Implements the 1000Hz real-time surveillance loop, cross-module anomaly detection,
 * intervention directive generation, and zero-bridge AMSV synchronization.
 */

#ifndef MAIO_CORE_HPP
#define MAIO_CORE_HPP

#include <cstdint>
#include <atomic>
#include <chrono>
#include <thread>
#include <array>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::maio {

// Intervention Directive Bitmask (Bits 0-31 in maio_global_state_beta)
constexpr uint32_t INTERVENTION_NONE              = 0x00000000;
constexpr uint32_t INTERVENTION_DEESCALATE_STRESS = 0x00000001; // Reduce scenario probe difficulty
constexpr uint32_t INTERVENTION_PROMPT_STRUCTURE  = 0x00000002; // Prompt candidate for STAR/MECE structure
constexpr uint32_t INTERVENTION_PACE_CORRECTION   = 0x00000004; // Instruct candidate to alter speaking rate
constexpr uint32_t INTERVENTION_VOCAB_ELEVATION   = 0x00000008; // Challenge candidate to use higher register
constexpr uint32_t INTERVENTION_CLARIFY_PHONEME   = 0x00000010; // Prompt re-articulation of blurred syllables
constexpr uint32_t INTERVENTION_EMERGENCY_HALT    = 0x80000000; // Engine fault or severe cognitive freeze

struct MaioTelemetrySnapshot {
    uint64_t timestamp_ns{0};
    float global_competency_index{0.0f};
    uint32_t system_health_code{0};
    uint32_t active_interventions{INTERVENTION_NONE};
    float vce_fluency{0.0f};
    float ccte_emotional_regulation{0.0f};
    float ccte_analytical_thinking{0.0f};
    float rsse_register_compliance{0.0f};
    float aeee_irt_theta{0.0f};
};

class MaioCore {
public:
    explicit MaioCore(solorock::amsv::MasterSharedMemorySegment* amsv_segment);
    ~MaioCore();

    /// Starts the 1000Hz surveillance monitoring thread
    void start_surveillance_loop();

    /// Stops the surveillance loop
    void stop_surveillance_loop();

    /// Executes a single 1ms surveillance iteration
    void step_surveillance_tick() noexcept;

    /// Generates dynamic intervention directives based on real-time state analysis
    [[nodiscard]] uint32_t compute_intervention_directives(const MaioTelemetrySnapshot& snap) const noexcept;

    /// Retrieves the most recent telemetry snapshot
    [[nodiscard]] MaioTelemetrySnapshot get_latest_telemetry() const noexcept;

    /// Directly synchronizes MAIO state into AMSV state vector (offsets 0x30 and 0x38)
    void sync_to_amsv(float competency_index, uint32_t health, uint32_t interventions) noexcept;

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
    std::atomic<bool> is_running_{false};
    std::unique_ptr<std::thread> worker_thread_{nullptr};
    MaioTelemetrySnapshot latest_snapshot_{};

    void surveillance_thread_entry();
};

} // namespace solorock::maio

#endif // MAIO_CORE_HPP
