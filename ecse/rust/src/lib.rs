//! lib.rs — ECSE Rust crate root
pub mod social_stream;

use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct EcseSummary {
    pub positive_affect: f32,
    pub negative_affect: f32,
    pub valence_score: f32,
    pub warmth_density: f32,
    pub collective_identity: f32,
    pub diplomatic_tact: f32,
    pub composite_score: f32,
}

#[no_mangle]
pub extern "C" fn ecse_rust_analyze(
    text_ptr: *const c_char,
    out: *mut EcseSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let res = social_stream::analyze_social_metrics(text);
    unsafe {
        (*out).positive_affect = res.positive_affect;
        (*out).negative_affect = res.negative_affect;
        (*out).valence_score = res.valence_score;
        (*out).warmth_density = res.warmth_density;
        (*out).collective_identity = res.collective_identity;
        (*out).diplomatic_tact = res.diplomatic_tact;
        (*out).composite_score = res.composite_score;
    }
    0
}
