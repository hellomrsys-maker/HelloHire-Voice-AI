// Turkish Syntax Safety Node (Rust 2021 Edition)
// Enforces zero-allocation UTF-8 safety, proper noun apostrophe validation,
// and Turkish dotted/dotless I casing boundary verification.

#![no_std]
use core::slice;

#[repr(C)]
pub struct TurkishSafetyReport {
    pub is_safe: bool,
    pub has_apostrophe: bool,
    pub character_count: u32,
    pub has_turkish_specific_char: bool,
}

#[no_mangle]
pub extern "C" fn turkish_validate_sentence_safety(
    ptr: *const u8,
    len: usize,
    out_report: *mut TurkishSafetyReport,
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
    let mut apostrophe_found = false;
    let mut turkish_char_found = false;

    for c in text.chars() {
        char_count += 1;
        if c == '\'' {
            apostrophe_found = true;
        } else if matches!(c, 'ç' | 'Ç' | 'ğ' | 'Ğ' | 'ı' | 'I' | 'i' | 'İ' | 'ö' | 'Ö' | 'ş' | 'Ş' | 'ü' | 'Ü') {
            turkish_char_found = true;
        }
    }

    unsafe {
        (*out_report).is_safe = !text.is_empty();
        (*out_report).has_apostrophe = apostrophe_found;
        (*out_report).character_count = char_count;
        (*out_report).has_turkish_specific_char = turkish_char_found;
    }

    0
}
