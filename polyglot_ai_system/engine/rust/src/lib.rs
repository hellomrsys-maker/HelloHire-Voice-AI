// =============================================================================
// engine/rust/src/lib.rs
// Rust data ingestion, tokenization, concurrent preprocessing pipelines,
// and C-linkage FFI exports for the verbal communication engine.
//
// Role: memory-safe data processing, tokenization, and preprocessing
// for the 6-language polyglot AI system.
// =============================================================================

pub mod tokenizer;
pub mod pipeline;
pub mod normalizer;
pub mod language_detector;
pub mod sentence_segmenter;
pub mod component_family;
pub mod ffi;

// Re-export key types at crate root
pub use tokenizer::{EngineTokenizer, TokenizerConfig, TokenRecord};
pub use pipeline::{PreprocessingPipeline, PipelineConfig, PipelineOutput};
pub use normalizer::{TextNormalizer, NormalizationLevel};
pub use language_detector::{LanguageDetector, DetectionResult};
pub use sentence_segmenter::{SentenceSegmenter, Sentence};
pub use component_family::{ComponentFamily, ComponentEntry, FamilyRegistry};

use tracing::info;

/// Initialize the engine Rust module (call once at startup).
pub fn initialize(log_level: &str) {
    use tracing_subscriber::{EnvFilter, fmt};

    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new(log_level));

    fmt()
        .with_env_filter(filter)
        .with_target(true)
        .compact()
        .init();

    info!("Engine Rust module initialized");
}
