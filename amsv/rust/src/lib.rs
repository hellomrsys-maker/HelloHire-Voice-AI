//! Advanced Multi-language Shared Memory (AMSV) — Rust Safe Memory Layer.
//!
//! Provides zero-copy, memory-safe access to the 64-byte Atomic Memory State Vector
//! and lock-free SPSC audio stream ring buffer.

use std::sync::atomic::{AtomicU64, Ordering};
use std::slice;

#[repr(C, align(64))]
pub struct AtomicStateVector {
    pub vce_phoneme_state: AtomicU64,
    pub vce_prosody_state: AtomicU64,
    pub ccte_cog_bank_alpha: AtomicU64,
    pub ccte_cog_bank_beta: AtomicU64,
    pub rsse_scenario_state: AtomicU64,
    pub aeee_examination_state: AtomicU64,
    pub maio_global_state_alpha: AtomicU64,
    pub maio_global_state_beta: AtomicU64,
}

const AUDIO_BUFFER_CAPACITY: usize = 65536;
const AUDIO_BUFFER_MASK: usize = AUDIO_BUFFER_CAPACITY - 1;

#[repr(C, align(64))]
pub struct LockFreeAudioRingBuffer {
    pub write_head: AtomicU64,
    pub read_tail: AtomicU64,
    pub samples: [f32; AUDIO_BUFFER_CAPACITY],
}

impl LockFreeAudioRingBuffer {
    pub fn push(&mut self, sample: f32) -> bool {
        let current_head = self.write_head.load(Ordering::Relaxed);
        let current_tail = self.read_tail.load(Ordering::Acquire);

        if current_head.wrapping_sub(current_tail) >= AUDIO_BUFFER_CAPACITY as u64 {
            return false; // Overflow
        }

        let idx = (current_head as usize) & AUDIO_BUFFER_MASK;
        self.samples[idx] = sample;
        self.write_head.store(current_head.wrapping_add(1), Ordering::Release);
        true
    }

    pub fn pop(&mut self) -> Option<f32> {
        let current_tail = self.read_tail.load(Ordering::Relaxed);
        let current_head = self.write_head.load(Ordering::Acquire);

        if current_tail == current_head {
            return None; // Underflow
        }

        let idx = (current_tail as usize) & AUDIO_BUFFER_MASK;
        let val = self.samples[idx];
        self.read_tail.store(current_tail.wrapping_add(1), Ordering::Release);
        Some(val)
    }

    pub fn available_read(&self) -> usize {
        let current_tail = self.read_tail.load(Ordering::Relaxed);
        let current_head = self.write_head.load(Ordering::Acquire);
        if current_head >= current_tail {
            (current_head - current_tail) as usize
        } else {
            0
        }
    }
}

/// Safe Rust reference to the 64-byte Atomic Memory State Vector.
pub struct AMSVSafeView<'a> {
    vector: &'a AtomicStateVector,
}

impl<'a> AMSVSafeView<'a> {
    pub unsafe fn from_raw_ptr(ptr: *const AtomicStateVector) -> Self {
        assert!(!ptr.is_null(), "AMSV pointer cannot be null");
        assert_eq!(ptr as usize % 64, 0, "AMSV pointer must be 64-byte aligned");
        Self { vector: &*ptr }
    }

    pub fn get_phoneme_state(&self) -> u64 {
        self.vector.vce_phoneme_state.load(Ordering::Acquire)
    }

    pub fn set_phoneme_state(&self, val: u64) {
        self.vector.vce_phoneme_state.store(val, Ordering::Release);
    }

    pub fn get_prosody_state(&self) -> u64 {
        self.vector.vce_prosody_state.load(Ordering::Acquire)
    }

    pub fn set_prosody_state(&self, val: u64) {
        self.vector.vce_prosody_state.store(val, Ordering::Release);
    }

    pub fn get_cognitive_score(&self, capability_index: usize) -> f32 {
        assert!(capability_index < 8, "Capability index must be 0..7");
        let bank = if capability_index < 4 {
            self.vector.ccte_cog_bank_alpha.load(Ordering::Acquire)
        } else {
            self.vector.ccte_cog_bank_beta.load(Ordering::Acquire)
        };
        let shift = (capability_index % 4) * 16;
        let raw_val = ((bank >> shift) & 0xFFFF) as u16;
        (raw_val as f32) / 65535.0
    }

    pub fn set_cognitive_score(&self, capability_index: usize, score: f32) {
        assert!(capability_index < 8, "Capability index must be 0..7");
        let clamped = score.clamp(0.0, 1.0);
        let fixed_val = (clamped * 65535.0).round() as u64;
        let shift = (capability_index % 4) * 16;
        let mask = !(0xFFFFu64 << shift);

        let target_atomic = if capability_index < 4 {
            &self.vector.ccte_cog_bank_alpha
        } else {
            &self.vector.ccte_cog_bank_beta
        };

        // Atomic compare-and-swap update
        let mut current = target_atomic.load(Ordering::Relaxed);
        loop {
            let new_val = (current & mask) | (fixed_val << shift);
            match target_atomic.compare_exchange_weak(current, new_val, Ordering::SeqCst, Ordering::Relaxed) {
                Ok(_) => break,
                Err(actual) => current = actual,
            }
        }
    }

    pub fn get_examination_theta(&self) -> f32 {
        let raw = self.vector.aeee_examination_state.load(Ordering::Acquire);
        f32::from_bits((raw & 0xFFFFFFFF) as u32)
    }

    pub fn set_examination_theta(&self, theta: f32) {
        let theta_bits = (theta.to_bits() as u64) & 0xFFFFFFFF;
        let current = self.vector.aeee_examination_state.load(Ordering::Relaxed);
        let updated = (current & 0xFFFFFFFF00000000) | theta_bits;
        self.vector.aeee_examination_state.store(updated, Ordering::Release);
    }
}
