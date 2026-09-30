//! CEFR Assessment & Adaptive Scoring Engine (Safe Rust)
//!
//! Provides zero-allocation proficiency mapping across CEFR stages (A1, A2, B1, B2, C1, C2)
//! and Item Response Theory (IRT) ability scaling.

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum CefrLevel {
    A1 = 1,
    A2 = 2,
    B1 = 3,
    B2 = 4,
    C1 = 5,
    C2 = 6,
}

pub struct AssessmentModel;

impl AssessmentModel {
    /// Maps raw percentage score [0.0, 100.0] to CEFR Level
    pub fn score_to_cefr(score: f32) -> CefrLevel {
        if score >= 90.0 {
            CefrLevel::C2
        } else if score >= 80.0 {
            CefrLevel::C1
        } else if score >= 70.0 {
            CefrLevel::B2
        } else if score >= 55.0 {
            CefrLevel::B1
        } else if score >= 40.0 {
            CefrLevel::A2
        } else {
            CefrLevel::A1
        }
    }

    /// Maps CEFR Level to IRT Ability Theta prior ($\theta \in [-3.0, +3.0]$)
    pub fn cefr_to_theta(level: CefrLevel) -> f32 {
        match level {
            CefrLevel::A1 => -2.0,
            CefrLevel::A2 => -1.0,
            CefrLevel::B1 => 0.0,
            CefrLevel::B2 => 0.8,
            CefrLevel::C1 => 1.6,
            CefrLevel::C2 => 2.5,
        }
    }

    /// Single Newton-Raphson IRT Ability Step:
    /// $\theta_{k+1} = \theta_k + \frac{\sum (u_i - P_i)}{\sum I_i}$
    pub fn update_theta_step(theta: f32, is_correct: bool, difficulty_b: f32, discrimination_a: f32) -> f32 {
        let u = if is_correct { 1.0f32 } else { 0.0f32 };
        let exp_term = ((-discrimination_a * (theta - difficulty_b)) as f64).exp() as f32;
        let p = 1.0f32 / (1.0f32 + exp_term);
        let info = (discrimination_a * discrimination_a) * p * (1.0f32 - p);

        let delta = (u - p) / (info.max(0.1f32));
        let updated = theta + delta;
        updated.clamp(-3.5f32, 3.5f32)
    }
}
