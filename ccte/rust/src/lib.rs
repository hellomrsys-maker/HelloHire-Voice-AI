//! CCTE Rust Cognitive Telemetry & Atomic Vector Pack/Unpack Library
//!
//! Provides high-throughput, zero-allocation conversion between 8-dimensional
//! continuous cognitive scores and the 64-byte AMSV State Vector's Q16 fixed-point slots.

use std::sync::atomic::{AtomicU64, Ordering};

#[repr(C)]
#[derive(Debug, Clone, Copy, Default)]
pub struct CognitiveScores {
    pub thinking_ability: f32,
    pub concentration_focus: f32,
    pub memory_recall: f32,
    pub creative_thinking: f32,
    pub imagination: f32,
    pub analytical_thinking: f32,
    pub verbal_reasoning: f32,
    pub emotional_regulation: f32,
}

impl CognitiveScores {
    /// Packs the 8 continuous scores into two 64-bit unsigned words (Q16 fixed point).
    /// Word Alpha: Thinking (0..15), Focus (16..31), Memory (32..47), Creativity (48..63).
    /// Word Beta:  Imagination (0..15), Analytical (16..31), Verbal (32..47), Emotional (48..63).
    pub fn to_amsv_words(&self) -> (u64, u64) {
        let t_q16 = to_q16(self.thinking_ability);
        let f_q16 = to_q16(self.concentration_focus);
        let m_q16 = to_q16(self.memory_recall);
        let c_q16 = to_q16(self.creative_thinking);

        let i_q16 = to_q16(self.imagination);
        let a_q16 = to_q16(self.analytical_thinking);
        let v_q16 = to_q16(self.verbal_reasoning);
        let e_q16 = to_q16(self.emotional_regulation);

        let alpha = (t_q16 as u64)
            | ((f_q16 as u64) << 16)
            | ((m_q16 as u64) << 32)
            | ((c_q16 as u64) << 48);

        let beta = (i_q16 as u64)
            | ((a_q16 as u64) << 16)
            | ((v_q16 as u64) << 32)
            | ((e_q16 as u64) << 48);

        (alpha, beta)
    }

    /// Unpacks two 64-bit unsigned words from AMSV into 8 continuous normalized floats.
    pub fn from_amsv_words(alpha: u64, beta: u64) -> Self {
        Self {
            thinking_ability: from_q16((alpha & 0xFFFF) as u16),
            concentration_focus: from_q16(((alpha >> 16) & 0xFFFF) as u16),
            memory_recall: from_q16(((alpha >> 32) & 0xFFFF) as u16),
            creative_thinking: from_q16(((alpha >> 48) & 0xFFFF) as u16),

            imagination: from_q16((beta & 0xFFFF) as u16),
            analytical_thinking: from_q16(((beta >> 16) & 0xFFFF) as u16),
            verbal_reasoning: from_q16(((beta >> 32) & 0xFFFF) as u16),
            emotional_regulation: from_q16(((beta >> 48) & 0xFFFF) as u16),
        }
    }

    /// Detects whether candidate is experiencing cognitive overload or panic freeze.
    pub fn is_overloaded(&self) -> bool {
        // Condition: High analytical demand combined with low emotional regulation or focus drop
        self.emotional_regulation < 0.35 || (self.concentration_focus < 0.40 && self.thinking_ability > 0.70)
    }
}

#[inline(always)]
fn to_q16(val: f32) -> u16 {
    (val.clamp(0.0, 1.0) * 65535.0) as u16
}

#[inline(always)]
fn from_q16(raw: u16) -> f32 {
    (raw as f32) / 65535.0
}

// ============================================================================
// C-ABI EXPORTS
// ============================================================================

#[no_mangle]
pub extern "C" fn ccte_pack_capabilities(
    thinking: f32,
    focus: f32,
    memory: f32,
    creativity: f32,
    imagination: f32,
    analytical: f32,
    verbal: f32,
    emotional: f32,
    out_alpha: *mut u64,
    out_beta: *mut u64,
) {
    if out_alpha.is_null() || out_beta.is_null() {
        return;
    }
    let scores = CognitiveScores {
        thinking_ability: thinking,
        concentration_focus: focus,
        memory_recall: memory,
        creative_thinking: creativity,
        imagination,
        analytical_thinking: analytical,
        verbal_reasoning: verbal,
        emotional_regulation: emotional,
    };
    let (alpha, beta) = scores.to_amsv_words();
    unsafe {
        *out_alpha = alpha;
        *out_beta = beta;
    }
}

#[no_mangle]
pub extern "C" fn ccte_unpack_capabilities(
    alpha: u64,
    beta: u64,
    out_scores_8: *mut f32,
) {
    if out_scores_8.is_null() {
        return;
    }
    let scores = CognitiveScores::from_amsv_words(alpha, beta);
    unsafe {
        let slice = std::slice::from_raw_parts_mut(out_scores_8, 8);
        slice[0] = scores.thinking_ability;
        slice[1] = scores.concentration_focus;
        slice[2] = scores.memory_recall;
        slice[3] = scores.creative_thinking;
        slice[4] = scores.imagination;
        slice[5] = scores.analytical_thinking;
        slice[6] = scores.verbal_reasoning;
        slice[7] = scores.emotional_regulation;
    }
}

#[no_mangle]
pub extern "C" fn ccte_detect_overload(alpha: u64, beta: u64) -> bool {
    let scores = CognitiveScores::from_amsv_words(alpha, beta);
    scores.is_overloaded()
}

#[no_mangle]
pub extern "C" fn ccte_atomic_sync_amsv(
    amsv_alpha_ptr: *mut u64,
    amsv_beta_ptr: *mut u64,
    scores_ptr: *const f32,
) {
    if amsv_alpha_ptr.is_null() || amsv_beta_ptr.is_null() || scores_ptr.is_null() {
        return;
    }
    let slice = unsafe { std::slice::from_raw_parts(scores_ptr, 8) };
    let scores = CognitiveScores {
        thinking_ability: slice[0],
        concentration_focus: slice[1],
        memory_recall: slice[2],
        creative_thinking: slice[3],
        imagination: slice[4],
        analytical_thinking: slice[5],
        verbal_reasoning: slice[6],
        emotional_regulation: slice[7],
    };
    let (alpha, beta) = scores.to_amsv_words();

    let atomic_alpha = unsafe { &*(amsv_alpha_ptr as *const AtomicU64) };
    let atomic_beta  = unsafe { &*(amsv_beta_ptr as *const AtomicU64) };

    atomic_alpha.store(alpha, Ordering::Release);
    atomic_beta.store(beta, Ordering::Release);
}
