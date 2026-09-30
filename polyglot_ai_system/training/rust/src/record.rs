// training/rust/src/record.rs
//! Training record types and validation error definitions.
//! Spec constraint: NO raw dialogue stored — only slot+family structured items.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

/// A single approved, normalized training record.
/// Raw dialogue is never stored per spec rules.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrainingRecord {
    pub record_id: String,
    pub language: String,
    pub component_family: String,
    pub slot_values: HashMap<String, String>,
    pub assembled_output: String,
    pub normalized: bool,
    pub approved: bool,
    pub created_at: f64,
    pub quality_score: f64,
    pub tags: Vec<String>,
}

impl TrainingRecord {
    /// Returns true if the record is safe to use in a training batch.
    pub fn is_usable(&self) -> bool {
        self.approved
            && self.normalized
            && !self.assembled_output.is_empty()
            && self.quality_score >= 0.5
            && !self.component_family.is_empty()
    }

    /// Byte length of the assembled output (for bucketing).
    pub fn byte_len(&self) -> usize {
        self.assembled_output.len()
    }

    /// Word count of the assembled output.
    pub fn word_count(&self) -> usize {
        self.assembled_output.split_whitespace().count()
    }
}

/// Errors produced during record validation.
#[derive(Debug, Error)]
pub enum ValidationError {
    #[error("Record {id}: assembled_output is empty")]
    EmptyOutput { id: String },

    #[error("Record {id}: not approved")]
    NotApproved { id: String },

    #[error("Record {id}: not normalized")]
    NotNormalized { id: String },

    #[error("Record {id}: quality_score {score} below threshold {threshold}")]
    LowQuality {
        id: String,
        score: f64,
        threshold: f64,
    },

    #[error("Record {id}: contains prohibited placeholder '{placeholder}'")]
    ContainsPlaceholder { id: String, placeholder: String },

    #[error("Record {id}: component_family is empty")]
    MissingFamily { id: String },

    #[error("Record {id}: slot '{slot}' has empty value")]
    EmptySlotValue { id: String, slot: String },

    #[error("Deserialization error: {0}")]
    DeserializationError(#[from] serde_json::Error),
}
