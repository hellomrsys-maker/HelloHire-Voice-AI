//! phonology_buffer_safety.rs - Engine C Sub-Core C1 (Rust)
//! Auditory & Phonological Voice Engine: Audio PCM buffer bounds, frame boundary safety,
//! and zero-allocation sample validation.

#![no_std]
#![allow(dead_code)]

pub type Q16 = u16;

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AudioBufferSafetyReport {
    pub is_valid: bool,
    pub sample_count: u32,
    pub peak_amplitude_q16: Q16,
    pub zero_crossing_rate_q16: Q16,
    pub clipping_detected: bool,
}

impl AudioBufferSafetyReport {
    pub const fn empty() -> Self {
        Self {
            is_valid: true,
            sample_count: 0,
            peak_amplitude_q16: 0,
            zero_crossing_rate_q16: 0,
            clipping_detected: false,
        }
    }
}

pub fn validate_pcm_samples(samples: &[i16]) -> AudioBufferSafetyReport {
    if samples.is_empty() {
        return AudioBufferSafetyReport {
            is_valid: false,
            sample_count: 0,
            peak_amplitude_q16: 0,
            zero_crossing_rate_q16: 0,
            clipping_detected: false,
        };
    }

    let mut peak: i16 = 0;
    let mut zero_crossings: u32 = 0;
    let mut prev_positive = samples[0] >= 0;
    let mut clipping = false;

    for &s in samples {
        let abs_val = if s == i16::MIN { i16::MAX } else { s.abs() };
        if abs_val > peak {
            peak = abs_val;
        }
        if abs_val >= 32760 {
            clipping = true;
        }

        let is_positive = s >= 0;
        if is_positive != prev_positive {
            zero_crossings += 1;
            prev_positive = is_positive;
        }
    }

    let peak_ratio = (peak as f32) / 32767.0f32;
    let peak_q16 = (peak_ratio.min(1.0f32) * 65535.0f32) as u16;
    let zcr = (zero_crossings as f32) / (samples.len() as f32);
    let zcr_q16 = (zcr.min(1.0f32) * 65535.0f32) as u16;

    AudioBufferSafetyReport {
        is_valid: samples.len() >= 16,
        sample_count: samples.len() as u32,
        peak_amplitude_q16: peak_q16,
        zero_crossing_rate_q16: zcr_q16,
        clipping_detected: clipping,
    }
}
