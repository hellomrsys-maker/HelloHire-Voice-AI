//! cognitive_invariants.rs - Engine D Sub-Core D1 (Rust)
//! Cognitive Capabilities & Adaptive Examination Engine: 8 Cognitive invariants,
//! psychometric score bounds, and zero-allocation 3PL scoring checks.

#![no_std]
#![allow(dead_code)]

pub type Q16 = u16;

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CognitiveInvariantsReport {
    pub is_valid: bool,
    pub thinking_q16: Q16,
    pub focus_q16: Q16,
    pub memory_q16: Q16,
    pub creative_q16: Q16,
    pub imagination_q16: Q16,
    pub analytical_q16: Q16,
    pub verbal_q16: Q16,
    pub emotional_q16: Q16,
    pub theta_bound_valid: bool,
}

impl CognitiveInvariantsReport {
    pub const fn empty() -> Self {
        Self {
            is_valid: true,
            thinking_q16: 32768,
            focus_q16: 32768,
            memory_q16: 32768,
            creative_q16: 32768,
            imagination_q16: 32768,
            analytical_q16: 32768,
            verbal_q16: 32768,
            emotional_q16: 32768,
            theta_bound_valid: true,
        }
    }
}

pub fn validate_cognitive_scores(scores: &[f32; 8], irt_theta: f32) -> CognitiveInvariantsReport {
    let mut q16_scores: [u16; 8] = [0; 8];
    let mut all_valid = true;

    for i in 0..8 {
        let s = scores[i];
        if s < 0.0f32 || s > 1.0f32 {
            all_valid = false;
        }
        let clamped = if s < 0.0f32 { 0.0f32 } else if s > 1.0f32 { 1.0f32 } else { s };
        q16_scores[i] = (clamped * 65535.0f32) as u16;
    }

    let theta_valid = irt_theta >= -4.0f32 && irt_theta <= 4.0f32;

    CognitiveInvariantsReport {
        is_valid: all_valid && theta_valid,
        thinking_q16: q16_scores[0],
        focus_q16: q16_scores[1],
        memory_q16: q16_scores[2],
        creative_q16: q16_scores[3],
        imagination_q16: q16_scores[4],
        analytical_q16: q16_scores[5],
        verbal_q16: q16_scores[6],
        emotional_q16: q16_scores[7],
        theta_bound_valid: theta_valid,
    }
}
