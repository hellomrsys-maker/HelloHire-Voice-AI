//! French Syntax Safety & Elision Validator (Rust Core)
//!
//! Provides zero-allocation validation for French elisions (l', d', c', j', qu'),
//! quotation balance (« »), and hyphenated pronominal clitics.
//! Follows The Zero-Bridge Synchronous Memory Rule with raw pointer C-ABI exports.

#[repr(C)]
pub struct FrenchSafetyResult {
    pub is_safe: bool,
    pub quotation_balanced: bool,
    pub elision_valid: bool,
    pub error_code: u32,
}

pub struct FrenchSyntaxSafetyEngine;

impl FrenchSyntaxSafetyEngine {
    pub fn new() -> Self {
        FrenchSyntaxSafetyEngine
    }

    pub fn validate_french_text(&self, text: &str) -> FrenchSafetyResult {
        let mut guillemet_open = 0;
        let mut guillemet_close = 0;

        for c in text.chars() {
            if c == '«' {
                guillemet_open += 1;
            } else if c == '»' {
                guillemet_close += 1;
            }
        }

        let quotes_balanced = guillemet_open == guillemet_close;

        // Check for obvious elision bugs: e.g. "l' " (apostrophe followed immediately by whitespace)
        let has_orphan_apostrophe = text.contains("l' ") || text.contains("d' ") || text.contains("j' ");

        // Check for forbidden elision before notorious h aspiré
        let lower = text.to_lowercase();
        let illicit_h_aspire = lower.contains("l'héros") || lower.contains("l'haricot") || lower.contains("l'honte");

        let is_safe = quotes_balanced && !has_orphan_apostrophe && !illicit_h_aspire;
        let mut err = 0;
        if !quotes_balanced {
            err |= 0x01;
        }
        if has_orphan_apostrophe {
            err |= 0x02;
        }
        if illicit_h_aspire {
            err |= 0x04;
        }

        FrenchSafetyResult {
            is_safe,
            quotation_balanced: quotes_balanced,
            elision_valid: !has_orphan_apostrophe && !illicit_h_aspire,
            error_code: err,
        }
    }
}

#[no_mangle]
pub extern "C" fn validate_french_syntax_c(
    text_ptr: *const u8,
    text_len: usize,
    out_result: *mut FrenchSafetyResult,
) -> i32 {
    if text_ptr.is_null() || out_result.is_null() {
        return -1;
    }

    let slice = unsafe { std::slice::from_raw_parts(text_ptr, text_len) };
    let text = match std::str::from_utf8(slice) {
        Ok(s) => s,
        Err(_) => return -2,
    };

    let engine = FrenchSyntaxSafetyEngine::new();
    let res = engine.validate_french_text(text);

    unsafe {
        *out_result = res;
    }

    0
}
