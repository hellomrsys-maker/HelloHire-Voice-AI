// ffi/rust_cpp/src/EngineCoreBridge.cpp
// C++ implementation of the Rust ↔ C++ bridge.
// Wraps EngineCore and TrainingCore behind the cxx-safe API.

#include "EngineCoreBridge.h"
#include "EngineCore.h"

#include <memory>
#include <mutex>
#include <stdexcept>
#include <chrono>
#include <cstring>

namespace polyglot {
namespace ffi {

// ─────────────────────────────────────────────────────────────────────────────
// Internal state
// ─────────────────────────────────────────────────────────────────────────────

static std::unique_ptr<polyglot::engine::EngineCore> g_engine;
static std::mutex g_mutex;
static bool g_initialized = false;

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

// struct definitions matching cxx-generated types
struct TokenizeRequest {
    std::string text;
    std::string language;
    int32_t max_tokens;
};

struct TokenizeResponse {
    std::vector<int32_t> token_ids;
    bool success;
    std::string error_msg;
};

struct TrainingBatchDescriptor {
    int32_t batch_idx;
    int32_t record_count;
    std::vector<int32_t> token_ids_flat;
    std::vector<int32_t> seq_lengths;
    int32_t max_seq_len;
};

struct TrainingStepResult {
    int32_t step;
    float loss;
    double elapsed_ms;
    bool success;
    std::string error_msg;
};

struct ComponentStatus {
    std::string name;
    bool ready;
    std::string version;
};

// ─────────────────────────────────────────────────────────────────────────────
// Bridge implementations
// ─────────────────────────────────────────────────────────────────────────────

bool engine_bridge_init(const std::string& lib_path) {
    std::lock_guard<std::mutex> lk(g_mutex);
    if (g_initialized) return true;
    try {
        polyglot::engine::EngineConfig cfg;
        cfg.lib_path = lib_path;
        g_engine = std::make_unique<polyglot::engine::EngineCore>(cfg);
        g_initialized = g_engine->initialize();
        return g_initialized;
    } catch (const std::exception& e) {
        return false;
    }
}

TokenizeResponse engine_bridge_tokenize(const TokenizeRequest& req) {
    std::lock_guard<std::mutex> lk(g_mutex);
    TokenizeResponse resp;
    if (!g_initialized || !g_engine) {
        resp.success = false;
        resp.error_msg = "Engine not initialized";
        return resp;
    }
    try {
        auto ids = g_engine->tokenize(req.text, req.language, req.max_tokens);
        resp.token_ids.assign(ids.begin(), ids.end());
        resp.success = true;
    } catch (const std::exception& e) {
        resp.success = false;
        resp.error_msg = e.what();
    }
    return resp;
}

TrainingStepResult engine_bridge_training_step(const TrainingBatchDescriptor& batch) {
    std::lock_guard<std::mutex> lk(g_mutex);
    TrainingStepResult result;
    result.step = batch.batch_idx;
    if (!g_initialized || !g_engine) {
        result.success = false;
        result.error_msg = "Engine not initialized";
        return result;
    }
    auto t0 = std::chrono::high_resolution_clock::now();
    try {
        // Forward the batch to the engine for processing
        float loss = g_engine->processBatch(
            batch.token_ids_flat.data(),
            batch.seq_lengths.data(),
            batch.record_count,
            batch.max_seq_len
        );
        auto t1 = std::chrono::high_resolution_clock::now();
        result.loss = loss;
        result.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
        result.success = true;
    } catch (const std::exception& e) {
        result.success = false;
        result.error_msg = e.what();
    }
    return result;
}

std::vector<ComponentStatus> engine_bridge_list_components() {
    std::lock_guard<std::mutex> lk(g_mutex);
    std::vector<ComponentStatus> result;
    if (!g_initialized || !g_engine) return result;

    auto components = g_engine->listComponents();
    for (const auto& c : components) {
        ComponentStatus cs;
        cs.name    = c.name;
        cs.ready   = c.ready;
        cs.version = c.version;
        result.push_back(std::move(cs));
    }
    return result;
}

bool engine_bridge_ping() {
    std::lock_guard<std::mutex> lk(g_mutex);
    return g_initialized && g_engine && g_engine->ping();
}

void engine_bridge_shutdown() {
    std::lock_guard<std::mutex> lk(g_mutex);
    if (g_engine) {
        g_engine->shutdown();
        g_engine.reset();
    }
    g_initialized = false;
}

} // namespace ffi
} // namespace polyglot
