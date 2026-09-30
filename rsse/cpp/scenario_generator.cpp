/**
 * @file scenario_generator.cpp
 * @brief Recruitment Scenario Simulation Engine (RSSE) C++ Implementation.
 */

#include "scenario_generator.hpp"
#include <algorithm>
#include <cmath>
#include <sstream>

namespace solorock::rsse {

ScenarioGenerator::ScenarioGenerator(solorock::amsv::MasterSharedMemorySegment* amsv_segment)
    : amsv_(amsv_segment) {
    if (amsv_) {
        sync_to_amsv();
    }
}

bool ScenarioGenerator::initialize_scenario(uint16_t target_format, const CandidatePerformanceHistory& history) {
    config_.format_code = (target_format >= 1 && target_format <= 8) ? target_format : 1;
    config_.current_turn = 0;
    config_.phase = InterviewPhase::WarmupIntroduction;
    config_.register_compliance = 1.0f;
    current_probe_idx_ = 0;

    // Difficulty scaling based on prior sessions and baseline capability
    float baseline_skill = (history.cumulative_fluency + history.cumulative_analytical + history.cumulative_emotional) / 3.0f;
    config_.dynamic_stress_multiplier = std::clamp(baseline_skill * 1.25f, 0.6f, 1.8f);

    loaded_depth_probes_.clear();
    loaded_stress_probes_.clear();

    std::string core_prompt;

    switch (config_.format_code) {
        case 1: // Technical
            config_.scenario_id = 101;
            core_prompt = "Design an ultra-low-latency distributed consensus cluster handling 10 million transactions per second with sub-50-microsecond p99 latency across three availability zones. Explain your memory ordering, network protocol, and failure detection strategy.";
            loaded_depth_probes_.push_back("How do you prevent thread starvation under asymmetric packet drop at the NIC ring buffer?");
            loaded_depth_probes_.push_back("Explain the exact memory fence semantics you will use between the serialization thread and the zero-copy ring buffer.");
            loaded_stress_probes_.push_back("Your proposed architecture violates linearizability during partition healing. Walk me through the exact bug you just introduced.");
            loaded_stress_probes_.push_back("That design will saturate PCIe lanes within 30 seconds. How do you recover without dropping live customer state?");
            break;

        case 2: // Behavioral
            config_.scenario_id = 201;
            core_prompt = "Tell me about a time when a catastrophic zero-day security incident compromised production infrastructure while your primary technical leads were unreachable. Walk me through your Situation, Task, Action, and measurable Result.";
            loaded_depth_probes_.push_back("What specific pushback did you receive from executive stakeholders during the downtime, and how did you de-escalate?");
            loaded_depth_probes_.push_back("How did you quantitatively measure whether customer trust was restored post-incident?");
            loaded_stress_probes_.push_back("You mentioned 'we decided'. What specifically did YOU do as an individual that changed the outcome?");
            loaded_stress_probes_.push_back("Why did your monitoring not catch the vulnerability before the exploit occurred?");
            break;

        case 3: // Competency
            config_.scenario_id = 301;
            core_prompt = "Demonstrate how you manage irreconcilable requirements between an engineering team pushing for technical refactoring and a commercial sales team demanding custom feature delivery for a $5M renewal.";
            loaded_depth_probes_.push_back("Walk me through the exact prioritization formula you used to balance engineering stability and customer ARR.");
            loaded_stress_probes_.push_back("Your compromise surrendered engineering integrity to commercial pressure. How do you defend that decision?");
            break;

        case 4: // Case Study
            config_.scenario_id = 401;
            core_prompt = "Our autonomous electric delivery fleet company is evaluating entering the German urban logistics market with 5,000 vehicles. Analyze market size, regulatory risks, unit economics per delivery, and propose a Go/No-Go framework.";
            loaded_depth_probes_.push_back("Break down the variable operating costs per vehicle-hour, specifically power, teleoperations, and insurance liability.");
            loaded_stress_probes_.push_back("Your delivery volume estimate is double the total market capacity of Berlin and Munich combined. Recalculate right now.");
            break;

        case 5: // Group Discussion
            config_.scenario_id = 501;
            core_prompt = "In this group simulation, synthesize consensus between clinical staff resisting change and two vendor-backed executives regarding a unified patient health record across 42 hospitals.";
            loaded_depth_probes_.push_back("A vocal participant just dismissed your interoperability concerns. Address their objection directly.");
            loaded_stress_probes_.push_back("Consensus has completely broken down and participants are walking out. What is your intervention?");
            break;

        case 6: // HR Screening
            config_.scenario_id = 601;
            core_prompt = "Why our firm, why this practice group, and what unique professional philosophy distinguishes your work ethic in ambiguous engagements?";
            loaded_depth_probes_.push_back("Can you provide an example of a fundamental value conflict you resolved in your previous role?");
            loaded_stress_probes_.push_back("That sounds like a rehearsed canned response. Give me an honest, unscripted moment where you failed.");
            break;

        case 7: // Executive
            config_.scenario_id = 701;
            core_prompt = "Deliver your 5-year strategic vision on capital allocation, talent retention, IP protection, and defense against state-sponsored actors for our $250M sovereign defense AI initiative.";
            loaded_depth_probes_.push_back("How do you structure the balance between commercial off-the-shelf defense tech and classified internal IP?");
            loaded_stress_probes_.push_back("A foreign intelligence agency has infiltrated your subcontractor. The press knows, but the board doesn't. Your first 60 minutes. Go.");
            break;

        case 8: // Panel
        default:
            config_.scenario_id = 801;
            core_prompt = "Defend your $1.2B network modernization roadmap before a hostile panel: CFO (25% cost cut), CSO (zero-trust isolation), and COO (zero downtime).";
            loaded_depth_probes_.push_back("Address the CFO and CSO directly by name and reconcile their contradictory mandates.");
            loaded_stress_probes_.push_back("The Chief Architect just called your design obsolete and amateurish. Respond without defensiveness.");
            break;
    }

    if (amsv_) {
        // Write prompt to shared memory buffer
        std::memset(amsv_->scenario_prompt_buffer, 0, sizeof(amsv_->scenario_prompt_buffer));
        std::strncpy(amsv_->scenario_prompt_buffer, core_prompt.c_str(), sizeof(amsv_->scenario_prompt_buffer) - 1);
        sync_to_amsv();
    }

    return true;
}

bool ScenarioGenerator::process_candidate_turn(const std::string& transcript, float speech_wpm) {
    config_.current_turn++;
    config_.current_wpm = speech_wpm;

    if (amsv_) {
        std::memset(amsv_->candidate_transcription, 0, sizeof(amsv_->candidate_transcription));
        std::strncpy(amsv_->candidate_transcription, transcript.c_str(), sizeof(amsv_->candidate_transcription) - 1);
    }

    // Heuristic Register Compliance Evaluation
    float wpm_target = 135.0f;
    float wpm_delta = std::abs(speech_wpm - wpm_target) / wpm_target;
    float wpm_score = std::clamp(1.0f - wpm_delta, 0.0f, 1.0f);

    // Simple word count check
    float length_score = (transcript.size() > 40) ? 1.0f : (static_cast<float>(transcript.size()) / 40.0f);
    
    config_.register_compliance = (wpm_score * 0.4f) + (length_score * 0.6f);

    // Dynamic phase transitions
    transition_phase();

    // Adapt difficulty from live cognitive state
    adapt_difficulty_from_amsv();

    // Sync state vector
    sync_to_amsv();

    return true;
}

void ScenarioGenerator::transition_phase() {
    switch (config_.phase) {
        case InterviewPhase::WarmupIntroduction:
            if (config_.current_turn >= 1) {
                config_.phase = InterviewPhase::CoreExploration;
            }
            break;
        case InterviewPhase::CoreExploration:
            if (config_.current_turn >= 2) {
                config_.phase = InterviewPhase::DepthProbing;
            }
            break;
        case InterviewPhase::DepthProbing:
            if (config_.current_turn >= 4) {
                config_.phase = InterviewPhase::StressChallenge;
            }
            break;
        case InterviewPhase::StressChallenge:
            if (config_.current_turn >= 6) {
                config_.phase = InterviewPhase::SynthesisDebrief;
            }
            break;
        case InterviewPhase::SynthesisDebrief:
            if (config_.current_turn >= 7) {
                config_.phase = InterviewPhase::Concluded;
            }
            break;
        case InterviewPhase::Concluded:
            break;
    }
}

void ScenarioGenerator::adapt_difficulty_from_amsv() {
    if (!amsv_) return;

    // Read emotional regulation score from CCTE cognitive bank beta (offset 0x18 in AMSV)
    // Bits 48-63 represent Emotional Regulation
    uint64_t beta = amsv_->state_vector.ccte_cog_bank_beta.load(std::memory_order_acquire);
    uint16_t emo_reg_q16 = static_cast<uint16_t>((beta >> 48) & 0xFFFF);
    float emo_reg = static_cast<float>(emo_reg_q16) / 65535.0f;

    // If candidate shows high emotional regulation (> 0.8), escalate stress challenge
    if (emo_reg > 0.80f) {
        config_.dynamic_stress_multiplier = std::min(config_.dynamic_stress_multiplier * 1.15f, 2.0f);
    } else if (emo_reg < 0.40f) {
        // De-escalate to avoid cognitive shutdown
        config_.dynamic_stress_multiplier = std::max(config_.dynamic_stress_multiplier * 0.85f, 0.5f);
    }
}

std::string ScenarioGenerator::generate_next_prompt() {
    switch (config_.phase) {
        case InterviewPhase::WarmupIntroduction:
        case InterviewPhase::CoreExploration:
            return amsv_ ? std::string(amsv_->scenario_prompt_buffer) : "Please begin your response.";

        case InterviewPhase::DepthProbing: {
            if (!loaded_depth_probes_.empty()) {
                size_t idx = current_probe_idx_ % loaded_depth_probes_.size();
                current_probe_idx_++;
                return loaded_depth_probes_[idx];
            }
            return "Elaborate further on your methodology and trade-offs.";
        }

        case InterviewPhase::StressChallenge: {
            if (!loaded_stress_probes_.empty()) {
                size_t idx = current_probe_idx_ % loaded_stress_probes_.size();
                current_probe_idx_++;
                return loaded_stress_probes_[idx];
            }
            return "Explain the vulnerability in your approach and why it failed.";
        }

        case InterviewPhase::SynthesisDebrief:
            return "Synthesize your overarching recommendations into a concise executive summary.";

        case InterviewPhase::Concluded:
            return "The interview scenario has completed. Evaluating holistic performance.";
    }
    return "Proceed with your analysis.";
}

void ScenarioGenerator::sync_to_amsv() noexcept {
    if (!amsv_) return;

    uint16_t comp_q16 = static_cast<uint16_t>(std::clamp(config_.register_compliance, 0.0f, 1.0f) * 65535.0f);
    uint64_t word = static_cast<uint64_t>(config_.scenario_id)
                  | (static_cast<uint64_t>(config_.current_turn) << 16)
                  | (static_cast<uint64_t>(comp_q16) << 32)
                  | (static_cast<uint64_t>(config_.phase) << 48);

    amsv_->state_vector.rsse_scenario_state.store(word, std::memory_order_release);
}

} // namespace solorock::rsse
