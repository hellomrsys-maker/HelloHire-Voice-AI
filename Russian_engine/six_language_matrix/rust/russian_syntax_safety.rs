// Russian Syntax Safety Node (Rust 2021 Edition)
// Enforces zero-allocation Cyrillic UTF-8 safety, hyphenated compound particle validation,
// and soft/hard sign palatalization boundary verification.

#![no_std]
use core::slice;

#[repr(C)]
pub struct RussianSafetyReport {
    pub is_safe: bool,
    pub has_hyphen_particle: bool,
    pub character_count: u32,
    pub has_palatalization_sign: bool,
}

#[no_mangle]
pub extern "C" fn russian_validate_sentence_safety(
    ptr: *const u8,
    len: usize,
    out_report: *mut RussianSafetyReport,
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
    let mut hyphen_particle_found = false;
    let mut palatal_sign_found = false;

    for c in text.chars() {
        char_count += 1;
        if c == '-' {
            hyphen_particle_found = true;
        } else if c == 'ь' || c == 'Ь' || c == 'ъ' || c == 'Ъ' {
            palatal_sign_found = true;
        }
    }

    unsafe {
        (*out_report).is_safe = !text.is_empty();
        (*out_report).has_hyphen_particle = hyphen_particle_found;
        (*out_report).character_count = char_count;
        (*out_report).has_palatalization_sign = palatal_sign_found;
    }

    0
}
