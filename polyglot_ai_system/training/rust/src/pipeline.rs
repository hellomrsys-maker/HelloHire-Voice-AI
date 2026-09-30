// training/rust/src/pipeline.rs
//! High-level DataPipeline: orchestrates BatchLoader, Tokenizer, and output.

use crate::batch::{BatchError, BatchLoader, DataBatch, DataSource};
use crate::metrics::PipelineMetrics;
use crate::tokenizer::{BpeTokenizer, Tokenizer};
use crate::validator::RecordValidator;
use tracing::info;

/// Configuration for the data pipeline.
#[derive(Debug, Clone)]
pub struct PipelineConfig {
    pub batch_size: usize,
    pub shuffle: bool,
    pub min_quality_score: f64,
    pub vocab_path: Option<String>,
    pub max_seq_len: usize,
    pub num_workers: usize,
}

impl Default for PipelineConfig {
    fn default() -> Self {
        Self {
            batch_size: 32,
            shuffle: true,
            min_quality_score: 0.5,
            vocab_path: None,
            max_seq_len: 512,
            num_workers: 4,
        }
    }
}

/// Full training data pipeline: load → validate → normalize → tokenize → batch.
pub struct DataPipeline {
    config: PipelineConfig,
    loader: BatchLoader,
    tokenizer: BpeTokenizer,
    metrics: PipelineMetrics,
}

impl DataPipeline {
    /// Construct a new DataPipeline from config and data sources.
    pub fn new(config: PipelineConfig, sources: Vec<DataSource>) -> Result<Self, BatchError> {
        // Build tokenizer
        let tokenizer = match &config.vocab_path {
            Some(path) => BpeTokenizer::load_from_file(path)
                .unwrap_or_else(|_| BpeTokenizer::bootstrap_character_level(32_000)),
            None => BpeTokenizer::bootstrap_character_level(32_000),
        };

        // Configure Rayon thread pool
        rayon::ThreadPoolBuilder::new()
            .num_threads(config.num_workers)
            .build_global()
            .ok(); // Ignore error if already initialized

        let validator = RecordValidator::new(config.min_quality_score);
        let mut loader = BatchLoader::new(config.batch_size)
            .with_validator(validator)
            .with_shuffle(config.shuffle);

        for src in sources {
            loader = loader.add_source(src);
        }

        Ok(Self {
            config,
            loader,
            tokenizer,
            metrics: PipelineMetrics::default(),
        })
    }

    /// Run one full epoch: load all data, tokenize, and return all batches.
    pub fn epoch(&mut self) -> Result<Vec<DataBatch>, BatchError> {
        let _timer = self.metrics.start_epoch();
        info!("Pipeline: starting epoch");

        let batches = self.loader.batches(|text| {
            let ids = self.tokenizer.encode(text);
            // Truncate to max_seq_len
            if ids.len() > self.config.max_seq_len {
                ids[..self.config.max_seq_len].to_vec()
            } else {
                ids
            }
        })?;

        self.metrics.record_epoch_batches(batches.len());
        info!("Pipeline: epoch complete — {} batches", batches.len());
        Ok(batches)
    }

    /// Return pipeline metrics snapshot.
    pub fn metrics(&self) -> &PipelineMetrics {
        &self.metrics
    }

    /// Vocabulary size of the tokenizer.
    pub fn vocab_size(&self) -> usize {
        self.tokenizer.vocab_size()
    }
}
