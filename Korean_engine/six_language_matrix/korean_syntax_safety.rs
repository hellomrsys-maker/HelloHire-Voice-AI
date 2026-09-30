//! Korean Engine — Rust High-Safety Syntax & Memory Module
//! Provides zero-cost abstraction, thread-safe SOV dependency tracking,
//! and raw pointer physical synchronization for the 64-byte Atomic Memory State Vector (AMSV).

pub const KOREAN_AMSV_MAGIC: u32 = 0x4B4F5245; // "KORE"
pub const KOREAN_AMSV_SIZE: usize = 64;

#[repr(C, align(64))]
pub struct KoreanAmsvLayout {
    pub magic_header: u32,            // 0..3: 0x4B4F5245
    pub version: u32,                 // 4..7: 0x00010000
    pub token_count: u32,             // 8..11
    pub sentence_count: u32,          // 12..15
    pub clause_type: u16,             // 16..17: Declarative, Interrogative, etc.
    pub syntax_flags: u8,             // 18: Head-final, Topic, Subject, Object
    pub particle_error_flags: u8,     // 19: 은/는, 이/가, 을/를 errors
    pub phonology_flags: u8,          // 20: Batchim, neutralization applied
    pub irregular_verb_flags: u8,     // 21: Irregular stem flags
    pub speech_level_code: u8,        // 22: 1=Hasipsio, 2=Haeyo, etc.
    pub honorific_concord_flags: u8,  // 23: Subject hon, 께서, lexical hon
    pub sub_ai_confidence: f32,       // 24..27: Confidence score
    pub syntax_latency_ns: u32,       // 28..31
    pub morph_latency_ns: u32,        // 32..35
    pub reserved: [u8; 12],           // 36..47
    pub crc32_checksum: u32,          // 48..51
    pub syntax_sub_ai_id: u8,         // 52
    pub phonology_sub_ai_id: u8,      // 53
    pub pragmatic_sub_ai_id: u8,      // 54
    pub editorial_sub_ai_id: u8,      // 55
    pub timestamp_epoch_ns: u64,      // 56..63
}

impl KoreanAmsvLayout {
    pub fn new() -> Self {
        Self {
            magic_header: KOREAN_AMSV_MAGIC,
            version: 0x00010000,
            token_count: 0,
            sentence_count: 0,
            clause_type: 0x0001,
            syntax_flags: 0x01, // Head-final default
            particle_error_flags: 0,
            phonology_flags: 0,
            irregular_verb_flags: 0,
            speech_level_code: 2, // Default Haeyo-che
            honorific_concord_flags: 0,
            sub_ai_confidence: 1.0,
            syntax_latency_ns: 0,
            morph_latency_ns: 0,
            reserved: [0u8; 12],
            crc32_checksum: 0,
            syntax_sub_ai_id: 1,
            phonology_sub_ai_id: 1,
            pragmatic_sub_ai_id: 1,
            editorial_sub_ai_id: 1,
            timestamp_epoch_ns: 0,
        }
    }

    /// Zero-bridge synchronized write into physical buffer pointer.
    pub unsafe fn sync_to_buffer(&self, raw_ptr: *mut u8) {
        if raw_ptr.is_null() {
            return;
        }
        std::ptr::copy_nonoverlapping(
            self as *const Self as *const u8,
            raw_ptr,
            KOREAN_AMSV_SIZE,
        );
    }
}
