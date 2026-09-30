//! lib.rs — CDIE Rust crate root
pub mod cross_domain_stream;

use std::ffi::CStr;
use std::os::raw::c_char;

#[repr(C)]
pub struct CdieSummary {
    pub cdti: f32,
    pub transfer_grade: u8,
    pub has_cross_domain_bridge: u8,
    pub manifold_distance: f32,
}

#[no_mangle]
pub extern "C" fn cdie_rust_evaluate(
    text_ptr: *const c_char,
    out: *mut CdieSummary,
) -> i32 {
    if text_ptr.is_null() || out.is_null() {
        return -1;
    }
    let text = unsafe { CStr::from_ptr(text_ptr) }.to_str().unwrap_or("");
    let res = cross_domain_stream::analyze_cross_domain(text);
    unsafe {
        (*out).cdti = res.cdti;
        (*out).transfer_grade = res.transfer_grade;
        (*out).has_cross_domain_bridge = res.has_cross_domain_bridge as u8;
        (*out).manifold_distance = res.manifold_distance;
    }
    0
}
