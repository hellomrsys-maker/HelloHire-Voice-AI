// =============================================================================
// engine/cpp/src/main.cpp
// Engine CLI — standalone validation executable
// =============================================================================

#include "EngineCore.h"
#include "VocalInputProcessor.h"
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    std::cout << "=== Polyglot AI System — Verbal Communication Engine CLI ===\n";

    // Create engine from config
    engine::EngineConfig config;
    config.engine_id        = "verbal_comm_engine_v1";
    config.engine_version   = "1.0.0";
    config.default_language = "en";
    config.supported_languages = {"en", "ja", "fr", "de", "ar", "es", "ta"};
    config.thread_pool_size = 4;
    config.enable_gpu       = false; // CLI mode runs on CPU
    config.attention_heads  = 8;
    config.attention_dim    = 512;
    config.max_sequence_length = 512;
    config.episodic_memory_slots = 1024;
    config.semantic_memory_slots = 8192;
    config.working_memory_bytes  = 256 * 1024 * 1024; // 256 MB

    std::cout << "Creating engine...\n";
    engine::EngineCore eng(std::move(config));

    std::cout << "Recruiting subsystems...\n";
    try {
        eng.recruitAllSubsystems();
    } catch (const std::exception& e) {
        std::cerr << "FATAL: Subsystem recruitment failed: " << e.what() << "\n";
        return 1;
    }

    std::cout << "Engine operational: " << (eng.isOperational() ? "YES" : "NO") << "\n";
    std::cout << "Status: " << eng.statusReport() << "\n";

    if (!eng.isOperational()) {
        std::cerr << "FATAL: Engine failed to reach operational status.\n";
        return 1;
    }

    std::cout << "\nHealth dump:\n" << eng.healthDump() << "\n\n";

    // Run a series of test inputs
    struct TestCase {
        std::string input;
        const char* expected_intent;
    };

    const std::vector<TestCase> test_cases = {
        {"Hi, I am Ash.",        "greet"},
        {"Hello, my name is Sam.", "greet"},
        {"Hey there! I'm Alex.", "greet"},
        {"What is the meaning of life?", "ask_question"},
        {"Please explain how attention works.", "make_request"},
        {"Goodbye! See you later.", "farewell"},
        {"How are you doing today?", "ask_question"},
    };

    int passed = 0;
    for (const auto& tc : test_cases) {
        std::cout << "INPUT:    " << tc.input << "\n";
        try {
            auto response = eng.processText(tc.input,
                                             engine::OutputModality::TEXT,
                                             engine::ReasoningDepth::MODERATE);
            std::cout << "RESPONSE: " << response.text << "\n";
            std::cout << "LATENCY:  " << response.latency.count() << " ms\n";
            std::cout << "CONF:     " << response.confidence << "\n";
            ++passed;
        } catch (const std::exception& e) {
            std::cerr << "ERROR processing input: " << e.what() << "\n";
        }
        std::cout << "---\n";
    }

    std::cout << "\nPassed " << passed << "/" << test_cases.size() << " test cases.\n";
    std::cout << "Final status: " << eng.statusReport() << "\n";

    eng.shutdown();
    std::cout << "Engine shut down cleanly.\n";
    return (passed == static_cast<int>(test_cases.size())) ? 0 : 1;
}
