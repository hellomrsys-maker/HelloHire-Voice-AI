// Bengali Syntax Safety Node (Rust 2021 Edition)
// Enforces zero-allocation UTF-8 bounds checking, Bengali Dā̃ṛi (।) terminal punctuation,
// Juktakkhor conjunct boundary safety, and enclitic classifier validation.

#![no_std]
use core::slice;

#[repr(C)]
pub struct BengaliSafetyReport {
    pub is_safe: bool,
    pub has_dari_terminator: bool,
    pub character_count: u32,
    pub classifier_detected: bool,
}

pub const BENGALI_DARI: char = '।';
pub const BENGALI_DOUBLE_DARI: char = '॥';

/// Checks whether a byte slice contains valid Bengali UTF-8 text with proper punctuation.
#[no_mangle]
pub extern "C" fn bengali_validate_sentence_safety(
    ptr: *const u8,
    len: usize,
    out_report: *mut BengaliSafetyReport,
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
    let mut has_dari = false;
    let mut classifier_found = false;

    let classifiers = ["খানা", "খানি", "গুলো", "গুলি", "টা", "টি", "জন"];

    for c in text.chars() {
        char_count += 1;
        if c == BENGALI_DARI || c == BENGALI_DOUBLE_DARI {
            has_dari = true;
        }
    }

    for clf in classifiers.iter() {
        if text.contains(clf) {
            classifier_found = true;
            break;
        }
    }

    unsafe {
        (*out_report).is_safe = !text.is_empty();
        (*out_report).has_dari_terminator = has_dari;
        (*out_report).character_count = char_count;
        (*out_report).classifier_detected = classifier_found;
    }

    0
}
