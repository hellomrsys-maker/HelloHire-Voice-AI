//! lib.rs — PACE Rust crate root
use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct PaceSummary {
    pub adaptation_calibration_index: f32,
    pub pacing_grade: u8,
    pub length_compliance: f32,
    pub register_fit: f32,
}

#[no_mangle]
pub extern "C" fn pace_rust_evaluate(
    candidate_ptr: *const c_char,
    _interviewer_ptr: *const c_char,
    out: *mut PaceSummary,
) -> i32 {
    if candidate_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(candidate_ptr) }.to_str().unwrap_or("");
    let words = text.split_whitespace().count();

    // Optimal response length in conversational interview: 60-180 words
    let length_score = if words >= 50 && words <= 200 {
        0.92
    } else if words < 25 || words > 300 {
        0.45
    } else {
        0.75
    };

    let register_fit = 0.88;
    let aci = (0.50 * length_score + 0.50 * register_fit).clamp(0.0, 1.0);

    let grade = if aci >= 0.80 { 1 }
        else if aci >= 0.60 { 2 }
        else if aci >= 0.40 { 3 }
        else { 4 };

    unsafe {
        (*out).adaptation_calibration_index = aci;
        (*out).pacing_grade = grade;
        (*out).length_compliance = length_score;
        (*out).register_fit = register_fit;
    }
    0
}
