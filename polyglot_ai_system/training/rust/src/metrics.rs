// training/rust/src/metrics.rs
//! Pipeline metrics collection and reporting.

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Instant;

#[derive(Debug, Default)]
pub struct PipelineMetrics {
    pub epochs_completed: AtomicU64,
    pub total_batches: AtomicU64,
    pub total_records_processed: AtomicU64,
    pub total_records_rejected: AtomicU64,
}

impl PipelineMetrics {
    pub fn start_epoch(&self) -> EpochTimer {
        EpochTimer {
            start: Instant::now(),
            metrics: Arc::new(self as *const _ as usize),
        }
    }

    pub fn record_epoch_batches(&self, n: usize) {
        self.total_batches.fetch_add(n as u64, Ordering::Relaxed);
        self.epochs_completed.fetch_add(1, Ordering::Relaxed);
    }

    pub fn snapshot(&self) -> MetricsSnapshot {
        MetricsSnapshot {
            epochs: self.epochs_completed.load(Ordering::Relaxed),
            total_batches: self.total_batches.load(Ordering::Relaxed),
            processed: self.total_records_processed.load(Ordering::Relaxed),
            rejected: self.total_records_rejected.load(Ordering::Relaxed),
        }
    }
}

pub struct MetricsSnapshot {
    pub epochs: u64,
    pub total_batches: u64,
    pub processed: u64,
    pub rejected: u64,
}

/// RAII timer for an epoch — measures wall time.
pub struct Timer {
    pub start: Instant,
    pub label: String,
}

impl Timer {
    pub fn new(label: impl Into<String>) -> Self {
        Self { start: Instant::now(), label: label.into() }
    }

    pub fn elapsed_ms(&self) -> f64 {
        self.start.elapsed().as_secs_f64() * 1000.0
    }
}

impl Drop for Timer {
    fn drop(&mut self) {
        let elapsed = self.start.elapsed().as_secs_f64() * 1000.0;
        tracing::debug!("[{}] elapsed: {:.2} ms", self.label, elapsed);
    }
}

// EpochTimer is a lightweight RAII wrapper
pub struct EpochTimer {
    start: Instant,
    metrics: Arc<usize>, // raw pointer stored as usize to avoid lifetime
}

impl Drop for EpochTimer {
    fn drop(&mut self) {
        let _elapsed = self.start.elapsed().as_secs_f64() * 1000.0;
        // Epoch timing logged via Timer drop
    }
}
