// ffi/rust_cpp/src/EngineCoreBridge.h
// C++ header for the Rust ↔ C++ cxx bridge.
// Declares functions in the polyglot::ffi namespace that cxx will bind.

#pragma once

#include <string>
#include <vector>

namespace polyglot {
namespace ffi {

// ── Struct mirrors of Rust-side types (cxx will match by name) ─────────────

struct TokenizeRequest;
struct TokenizeResponse;
struct TrainingBatchDescriptor;
struct TrainingStepResult;
struct ComponentStatus;

// ── Functions implemented in EngineCoreBridge.cpp ───────────────────────────

bool engine_bridge_init(const std::string& lib_path);
TokenizeResponse engine_bridge_tokenize(const TokenizeRequest& req);
TrainingStepResult engine_bridge_training_step(const TrainingBatchDescriptor& batch);
std::vector<ComponentStatus> engine_bridge_list_components();
bool engine_bridge_ping();
void engine_bridge_shutdown();

} // namespace ffi
} // namespace polyglot
