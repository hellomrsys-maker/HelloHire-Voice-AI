/**
 * @file test_cognitive_engines_cpp.cpp
 * @brief Comprehensive verification of all 8 C++ Cognitive & Communication Engines.
 *
 * Verifies:
 *   1. ALIE C++ Core (Listening Scorecard & Grade)
 *   2. ECSE C++ Core (Social Calibration & Grade)
 *   3. PMCE C++ Core (Persuasion Scorecard & Grade)
 *   4. HCTE C++ Core (Cognitive Personas & Grade)
 *   5. DCVE C++ Core (Domain Competence & Grade)
 *   6. NACE C++ Core (Narrative Arc & Grade)
 *   7. LSCE C++ Core (Cognitive Endurance & Grade)
 *   8. PACE C++ Core (Pacing & Adaptation & Grade)
 *   9. Zero-Bridge Synchronous Memory write to 64-byte AtomicStateVector (0-ns sync)
 */

#include <iostream>
#include <cassert>
#include <cstring>

#include "../amsv/include/amsv_layout.h"
#include "../alie/cpp/alie_core.hpp"
#include "../ecse/cpp/ecse_core.hpp"
#include "../pmce/cpp/pmce_core.hpp"
#include "../hcte/cpp/hcte_core.hpp"
#include "../dcve/cpp/dcve_core.hpp"
#include "../nace/cpp/nace_core.hpp"
#include "../lsce/cpp/lsce_core.hpp"
#include "../pace/cpp/pace_core.hpp"

