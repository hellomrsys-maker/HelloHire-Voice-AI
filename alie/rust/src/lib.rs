//! lib.rs — ALIE Rust crate root
pub mod listening_stream;

use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct AlieSummary {
    pub jaccard: f32,
    pub pronoun_echo: u8,
    pub repair_count: u32,
    pub entity_carry: u32,
    pub latency_score: f32,
    pub composite: f32,
}

#[no_mangle]
pub extern "C" fn alie_rust_analyze(
    question_ptr: *const c_char,
    answer_ptr: *const c_char,
    latency_ms: f32,
    out: *mut AlieSummary,
) -> i32 {
    if question_ptr.is_null() || answer_ptr.is_null() || out.is_null() {
        return -1;
    }
    let q = unsafe { CStr::from_ptr(question_ptr) }.to_str().unwrap_or("");
    let a = unsafe { CStr::from_ptr(answer_ptr) }.to_str().unwrap_or("");

    let res = listening_stream::analyze_listening_pair(q, a, &[], latency_ms);
    unsafe {
        (*out).jaccard = res.jaccard_topic_overlap;
        (*out).pronoun_echo = res.pronoun_echo_detected as u8;
        (*out).repair_count = res.repair_signal_count;
        (*out).entity_carry = res.entity_carry_count;
        (*out).latency_score = res.latency_score;
        (*out).composite = res.composite_listening_score;
    }
    0
}
