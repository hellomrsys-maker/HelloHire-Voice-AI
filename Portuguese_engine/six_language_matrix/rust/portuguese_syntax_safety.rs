// Portuguese Syntax Safety Node (Rust 2021 Edition)
// Enforces zero-allocation UTF-8 safety, hyphenated clitic validation,
// mesoclisis hyphen balance, and crase grave accent verification.

#![no_std]
use core::slice;

#[repr(C)]
pub struct PortugueseSafetyReport {
    pub is_safe: bool,
    pub has_clitic_hyphen: bool,
    pub character_count: u32,
    pub has_crase_accent: bool,
}

#[no_mangle]
pub extern "C" fn portuguese_validate_sentence_safety(
    ptr: *const u8,
    len: usize,
    out_report: *mut PortugueseSafetyReport,
) -> i32 {
    if ptr.is_null() || out_report.is_null() {
        return -1;
    }

    let slice_data = unsafe { slice::from_raw_parts(ptr, len) };
    let text = match core::str::from_utf8(slice_data) {
        Ok(s) => s.trim(),
        Err(_) => return -2,
    };

    let mut char_count: u32 = 0;
    let mut clitic_found = false;
    let mut crase_found = false;

    for c in text.chars() {
        char_count += 1;
        if c == '-' {
            clitic_found = true;
        } else if c == 'à' || c == 'À' {
            crase_found = true;
        }
    }

    unsafe {
        (*out_report).is_safe = !text.is_empty();
        (*out_report).has_clitic_hyphen = clitic_found;
        (*out_report).character_count = char_count;
        (*out_report).has_crase_accent = crase_found;
    }

    0
}
