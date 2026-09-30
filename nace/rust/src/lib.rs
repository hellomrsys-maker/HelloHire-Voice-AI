//! lib.rs — NACE Rust crate root
use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct NaceSummary {
    pub narrative_coherence_index: f32,
    pub narrative_grade: u8,
    pub contradiction_flag: u8,
    pub star_climax_score: f32,
}

#[no_mangle]
pub extern "C" fn nace_rust_evaluate(
    text_ptr: *const c_char,
    has_contradiction: u8,
    out: *mut NaceSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let lower = text.to_lowercase();

    let star_cues = ["situation", "task", "action", "result", "outcome", "finally", "achieved", "delivered"];
    let mut star_count = 0;
    for c in &star_cues {
        if lower.contains(c) { star_count += 1; }
    }
    let climax = ((star_count as f32) * 0.25).clamp(0.0, 1.0);

    let contra_penalty = if has_contradiction != 0 { 0.50 } else { 0.0 };
    let nci = (0.45 * climax + 0.40 * 0.85 + 0.15 - contra_penalty).clamp(0.0, 1.0);

    let grade = if has_contradiction != 0 {
        4
    } else if nci >= 0.80 {
        1
    } else if nci >= 0.60 {
        2
    } else if nci >= 0.40 {
        3
    } else {
        4
    };

    unsafe {
        (*out).narrative_coherence_index = nci;
        (*out).narrative_grade = grade;
        (*out).contradiction_flag = has_contradiction;
        (*out).star_climax_score = climax;
    }
    0
}
