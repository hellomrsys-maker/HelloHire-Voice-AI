// ffi/rust_cpp/src/lib.rs
//! Rust ↔ C++ cxx bridge.
//!
//! Exposes the C++ EngineCore and TrainingCore to Rust callers
//! and provides safe Rust wrappers. Used by the Rust data pipeline
//! to query engine tokenization, send batches to C++ training, and
//! receive evaluation metrics.

#[cxx::bridge(namespace = "polyglot::ffi")]
pub mod ffi {
    // ── Types visible to both Rust and C++ ──────────────────────────────

    /// Tokenization request from Rust → C++ engine
    struct TokenizeRequest {
        text: String,
        language: String,
        max_tokens: i32,
    }

    /// Tokenization response from C++ → Rust
    struct TokenizeResponse {
        token_ids: Vec<i32>,
        success: bool,
        error_msg: String,
    }

    /// Training batch descriptor sent from Rust → C++
    struct TrainingBatchDescriptor {
        batch_idx: i32,
        record_count: i32,
        /// Flattened token IDs: [record_count × max_seq_len]
        token_ids_flat: Vec<i32>,
        seq_lengths: Vec<i32>,
        max_seq_len: i32,
    }

    /// Training step result received from C++ → Rust
    struct TrainingStepResult {
        step: i32,
        loss: f32,
        elapsed_ms: f64,
        success: bool,
        error_msg: String,
    }

    /// Engine component status
    struct ComponentStatus {
        name: String,
        ready: bool,
        version: String,
    }

    // ── C++ functions callable from Rust ────────────────────────────────

    unsafe extern "C++" {
        include!("polyglot_ai_system/ffi/rust_cpp/src/EngineCoreBridge.h");

        /// Initialize the engine bridge. Must be called before any other function.
        /// Returns true on success.
        fn engine_bridge_init(lib_path: &str) -> bool;

        /// Tokenize a text string using the C++ engine's tokenizer.
        fn engine_bridge_tokenize(req: &TokenizeRequest) -> TokenizeResponse;

        /// Send a training batch to the C++ TrainingCore for a single step.
        fn engine_bridge_training_step(
            batch: &TrainingBatchDescriptor,
        ) -> TrainingStepResult;

        /// Query component status from the engine.
        fn engine_bridge_list_components() -> Vec<ComponentStatus>;

        /// Ping the engine bridge (returns true if healthy).
        fn engine_bridge_ping() -> bool;

        /// Shutdown the engine bridge and release all resources.
        fn engine_bridge_shutdown();
    }

    // ── Rust functions callable from C++ ────────────────────────────────

    extern "Rust" {
        /// Rust callback: invoked by C++ when a training step completes.
        /// Allows Rust pipeline to update metrics without polling.
        fn on_training_step_complete(result: &TrainingStepResult);

        /// Rust callback: invoked by C++ when the engine needs more data.
        /// Returns the next batch or an empty descriptor if the epoch is done.
        fn on_request_next_batch(epoch: i32, step: i32) -> TrainingBatchDescriptor;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Rust callback implementations
// ─────────────────────────────────────────────────────────────────────────────

use std::sync::{Arc, Mutex};
use once_cell::sync::Lazy;

/// Shared training metrics updated by C++ callbacks.
#[derive(Debug, Default, Clone)]
pub struct TrainingMetrics {
    pub total_steps: u64,
    pub total_loss: f64,
    pub last_loss: f32,
}

static METRICS: Lazy<Arc<Mutex<TrainingMetrics>>> =
    Lazy::new(|| Arc::new(Mutex::new(TrainingMetrics::default())));

/// Global batch provider: set by the host to supply batches on demand.
static BATCH_PROVIDER: Lazy<Arc<Mutex<Option<Box<dyn BatchProvider + Send>>>>> =
    Lazy::new(|| Arc::new(Mutex::new(None)));

/// Trait for supplying training batches to the C++ core.
pub trait BatchProvider {
    fn next_batch(&mut self, epoch: i32, step: i32) -> ffi::TrainingBatchDescriptor;
}

/// Called by C++ when a training step finishes.
pub fn on_training_step_complete(result: &ffi::TrainingStepResult) {
    if result.success {
        if let Ok(mut m) = METRICS.lock() {
            m.total_steps += 1;
            m.total_loss += result.loss as f64;
            m.last_loss = result.loss;
        }
        tracing::debug!(
            step = result.step,
            loss = result.loss,
            elapsed_ms = result.elapsed_ms,
            "Training step complete (C++ callback)"
        );
    } else {
        tracing::warn!(
            step = result.step,
            error = %result.error_msg,
            "Training step failed (C++ callback)"
        );
    }
}

/// Called by C++ to request the next training batch.
pub fn on_request_next_batch(epoch: i32, step: i32) -> ffi::TrainingBatchDescriptor {
    if let Ok(mut guard) = BATCH_PROVIDER.lock() {
        if let Some(provider) = guard.as_mut() {
            return provider.next_batch(epoch, step);
        }
    }
    // Empty batch signals end-of-epoch
    ffi::TrainingBatchDescriptor {
        batch_idx: -1,
        record_count: 0,
        token_ids_flat: vec![],
        seq_lengths: vec![],
        max_seq_len: 0,
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Public safe wrapper API
// ─────────────────────────────────────────────────────────────────────────────

/// Initialize the engine bridge.
pub fn init(lib_path: &str) -> bool {
    ffi::engine_bridge_init(lib_path)
}

/// Safe wrapper: tokenize text via C++ engine.
pub fn tokenize(text: &str, language: &str, max_tokens: i32) -> Option<Vec<i32>> {
    let req = ffi::TokenizeRequest {
        text: text.to_string(),
        language: language.to_string(),
        max_tokens,
    };
    let resp = ffi::engine_bridge_tokenize(&req);
    if resp.success {
        Some(resp.token_ids)
    } else {
        tracing::warn!("Tokenization failed: {}", resp.error_msg);
        None
    }
}

/// Safe wrapper: send one training batch to C++.
pub fn training_step(
    batch_idx: i32,
    token_ids: &[i32],
    seq_lengths: &[i32],
    max_seq_len: i32,
) -> Option<f32> {
    let batch = ffi::TrainingBatchDescriptor {
        batch_idx,
        record_count: seq_lengths.len() as i32,
        token_ids_flat: token_ids.to_vec(),
        seq_lengths: seq_lengths.to_vec(),
        max_seq_len,
    };
    let result = ffi::engine_bridge_training_step(&batch);
    if result.success {
        Some(result.loss)
    } else {
        tracing::warn!("Training step failed: {}", result.error_msg);
        None
    }
}

/// Safe wrapper: list engine components.
pub fn list_components() -> Vec<(String, bool)> {
    ffi::engine_bridge_list_components()
        .into_iter()
        .map(|c| (c.name, c.ready))
        .collect()
}

/// Ping the engine.
pub fn ping() -> bool {
    ffi::engine_bridge_ping()
}

/// Shutdown the bridge.
pub fn shutdown() {
    ffi::engine_bridge_shutdown();
}

/// Get a snapshot of training metrics.
pub fn get_metrics() -> TrainingMetrics {
    METRICS.lock().unwrap().clone()
}

/// Register a batch provider for C++ callbacks.
pub fn set_batch_provider(provider: Box<dyn BatchProvider + Send>) {
    if let Ok(mut guard) = BATCH_PROVIDER.lock() {
        *guard = Some(provider);
    }
}
