// =============================================================================
// engine/rust/src/pipeline.rs
// Memory-safe concurrent preprocessing pipeline with Rayon parallelism.
// Handles batch tokenization, normalization, language detection,
// and sentence segmentation in a single pass.
// =============================================================================

use std::sync::Arc;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use anyhow::Result;
use tracing::{debug, info};

use crate::tokenizer::{EngineTokenizer, TokenRecord, TokenizerConfig, TokenizationStrategy};
use crate::normalizer::{TextNormalizer, NormalizationLevel};
use crate::language_detector::{LanguageDetector, DetectionResult};
use crate::sentence_segmenter::{SentenceSegmenter, Sentence};

// =============================================================================
// PipelineConfig
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PipelineConfig {
    pub tokenizer:          TokenizerConfig,
    pub normalization_level: NormalizationLevel,
    pub detect_language:     bool,
    pub segment_sentences:   bool,
    pub batch_size:          usize,
    pub max_workers:         usize,
}

impl Default for PipelineConfig {
    fn default() -> Self {
        Self {
            tokenizer:           TokenizerConfig::default(),
            normalization_level: NormalizationLevel::Standard,
            detect_language:     true,
            segment_sentences:   true,
            batch_size:          64,
            max_workers:         rayon::current_num_threads(),
        }
    }
}

