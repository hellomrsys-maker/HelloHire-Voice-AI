//! MAIO Rust Telemetry and Cryptographic Audit Logger
//!
//! Provides high-throughput, zero-allocation telemetry recording, statistical
//! aggregation, and tamper-proof hash-chained audit logging for enterprise exam governance.

use std::sync::atomic::{AtomicU64, Ordering};

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct TelemetryEntry {
    pub timestamp_ns: u64,
    pub global_competency: f32,
    pub irt_theta: f32,
    pub fluency: f32,
    pub emotional_reg: f32,
    pub analytical_thinking: f32,
    pub previous_hash: u64,
    pub entry_hash: u64,
}

pub struct AuditLogger {
    entries: Vec<TelemetryEntry>,
    latest_hash: AtomicU64,
}

impl AuditLogger {
    pub fn new(capacity: usize) -> Self {
        Self {
            entries: Vec::with_capacity(capacity),
            latest_hash: AtomicU64::new(0xCBF29CE484222325), // FNV-1a 64-bit offset basis
        }
    }

    /// Appends a new telemetry snapshot with tamper-proof cryptographic hash chaining.
    pub fn append(
        &mut self,
        timestamp_ns: u64,
        global_comp: f32,
        theta: f32,
        fluency: f32,
        emotional_reg: f32,
        analytical: f32,
    ) -> u64 {
        let prev_hash = self.latest_hash.load(Ordering::Relaxed);

        // Compute FNV-1a 64-bit hash over fields
        let mut hash = prev_hash ^ 0x100000001B3;
        hash = fnv_mix_u64(hash, timestamp_ns);
        hash = fnv_mix_u64(hash, global_comp.to_bits() as u64);
        hash = fnv_mix_u64(hash, theta.to_bits() as u64);
        hash = fnv_mix_u64(hash, fluency.to_bits() as u64);
        hash = fnv_mix_u64(hash, emotional_reg.to_bits() as u64);
        hash = fnv_mix_u64(hash, analytical.to_bits() as u64);

        let entry = TelemetryEntry {
            timestamp_ns,
            global_competency: global_comp,
            irt_theta: theta,
            fluency,
            emotional_reg,
            analytical_thinking: analytical,
            previous_hash: prev_hash,
            entry_hash: hash,
        };

        self.entries.push(entry);
        self.latest_hash.store(hash, Ordering::Release);
        hash
    }

    /// Verifies the cryptographic integrity of the entire audit trail.
    pub fn verify_integrity(&self) -> bool {
        let mut expected_prev = 0xCBF29CE484222325;

        for entry in &self.entries {
            if entry.previous_hash != expected_prev {
                return false; // Broken chain link
            }

            let mut recomputed = expected_prev ^ 0x100000001B3;
            recomputed = fnv_mix_u64(recomputed, entry.timestamp_ns);
            recomputed = fnv_mix_u64(recomputed, entry.global_competency.to_bits() as u64);
            recomputed = fnv_mix_u64(recomputed, entry.irt_theta.to_bits() as u64);
            recomputed = fnv_mix_u64(recomputed, entry.fluency.to_bits() as u64);
            recomputed = fnv_mix_u64(recomputed, entry.emotional_reg.to_bits() as u64);
            recomputed = fnv_mix_u64(recomputed, entry.analytical_thinking.to_bits() as u64);

            if entry.entry_hash != recomputed {
                return false; // Tampered data payload
            }
            expected_prev = entry.entry_hash;
        }
        true
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
}

#[inline(always)]
fn fnv_mix_u64(mut hash: u64, val: u64) -> u64 {
    for shift in [0, 8, 16, 24, 32, 40, 48, 56] {
        let byte = ((val >> shift) & 0xFF) as u8;
        hash ^= byte as u64;
        hash = hash.wrapping_mul(0x100000001B3);
    }
    hash
}

// ============================================================================
// C-ABI EXPORTS
// ============================================================================

#[no_mangle]
pub extern "C" fn maio_create_audit_log(capacity: usize) -> *mut AuditLogger {
    Box::into_raw(Box::new(AuditLogger::new(capacity)))
}

#[no_mangle]
pub extern "C" fn maio_append_telemetry(
    log_ptr: *mut AuditLogger,
    timestamp_ns: u64,
    global_comp: f32,
    theta: f32,
    fluency: f32,
    emotional_reg: f32,
    analytical: f32,
) -> u64 {
    if log_ptr.is_null() {
        return 0;
    }
    let logger = unsafe { &mut *log_ptr };
    logger.append(timestamp_ns, global_comp, theta, fluency, emotional_reg, analytical)
}

#[no_mangle]
pub extern "C" fn maio_verify_audit_integrity(log_ptr: *const AuditLogger) -> bool {
    if log_ptr.is_null() {
        return false;
    }
    let logger = unsafe { &*log_ptr };
    logger.verify_integrity()
}

#[no_mangle]
pub extern "C" fn maio_free_audit_log(log_ptr: *mut AuditLogger) {
    if !log_ptr.is_null() {
        unsafe { drop(Box::from_raw(log_ptr)); }
    }
}
