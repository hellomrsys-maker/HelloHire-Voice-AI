//! lib.rs — PMCE Rust crate root
pub mod persuasion_stream;

use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct PmceSummary {
    pub logos: f32,
    pub ethos: f32,
    pub pathos: f32,
    pub kairos: f32,
    pub cta: f32,
    pub composite: f32,
}

#[no_mangle]
pub extern "C" fn pmce_rust_analyze(
    text_ptr: *const c_char,
    out: *mut PmceSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let res = persuasion_stream::analyze_persuasion(text);
    unsafe {
        (*out).logos = res.logos;
        (*out).ethos = res.ethos;
        (*out).pathos = res.pathos;
        (*out).kairos = res.kairos;
        (*out).cta = res.cta;
        (*out).composite = res.composite;
    }
    0
}
