//! Hindustani Syntax Safety & Postposition Validator (Rust Core)
//!
//! Provides zero-allocation validation for Hindustani postpositions, danda terminators,
//! and virama cluster integrity.
//! Follows The Zero-Bridge Synchronous Memory Rule with raw pointer C-ABI exports.

#[repr(C)]
pub struct HindustaniSafetyResult {
    pub is_safe: bool,
    pub has_postposition: bool,
    pub danda_valid: bool,
    pub error_code: u32,
}

pub struct HindustaniSyntaxSafetyEngine;

impl HindustaniSyntaxSafetyEngine {
    pub fn new() -> Self {
        HindustaniSyntaxSafetyEngine
    }

    pub fn validate_hindustani_text(&self, text: &str) -> HindustaniSafetyResult {
        // Check for postpositional markers
        let has_postposition = text.contains(" ne") || text.contains(" ko") || text.contains(" se")
            || text.contains(" mein") || text.contains(" par") || text.contains(" ka")
            || text.contains("ने") || text.contains("को") || text.contains("से") || text.contains("में");

        // Check for valid terminators
        let danda_valid = !text.contains("|||") && !text.contains("।।।");

        // Check for illegal stand-alone virama at string start
        let invalid_virama = text.starts_with('्');

        let is_safe = danda_valid && !invalid_virama;
        let mut err = 0;
        if !danda_valid {
            err |= 0x01;
        }
        if invalid_virama {
            err |= 0x02;
        }

        HindustaniSafetyResult {
            is_safe,
            has_postposition,
            danda_valid,
            error_code: err,
        }
    }
}

#[no_mangle]
pub extern "C" fn validate_hindustani_syntax_c(
    text_ptr: *const u8,
    text_len: usize,
    out_result: *mut HindustaniSafetyResult,
) -> i32 {
    if text_ptr.is_null() || out_result.is_null() {
        return -1;
    }

    let slice = unsafe { std::slice::from_raw_parts(text_ptr, text_len) };
    let text = match std::str::from_utf8(slice) {
        Ok(s) => s,
        Err(_) => return -2,
    };

    let engine = HindustaniSyntaxSafetyEngine::new();
    let res = engine.validate_hindustani_text(text);

    unsafe {
        *out_result = res;
    }

    0
}
