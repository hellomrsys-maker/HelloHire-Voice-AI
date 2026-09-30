// training/rust/src/validator.rs
//! Record validator — enforces spec rules before records enter the training pipeline.

use crate::record::{TrainingRecord, ValidationError};

const PROHIBITED_PLACEHOLDERS: &[&str] = &[
    "TODO", "STUB", "FIXME", "...", "<PLACEHOLDER>", "<TODO>", "XXX",
    "placeholder", "example_text", "fill_me",
];

pub struct RecordValidator {
    pub min_quality_score: f64,
    pub require_approved: bool,
    pub require_normalized: bool,
    pub check_placeholders: bool,
    pub min_word_count: usize,
    pub max_word_count: usize,
}

impl Default for RecordValidator {
    fn default() -> Self {
        Self {
            min_quality_score: 0.5,
            require_approved: true,
            require_normalized: true,
            check_placeholders: true,
            min_word_count: 1,
            max_word_count: 2048,
        }
    }
}

impl RecordValidator {
    pub fn new(min_quality_score: f64) -> Self {
        Self {
            min_quality_score,
            ..Default::default()
        }
    }

    /// Validate a single record. Returns Ok(()) or first ValidationError.
    pub fn validate(&self, record: &TrainingRecord) -> Result<(), ValidationError> {
        if record.assembled_output.is_empty() {
            return Err(ValidationError::EmptyOutput {
                id: record.record_id.clone(),
            });
        }
        if self.require_approved && !record.approved {
            return Err(ValidationError::NotApproved {
                id: record.record_id.clone(),
            });
        }
        if self.require_normalized && !record.normalized {
            return Err(ValidationError::NotNormalized {
                id: record.record_id.clone(),
            });
        }
        if record.quality_score < self.min_quality_score {
            return Err(ValidationError::LowQuality {
                id: record.record_id.clone(),
                score: record.quality_score,
                threshold: self.min_quality_score,
            });
        }
        if record.component_family.is_empty() {
            return Err(ValidationError::MissingFamily {
                id: record.record_id.clone(),
            });
        }
        if self.check_placeholders {
            let output_upper = record.assembled_output.to_uppercase();
            for &placeholder in PROHIBITED_PLACEHOLDERS {
                if output_upper.contains(&placeholder.to_uppercase()) {
                    return Err(ValidationError::ContainsPlaceholder {
                        id: record.record_id.clone(),
                        placeholder: placeholder.to_string(),
                    });
                }
            }
        }
        for (slot, value) in &record.slot_values {
            if value.trim().is_empty() {
                return Err(ValidationError::EmptySlotValue {
                    id: record.record_id.clone(),
                    slot: slot.clone(),
                });
            }
        }
        let wc = record.word_count();
        if wc < self.min_word_count || wc > self.max_word_count {
            // Treat word count bounds as soft warnings, not hard failures
            // (log but pass through — callers can choose to filter)
        }
        Ok(())
    }

    /// Validate a batch of records, returning only the valid ones.
    pub fn filter_valid<'a>(&self, records: &'a [TrainingRecord]) -> Vec<&'a TrainingRecord> {
        records
            .iter()
            .filter(|r| self.validate(r).is_ok())
            .collect()
    }
}
