//! AEEE Rust 3PL Item Response Theory & Adaptive Examination Engine
//!
//! Provides ultra-low latency, sub-microsecond IRT ability estimation,
//! Fisher Information maximization, and zero-bridge AMSV synchronization.

use std::sync::atomic::{AtomicU64, Ordering};

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct ItemCalibration {
    pub a: f32, // Discrimination
    pub b: f32, // Difficulty
    pub c: f32, // Pseudo-guessing
}

pub struct AdaptiveSession {
    pub current_theta: f32,
    pub standard_error: f32,
    pub target_sem: f32,
    pub max_items: u32,
    pub question_count: u32,
    administered_items: Vec<ItemCalibration>,
    responses: Vec<f32>,
}

impl AdaptiveSession {
    pub fn new(max_items: u32, target_sem: f32) -> Self {
        Self {
            current_theta: 0.0,
            standard_error: 1.0,
            target_sem,
            max_items,
            question_count: 0,
            administered_items: Vec::with_capacity(max_items as usize),
            responses: Vec::with_capacity(max_items as usize),
        }
    }

    /// Evaluates 3PL response probability: P(θ) = c + (1 - c) / (1 + exp(-a (θ - b)))
    #[inline(always)]
    pub fn probability_3pl(&self, theta: f32, item: &ItemCalibration) -> f32 {
        let exp_term = (-item.a * (theta - item.b).clamp(-20.0, 20.0)).exp();
        let p_star = 1.0 / (1.0 + exp_term);
        item.c + (1.0 - item.c) * p_star
    }

    /// Computes Fisher Information: I(θ) = a^2 * (P - c)^2 / (1 - c)^2 * (1 - P) / P
    #[inline(always)]
    pub fn fisher_information(&self, theta: f32, item: &ItemCalibration) -> f32 {
        let p = self.probability_3pl(theta, item);
        if p <= item.c || p >= 1.0 {
            return 0.0;
        }
        let p_star = (p - item.c) / (1.0 - item.c);
        let numerator = (item.a * item.a) * (p_star * p_star) * (1.0 - p);
        numerator / p
    }

    /// Ingests candidate response score u in [0.0, 1.0], updates theta and SEM via Newton-Raphson.
    pub fn submit_response(&mut self, u: f32, item: ItemCalibration) -> (f32, f32) {
        self.question_count += 1;
        self.administered_items.push(item);
        self.responses.push(u.clamp(0.0, 1.0));

        let theta = self.current_theta;
        let mut total_score_grad = -theta; // Prior N(0, 1) log-gradient
        let mut total_info = 1.0f32;       // Prior precision

        for (i, itm) in self.administered_items.iter().enumerate() {
            let resp = self.responses[i];
            let p = self.probability_3pl(theta, itm);
            let info = self.fisher_information(theta, itm);

            total_score_grad += itm.a * (resp - p);
            total_info += info;
        }

        let delta_theta = (total_score_grad / total_info).clamp(-0.75, 0.75);
        self.current_theta = (theta + delta_theta).clamp(-3.5, 3.5);
        self.standard_error = 1.0 / total_info.max(0.1).sqrt();

        (self.current_theta, self.standard_error)
    }

    pub fn is_completed(&self) -> bool {
        self.question_count >= self.max_items ||
            (self.question_count >= 3 && self.standard_error <= self.target_sem)
    }
}

// ============================================================================
// C-ABI EXPORTS
// ============================================================================

#[no_mangle]
pub extern "C" fn aeee_create_session(max_items: u32, target_sem: f32) -> *mut AdaptiveSession {
    Box::into_raw(Box::new(AdaptiveSession::new(max_items, target_sem)))
}

#[no_mangle]
pub extern "C" fn aeee_submit_response(
    sess_ptr: *mut AdaptiveSession,
    response_score: f32,
    a: f32,
    b: f32,
    c: f32,
    out_theta: *mut f32,
    out_sem: *mut f32,
) -> bool {
    if sess_ptr.is_null() {
        return false;
    }
    let sess = unsafe { &mut *sess_ptr };
    let item = ItemCalibration { a, b, c };
    let (new_theta, new_sem) = sess.submit_response(response_score, item);

    if !out_theta.is_null() {
        unsafe { *out_theta = new_theta; }
    }
    if !out_sem.is_null() {
        unsafe { *out_sem = new_sem; }
    }
    true
}

#[no_mangle]
pub extern "C" fn aeee_check_stopping_rule(sess_ptr: *const AdaptiveSession) -> bool {
    if sess_ptr.is_null() {
        return true;
    }
    let sess = unsafe { &*sess_ptr };
    sess.is_completed()
}

#[no_mangle]
pub extern "C" fn aeee_sync_to_amsv(
    amsv_u64_slot5_ptr: *mut u64,
    theta: f32,
    sem: f32,
    question_idx: u16,
) {
    if amsv_u64_slot5_ptr.is_null() {
        return;
    }
    let theta_bits = theta.to_bits();
    let sem_q16 = ((sem.clamp(0.0, 1.0) * 65535.0) as u16) as u64;
    let word: u64 = (theta_bits as u64)
        | (sem_q16 << 32)
        | ((question_idx as u64) << 48);

    let atomic_ref = unsafe { &*(amsv_u64_slot5_ptr as *const AtomicU64) };
    atomic_ref.store(word, Ordering::Release);
}

#[no_mangle]
pub extern "C" fn aeee_free_session(sess_ptr: *mut AdaptiveSession) {
    if !sess_ptr.is_null() {
        unsafe { drop(Box::from_raw(sess_ptr)); }
    }
}
