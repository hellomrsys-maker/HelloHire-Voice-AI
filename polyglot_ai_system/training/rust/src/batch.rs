// training/rust/src/batch.rs
//! Batch loading and batching logic for the training data pipeline.
//! Loads JSONL records concurrently, validates, normalizes, and emits DataBatches.

use crate::normalizer::Normalizer;
use crate::record::{TrainingRecord, ValidationError};
use crate::validator::RecordValidator;
use crate::{increment_processed, increment_rejected};

use rayon::prelude::*;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use thiserror::Error;
use tracing::{debug, info, warn};

#[derive(Debug, Error)]
pub enum BatchError {
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON parse error on line {line}: {source}")]
    Json { line: usize, source: serde_json::Error },
    #[error("Empty data source: {path}")]
    EmptySource { path: String },
}

/// Identifies a data source (file path + format).
#[derive(Debug, Clone)]
pub struct DataSource {
    pub path: PathBuf,
    pub format: DataFormat,
    pub language_filter: Option<String>,
    pub family_filter: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DataFormat {
    Jsonl,
    Json,
}

impl DataSource {
    pub fn jsonl<P: Into<PathBuf>>(path: P) -> Self {
        Self {
            path: path.into(),
            format: DataFormat::Jsonl,
            language_filter: None,
            family_filter: None,
        }
    }

    pub fn with_language_filter(mut self, lang: impl Into<String>) -> Self {
        self.language_filter = Some(lang.into());
        self
    }

    pub fn with_family_filter(mut self, family: impl Into<String>) -> Self {
        self.family_filter = Some(family.into());
        self
    }
}

/// A processed batch of training records ready for the model.
#[derive(Debug, Clone)]
pub struct DataBatch {
    /// Batch index within the current epoch
    pub batch_idx: usize,
    /// Records in this batch
    pub records: Vec<TrainingRecord>,
    /// Per-record token ID sequences (tokenized assembled_output)
    pub token_ids: Vec<Vec<u32>>,
    /// Sequence lengths
    pub lengths: Vec<usize>,
}

impl DataBatch {
    pub fn len(&self) -> usize {
        self.records.len()
    }

    pub fn is_empty(&self) -> bool {
        self.records.is_empty()
    }

    /// Maximum sequence length in this batch.
    pub fn max_len(&self) -> usize {
        self.lengths.iter().copied().max().unwrap_or(0)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// BatchLoader
// ─────────────────────────────────────────────────────────────────────────────

pub struct BatchLoader {
    sources: Vec<DataSource>,
    validator: RecordValidator,
    normalizer: Normalizer,
    batch_size: usize,
    shuffle: bool,
}

impl BatchLoader {
    pub fn new(batch_size: usize) -> Self {
        Self {
            sources: Vec::new(),
            validator: RecordValidator::default(),
            normalizer: Normalizer::default(),
            batch_size,
            shuffle: true,
        }
    }

    pub fn add_source(mut self, source: DataSource) -> Self {
        self.sources.push(source);
        self
    }

    pub fn with_validator(mut self, validator: RecordValidator) -> Self {
        self.validator = validator;
        self
    }

    pub fn with_shuffle(mut self, shuffle: bool) -> Self {
        self.shuffle = shuffle;
        self
    }

    /// Load all records from all sources in parallel, validate and normalize.
    pub fn load_all(&self) -> Result<Vec<TrainingRecord>, BatchError> {
        let all_records: Vec<Result<Vec<TrainingRecord>, BatchError>> = self
            .sources
            .par_iter()
            .map(|src| self.load_source(src))
            .collect();

        let mut merged = Vec::new();
        for result in all_records {
            let records = result?;
            for record in records {
                match self.validator.validate(&record) {
                    Ok(()) => {
                        increment_processed();
                        // Normalize slot values
                        let normalized_slots =
                            self.normalizer.normalize_slots(&record.slot_values);
                        let normalized_output =
                            self.normalizer.normalize(&record.assembled_output);
                        merged.push(TrainingRecord {
                            slot_values: normalized_slots,
                            assembled_output: normalized_output,
                            normalized: true,
                            ..record
                        });
                    }
                    Err(e) => {
                        increment_rejected();
                        debug!("Rejected record: {}", e);
                    }
                }
            }
        }

        if self.shuffle {
            use rand::seq::SliceRandom;
            let mut rng = rand::thread_rng();
            merged.shuffle(&mut rng);
        }

        info!("Loaded {} usable records total", merged.len());
        Ok(merged)
    }

    /// Load records from a single data source.
    fn load_source(&self, source: &DataSource) -> Result<Vec<TrainingRecord>, BatchError> {
        let path = &source.path;
        if !path.exists() {
            warn!("Data source does not exist: {}", path.display());
            return Ok(vec![]);
        }

        let file = File::open(path)?;
        let reader = BufReader::with_capacity(256 * 1024, file);
        let mut records = Vec::new();

        match source.format {
            DataFormat::Jsonl => {
                for (line_idx, line_result) in reader.lines().enumerate() {
                    let line = line_result?;
                    let trimmed = line.trim();
                    if trimmed.is_empty() {
                        continue;
                    }
                    let record: TrainingRecord = serde_json::from_str(trimmed).map_err(|e| {
                        BatchError::Json {
                            line: line_idx + 1,
                            source: e,
                        }
                    })?;

                    // Apply source-level filters
                    if let Some(ref lang) = source.language_filter {
                        if &record.language != lang {
                            continue;
                        }
                    }
                    if let Some(ref family) = source.family_filter {
                        if &record.component_family != family {
                            continue;
                        }
                    }

                    records.push(record);
                }
            }
            DataFormat::Json => {
                let content = std::fs::read_to_string(path)?;
                let parsed: Vec<TrainingRecord> = serde_json::from_str(&content)
                    .map_err(|e| BatchError::Json { line: 0, source: e })?;
                records.extend(parsed);
            }
        }

        Ok(records)
    }

    /// Iterate over all records as fixed-size DataBatches.
    /// The provided tokenizer function converts assembled_output to token IDs.
    pub fn batches<F>(
        &self,
        tokenize_fn: F,
    ) -> Result<Vec<DataBatch>, BatchError>
    where
        F: Fn(&str) -> Vec<u32> + Send + Sync,
    {
        let records = self.load_all()?;
        let batches: Vec<DataBatch> = records
            .chunks(self.batch_size)
            .enumerate()
            .map(|(batch_idx, chunk)| {
                let token_ids: Vec<Vec<u32>> = chunk
                    .par_iter()
                    .map(|r| tokenize_fn(&r.assembled_output))
                    .collect();
                let lengths: Vec<usize> = token_ids.iter().map(|ids| ids.len()).collect();
                DataBatch {
                    batch_idx,
                    records: chunk.to_vec(),
                    token_ids,
                    lengths,
                }
            })
            .collect();

        info!("Created {} batches of size {}", batches.len(), self.batch_size);
        Ok(batches)
    }
}
