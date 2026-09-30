//! lib.rs — LSCE Rust crate root
use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct LsceSummary {
    pub endurance_index: f32,
    pub endurance_grade: u8,
    pub stamina_slope: f32,
    pub ttr_diversity: f32,
}

#[no_mangle]
pub extern "C" fn lsce_rust_evaluate(
    text_ptr: *const c_char,
    stamina_slope: f32,
    out: *mut LsceSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let words: Vec<&str> = text.split_whitespace().collect();
    let total_words = words.len().max(1);

    // Compute Type-Token Ratio (TTR)
    let mut unique_words = std::collections::HashSet::new();
    for w in &words {
        unique_words.insert(w.to_lowercase());
    }
    let ttr = (unique_words.len() as f32 / total_words as f32).clamp(0.0, 1.0);

    let resilience = 0.85;
    let ei = (0.40 * stamina_slope + 0.30 * ttr + 0.30 * resilience).clamp(0.0, 1.0);

    let grade = if ei >= 0.80 { 1 }
        else if ei >= 0.60 { 2 }
        else if ei >= 0.40 { 3 }
        else { 4 };

    unsafe {
        (*out).endurance_index = ei;
        (*out).endurance_grade = grade;
        (*out).stamina_slope = stamina_slope;
        (*out).ttr_diversity = ttr;
    }
    0
}
