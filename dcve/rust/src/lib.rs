//! lib.rs — DCVE Rust crate root
use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct DcveSummary {
    pub domain_competence_index: f32,
    pub domain_grade: u8,
    pub buzzword_density: f32,
    pub conceptual_precision: f32,
}

#[no_mangle]
pub extern "C" fn dcve_rust_evaluate(
    text_ptr: *const c_char,
    out: *mut DcveSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let lower = text.to_lowercase();

    let technical = ["p99", "latency", "distributed", "concurrency", "mutex", "cache", "throughput", "consensus", "atomic", "sharding", "zero-copy"];
    let buzzwords = ["synergy", "paradigm", "game-changer", "disrupt", "leverage", "hyper-scale", "next-gen", "silver bullet"];

    let mut tech_count = 0;
    for t in &technical {
        if lower.contains(t) { tech_count += 1; }
    }
    let mut buzz_count = 0;
    for b in &buzzwords {
        if lower.contains(b) { buzz_count += 1; }
    }

    let has_numbers = lower.chars().any(|c| c.is_ascii_digit());
    let precision = if has_numbers { 0.85 } else { 0.50 };

    let depth = ((tech_count as f32) * 0.20).clamp(0.0, 1.0);
    let buzz = ((buzz_count as f32) * 0.25).clamp(0.0, 1.0);

    let dci = (0.40 * depth + 0.35 * precision + 0.25 * (1.0 - buzz)).clamp(0.0, 1.0);

    let grade = if dci >= 0.78 { 1 }
        else if dci >= 0.58 { 2 }
        else if dci >= 0.38 { 3 }
        else { 4 };

    unsafe {
        (*out).domain_competence_index = dci;
        (*out).domain_grade = grade;
        (*out).buzzword_density = buzz;
        (*out).conceptual_precision = precision;
    }
    0
}
