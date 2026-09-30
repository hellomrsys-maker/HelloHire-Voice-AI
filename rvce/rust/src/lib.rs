//! lib.rs - RVCE Rust Layer Root
pub mod verbal_stream_processor;
pub mod cognitive_metrics;

use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct RustCandidateSummary {
    pub total_words: u32,
    pub unique_words: u32,
    pub ttr: f32,
    pub filler_ratio: f32,
    pub pace_wpm: f32,
    pub star_score: f32,
    pub composite_hireability: f32,
}

#[no_mangle]
pub extern "C" fn rvce_rust_analyze_transcript(
    transcript_ptr: *const c_char,
    duration_sec: f32,
    turn: u16,
    out_summary: *mut RustCandidateSummary,
) -> i32 {
    if transcript_ptr.is_null() || out_summary.is_null() {
        return -1;
    }
    let c_str = unsafe { CStr::from_ptr(transcript_ptr) };
    let text = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return -2,
    };

    let stream = verbal_stream_processor::process_transcript_stream(text, duration_sec);
    let cog = cognitive_metrics::extract_fast_cognitive_vector(text, stream.pace_wpm, turn, duration_sec / 60.0);

    unsafe {
        (*out_summary).total_words = stream.total_words as u32;
        (*out_summary).unique_words = stream.unique_words as u32;
        (*out_summary).ttr = stream.type_token_ratio;
        (*out_summary).filler_ratio = stream.filler_ratio;
        (*out_summary).pace_wpm = stream.pace_wpm;
        (*out_summary).star_score = stream.star_completeness;
        (*out_summary).composite_hireability = cog.composite_hireability;
    }
    0
}
