/**
 * @file scenario_generator.hpp
 * @brief Recruitment Scenario Simulation Engine (RSSE) C++ Dynamic Generator.
 *
 * Implements real-time dynamic instantiation of interview scenarios,
 * adaptive difficulty scaling, state machine branch transitions,
 * and zero-bridge AMSV synchronization.
 */

#ifndef RSSE_SCENARIO_GENERATOR_HPP
#define RSSE_SCENARIO_GENERATOR_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <cstring>
#include "../../amsv/include/amsv_layout.h"

namespace solorock::rsse {

enum class InterviewPhase : uint16_t {
    WarmupIntroduction = 1,
    CoreExploration    = 2,
    DepthProbing       = 3,
    StressChallenge    = 4,
    SynthesisDebrief   = 5,
    Concluded          = 6
};

struct CandidatePerformanceHistory {
    float cumulative_fluency{0.80f};
    float cumulative_analytical{0.75f};
    float cumulative_emotional{0.85f};
    float prior_failure_rate{0.10f};
    uint32_t total_sessions_completed{5};
};

struct DynamicScenarioConfig {
    uint16_t scenario_id{101};
    uint16_t format_code{1}; // 1-8
    uint16_t current_turn{0};
    InterviewPhase phase{InterviewPhase::WarmupIntroduction};
    float register_compliance{1.0f};
    float dynamic_stress_multiplier{1.0f}; // [0.5, 2.0]
    float current_wpm{135.0f};
};

class ScenarioGenerator {
public:
    explicit ScenarioGenerator(solorock::amsv::MasterSharedMemorySegment* amsv_segment);
    ~ScenarioGenerator() = default;

    /// Initializes a scenario dynamically matched to candidate history
    bool initialize_scenario(uint16_t target_format, const CandidatePerformanceHistory& history);

    /// Processes candidate response turn, evaluates register compliance, advances phase
    bool process_candidate_turn(const std::string& transcript, float speech_wpm);

    /// Selects the next probe or prompt based on performance and current state
    std::string generate_next_prompt();

    /// Dynamically scales stress and difficulty based on live CCTE cognitive state
    void adapt_difficulty_from_amsv();

    /// Synchronizes current RSSE state into 64-byte AMSV state vector
    void sync_to_amsv() noexcept;

    // Accessors
    [[nodiscard]] const DynamicScenarioConfig& get_config() const noexcept { return config_; }
    [[nodiscard]] InterviewPhase get_current_phase() const noexcept { return config_.phase; }

private:
    solorock::amsv::MasterSharedMemorySegment* amsv_{nullptr};
    DynamicScenarioConfig config_{};
    std::vector<std::string> loaded_depth_probes_;
    std::vector<std::string> loaded_stress_probes_;
    uint32_t current_probe_idx_{0};

    void transition_phase();
};

} // namespace solorock::rsse

#endif // RSSE_SCENARIO_GENERATOR_HPP