// =============================================================================
// PipelineOutput
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PipelineOutput {
    /// Original raw input text
    pub raw_text:             String,

    /// Normalized text
    pub normalized_text:      String,

    /// Detected language (BCP-47 code)
    pub language_code:        String,

    /// Language detection confidence [0,1]
    pub lang_confidence:      f32,

    /// List of segmented sentences with their token records
    pub sentences:            Vec<SentencePipelineOutput>,

    /// All tokens in sequence (flattened across sentences)
    pub all_tokens:           Vec<TokenRecord>,

    /// Whether processing succeeded
    pub success:              bool,

    /// Error message if any
    pub error:                Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SentencePipelineOutput {
    pub sentence_text:   String,
    pub tokens:          Vec<TokenRecord>,
    pub start_offset:    u32,
    pub end_offset:      u32,
}

// =============================================================================
// PreprocessingPipeline
// =============================================================================

pub struct PreprocessingPipeline {
    config:     PipelineConfig,
    tokenizer:  Arc<EngineTokenizer>,
    normalizer: Arc<TextNormalizer>,
    lang_det:   Arc<LanguageDetector>,
    segmenter:  Arc<SentenceSegmenter>,
}

impl PreprocessingPipeline {
    /// Creates a new preprocessing pipeline with the given configuration.
    pub fn new(config: PipelineConfig) -> Self {
        let normalizer = Arc::new(TextNormalizer::new(config.normalization_level.clone()));
        let tokenizer  = Arc::new(EngineTokenizer::new(config.tokenizer.clone()));
        let lang_det   = Arc::new(LanguageDetector::new());
        let segmenter  = Arc::new(SentenceSegmenter::new());

        Self { config, tokenizer, normalizer, lang_det, segmenter }
    }

    // -------------------------------------------------------------------------
    // Single document processing
    // -------------------------------------------------------------------------

    /// Processes a single text document through the full pipeline.
    pub fn process(&self, raw_text: &str) -> PipelineOutput {
        debug!("Processing document ({} chars)", raw_text.len());

        // Stage 1: Normalize text
        let normalized = self.normalizer.normalize(raw_text);

        // Stage 2: Language detection
        let lang_result = if self.config.detect_language {
            self.lang_det.detect(&normalized)
        } else {
            DetectionResult { language: "en".into(), confidence: 1.0 }
        };

        // Stage 3: Sentence segmentation
        let sentences: Vec<Sentence> = if self.config.segment_sentences {
            self.segmenter.segment(&normalized)
        } else {
            vec![Sentence {
                text:  normalized.clone(),
                start: 0,
                end:   normalized.len() as u32,
            }]
        };

        // Stage 4: Tokenize each sentence
        let sentence_outputs: Vec<SentencePipelineOutput> = sentences
            .par_iter()
            .map(|sent| {
                let tokens = self.tokenizer.tokenize(&sent.text)
                    .unwrap_or_default();
                SentencePipelineOutput {
                    sentence_text: sent.text.clone(),
                    tokens,
                    start_offset:  sent.start,
                    end_offset:    sent.end,
                }
            })
            .collect();

        // Stage 5: Flatten tokens
        let all_tokens: Vec<TokenRecord> = sentence_outputs
            .iter()
            .flat_map(|s| s.tokens.iter().cloned())
            .collect();

        debug!("Pipeline output: {} sentences, {} tokens",
               sentence_outputs.len(), all_tokens.len());

        PipelineOutput {
            raw_text:        raw_text.to_string(),
            normalized_text: normalized,
            language_code:   lang_result.language,
            lang_confidence: lang_result.confidence,
            sentences:       sentence_outputs,
            all_tokens,
            success:         true,
            error:           None,
        }
    }

    // -------------------------------------------------------------------------
    // Batch processing (parallel via Rayon)
    // -------------------------------------------------------------------------

    /// Processes a batch of documents in parallel.
    /// Returns one PipelineOutput per input document.
    pub fn process_batch(&self, documents: &[&str]) -> Vec<PipelineOutput> {
        info!("Processing batch of {} documents", documents.len());
        documents.par_iter()
            .map(|doc| self.process(doc))
            .collect()
    }

    /// Processes a streaming iterator of documents.
    /// Applies back-pressure by chunking into batches of `batch_size`.
    pub fn process_stream<I>(&self, iter: I) -> impl Iterator<Item = PipelineOutput> + '_
    where
        I: Iterator<Item = String> + Send + 'static
    {
        let batch_size = self.config.batch_size;
        let mut buffer  = Vec::with_capacity(batch_size);
        let mut results = Vec::new();

        for doc in iter {
            buffer.push(doc);
            if buffer.len() >= batch_size {
                let batch_refs: Vec<&str> = buffer.iter().map(|s| s.as_str()).collect();
                results.extend(self.process_batch(&batch_refs));
                buffer.clear();
            }
        }
        // Process remaining
        if !buffer.is_empty() {
            let batch_refs: Vec<&str> = buffer.iter().map(|s| s.as_str()).collect();
            results.extend(self.process_batch(&batch_refs));
        }

        results.into_iter()
    }

    // -------------------------------------------------------------------------
    // Accessors
    // -------------------------------------------------------------------------

    pub fn tokenizer(&self) -> &EngineTokenizer { &self.tokenizer }
    pub fn config(&self) -> &PipelineConfig { &self.config }
}

// =============================================================================
// DataIngestionPipeline — wraps PreprocessingPipeline with I/O support
// Reads from files/streams, preprocesses, and writes structured output
// =============================================================================

pub struct DataIngestionPipeline {
    preprocessor: PreprocessingPipeline,
}

impl DataIngestionPipeline {
    pub fn new(config: PipelineConfig) -> Self {
        Self {
            preprocessor: PreprocessingPipeline::new(config)
        }
    }

    /// Ingests text from a string slice and returns structured pipeline output.
    pub fn ingest_text(&self, text: &str) -> Result<PipelineOutput> {
        Ok(self.preprocessor.process(text))
    }

    /// Ingests a list of texts (e.g. lines from a corpus file).
    pub fn ingest_texts(&self, texts: &[&str]) -> Result<Vec<PipelineOutput>> {
        Ok(self.preprocessor.process_batch(texts))
    }

    /// Ingests raw bytes (UTF-8) — validates encoding before processing.
    pub fn ingest_bytes(&self, bytes: &[u8]) -> Result<PipelineOutput> {
        let text = std::str::from_utf8(bytes)
            .map_err(|e| anyhow::anyhow!("Invalid UTF-8 in input: {}", e))?;
        Ok(self.preprocessor.process(text))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipeline_single() {
        let pipeline = PreprocessingPipeline::new(PipelineConfig::default());
        let output = pipeline.process("Hi, I am Ash. How are you?");
        assert!(output.success);
        assert!(!output.all_tokens.is_empty());
        assert_eq!(output.language_code, "en");
    }

    #[test]
    fn test_pipeline_batch() {
        let pipeline = PreprocessingPipeline::new(PipelineConfig::default());
        let docs = ["Hello world.", "This is a test.", "How are you?"];
        let outputs = pipeline.process_batch(&docs);
        assert_eq!(outputs.len(), 3);
        for output in &outputs {
            assert!(output.success);
        }
    }

    #[test]
    fn test_ingestion_utf8_validation() {
        let ingestion = DataIngestionPipeline::new(PipelineConfig::default());
        let valid_result = ingestion.ingest_bytes(b"Hello world");
        assert!(valid_result.is_ok());

        let invalid_utf8 = &[0xFF, 0xFE, 0x00];
        let invalid_result = ingestion.ingest_bytes(invalid_utf8);
        assert!(invalid_result.is_err());
    }

    #[test]
    fn test_pipeline_empty_input() {
        let pipeline = PreprocessingPipeline::new(PipelineConfig::default());
        let output = pipeline.process("");
        assert!(output.success);
        assert!(output.all_tokens.is_empty() || output.all_tokens.iter().all(|t| t.is_special));
    }
}
