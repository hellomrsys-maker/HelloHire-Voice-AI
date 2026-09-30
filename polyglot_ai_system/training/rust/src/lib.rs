// training/rust/src/lib.rs
//! Polyglot Training — Rust Data Pipeline
//!
//! High-throughput, memory-safe data processing for the AI training system.
//! Implements:
//!   - Concurrent batch loading from JSONL/YAML/binary sources
//!   - BPE / WordPiece / Unigram tokenization
//!   - Unicode normalization and language detection
//!   - Training record validation (enforcing spec: no raw dialogue, approved only)
//!   - Parallel preprocessing with Rayon work-stealing
//!   - C FFI exports for the C++ training core
//!   - Metrics collection and reporting

pub mod batch;
pub mod ffi;
pub mod metrics;
pub mod normalizer;
pub mod pipeline;
pub mod record;
pub mod tokenizer;
pub mod validator;

use std::sync::atomic::{AtomicU64, Ordering};

/// Global processed-record counter (atomic, lock-free).
static PROCESSED_RECORDS: AtomicU64 = AtomicU64::new(0);
static REJECTED_RECORDS: AtomicU64 = AtomicU64::new(0);

pub fn increment_processed() {
    PROCESSED_RECORDS.fetch_add(1, Ordering::Relaxed);
}

pub fn increment_rejected() {
    REJECTED_RECORDS.fetch_add(1, Ordering::Relaxed);
}

pub fn processed_count() -> u64 {
    PROCESSED_RECORDS.load(Ordering::Relaxed)
}

pub fn rejected_count() -> u64 {
    REJECTED_RECORDS.load(Ordering::Relaxed)
}

// ─────────────────────────────────────────────────────────────────────────────
// Re-exports for public API
// ─────────────────────────────────────────────────────────────────────────────

pub use batch::{BatchLoader, DataBatch, DataSource};
pub use ffi::{
    polyglot_batch_free, polyglot_batch_get_record, polyglot_batch_len,
    polyglot_pipeline_create, polyglot_pipeline_destroy, polyglot_pipeline_next_batch,
};
pub use metrics::{PipelineMetrics, Timer};
pub use normalizer::Normalizer;
pub use pipeline::{DataPipeline, PipelineConfig};
pub use record::{TrainingRecord, ValidationError};
pub use tokenizer::{BpeTokenizer, Tokenizer, TokenizerKind, Vocab};
pub use validator::RecordValidator;