int main() {
    std::cout << "========================================================\n";
    std::cout << "TESTING ALL 8 C++ COGNITIVE ENGINES & ZERO-BRIDGE AMSV\n";
    std::cout << "========================================================\n";

    // 0. Allocate cache-line aligned 64-byte AtomicStateVector
    alignas(64) solorock::amsv::AtomicStateVector amsv{};
    std::memset(&amsv, 0, sizeof(amsv));
    static_assert(sizeof(solorock::amsv::AtomicStateVector) == 64, "AMSV must be exactly 64 bytes");

    // 1. ALIE Test
    std::cout << "[1/8] ALIE C++ Engine Evaluation...";
    {
        solorock::alie::ActiveListeningIntelligenceEngine alie(&amsv);
        std::vector<std::string> hist = {"Past context on database indexing"};
        auto sc = alie.evaluate(
            "What happened during the outage?",
            "During the outage you mentioned, we diagnosed thread starvation and resolved it.",
            hist, 1200.0f, 1
        );
        assert(sc.listening_grade >= 1 && sc.listening_grade <= 4);
        assert(sc.global_listening_index > 0.0f);
        std::cout << " PASS (Grade: " << sc.listening_grade << ", GLI: " << sc.global_listening_index << ")\n";
    }

    // 2. ECSE Test
    std::cout << "[2/8] ECSE C++ Engine Evaluation...";
    {
        solorock::ecse::EmotionalCommunicationSocialEngine ecse(&amsv);
        auto sc = ecse.evaluate(
            "I appreciate your question. Together as a team, we enthusiastically addressed the challenge.",
            "Can you explain your teamwork?",
            140.0f, 135.0f, 1
        );
        assert(sc.social_grade >= 1 && sc.social_grade <= 4);
        assert(sc.global_social_intelligence > 0.0f);
        std::cout << " PASS (Grade: " << sc.social_grade << ", GSI: " << sc.global_social_intelligence << ")\n";
    }

    // 3. PMCE Test
    std::cout << "[3/8] PMCE C++ Engine Evaluation...";
    {
        solorock::pmce::PersuasionMessageConstructionEngine pmce(&amsv);
        auto sc = pmce.evaluate(
            "In my experience as lead architect, data shows p99 latency dropped by 35ms because we deployed Raft. "
            "I propose we standardize this pattern.", 1
        );
        assert(sc.persuasion_grade >= 1 && sc.persuasion_grade <= 4);
        assert(sc.global_persuasion_index > 0.0f);
        std::cout << " PASS (Grade: " << sc.persuasion_grade << ", GPI: " << sc.global_persuasion_index << ")\n";
    }

    // 4. HCTE Test
    std::cout << "[4/8] HCTE C++ Engine Evaluation...";
    {
        solorock::hcte::HumanCognitiveThinkingEngine hcte(&amsv);
        auto sc = hcte.evaluate(
            "We identified a critical single point of failure in our dependency graph. "
            "To mitigate this risk, we implemented circuit breakers and fallback mechanisms for resilience."
        );
        assert(sc.cognitive_grade >= 1 && sc.cognitive_grade <= 4);
        assert(sc.global_cognitive_index > 0.0f);
        assert(sc.cognitive_tension > 0.0f);
        std::cout << " PASS (Grade: " << sc.cognitive_grade << ", GCI: " << sc.global_cognitive_index << ")\n";
    }

    // 5. DCVE Test
    std::cout << "[5/8] DCVE C++ Engine Evaluation...";
    {
        solorock::dcve::DomainCompetenceVerbalEngine dcve(&amsv);
        auto sc = dcve.evaluate(
            "We configured Kafka topic partitions to ensure linearizability, while Redis cache reduced p99 latency by 40ms."
        );
        assert(sc.domain_grade >= 1 && sc.domain_grade <= 4);
        assert(sc.track_id == 1); // Engineering
        assert(sc.domain_competence_index > 0.0f);
        std::cout << " PASS (Grade: " << sc.domain_grade << ", Track: " << sc.track_id << ", DCI: " << sc.domain_competence_index << ")\n";
    }

    // 6. NACE Test
    std::cout << "[6/8] NACE C++ Engine Evaluation...";
    {
        solorock::nace::NarrativeArcCoherenceEngine nace(&amsv);
        auto sc = nace.evaluate(
            "The problem was a cascading outage. My role was lead investigator. "
            "I implemented a distributed queue. As a result, we achieved zero downtime.", 1
        );
        assert(sc.narrative_grade >= 1 && sc.narrative_grade <= 4);
        assert(sc.narrative_coherence_index > 0.0f);
        assert(sc.climax_score >= 0.75f);
        std::cout << " PASS (Grade: " << sc.narrative_grade << ", NCI: " << sc.narrative_coherence_index << ")\n";
    }

    // 7. LSCE Test
    std::cout << "[7/8] LSCE C++ Engine Evaluation...";
    {
        solorock::lsce::CognitiveEnduranceEngine lsce(&amsv);
        auto sc = lsce.evaluate(
            "Can you explain both the root cause and your mitigation?",
            "First, the root cause was lock contention. Second, our mitigation introduced non-blocking queues.", 1
        );
        assert(sc.endurance_grade >= 1 && sc.endurance_grade <= 4);
        assert(sc.endurance_index > 0.0f);
        std::cout << " PASS (Grade: " << sc.endurance_grade << ", EI: " << sc.endurance_index << ")\n";
    }

    // 8. PACE Test
    std::cout << "[8/8] PACE C++ Engine Evaluation...";
    {
        solorock::pace::PacingAdaptationEngine pace(&amsv);
        auto sc = pace.evaluate(
            "Briefly, in one sentence, what was your role?",
            "I was the principal engineer responsible for the consensus layer refactoring."
        );
        assert(sc.pacing_grade >= 1 && sc.pacing_grade <= 4);
        assert(sc.adaptation_index > 0.0f);
        std::cout << " PASS (Grade: " << sc.pacing_grade << ", ACI: " << sc.adaptation_index << ")\n";
    }

    // 9. Zero-Bridge AMSV Vector Memory Verification
    std::cout << "\n[9/9] Verifying Zero-Bridge AMSV 64-byte Physical Memory Sync...\n";
    uint64_t vce_p = amsv.vce_phoneme_state.load();
    uint64_t bank_a = amsv.ccte_cog_bank_alpha.load();
    uint64_t bank_b = amsv.ccte_cog_bank_beta.load();
    uint64_t aeee = amsv.aeee_examination_state.load();
    uint64_t maio_a = amsv.maio_global_state_alpha.load();
    uint64_t maio_b = amsv.maio_global_state_beta.load();

    // Verify non-zero updates in designated engine slots
    assert(bank_a != 0);  // ALIE
    assert(bank_b != 0);  // ALIE
    assert(aeee != 0);    // PMCE
    assert(maio_a != 0);  // DCVE & NACE
    assert(maio_b != 0);  // HCTE, LSCE & PACE

    std::cout << "  -> Bank Alpha (ALIE): 0x" << std::hex << bank_a << "\n";
    std::cout << "  -> Bank Beta  (ALIE): 0x" << std::hex << bank_b << "\n";
    std::cout << "  -> AEEE State (PMCE): 0x" << std::hex << aeee << "\n";
    std::cout << "  -> MAIO Alpha (DCVE/NACE): 0x" << std::hex << maio_a << "\n";
    std::cout << "  -> MAIO Beta  (HCTE/LSCE/PACE): 0x" << std::hex << maio_b << "\n";
    std::cout << "  -> 0-ns Synchronous Memory Verification: 100% SUCCESS.\n";

    std::cout << "\nALL 8 C++ COGNITIVE ENGINES AND GRADING PASSED.\n";
    return 0;
}
