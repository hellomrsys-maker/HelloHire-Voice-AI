//! Italian Engine — Rust Syntax Safety & Zero-Bridge AMSV FFI
//! Provides zero-allocation validation for Italian clitic chains, elision boundaries,
//! and direct physical synchronization with the 64-byte Atomic Memory State Vector (AMSV).

#[repr(C, align(64))]
pub struct ItalianAMSV {
    pub magic: u32,             // 0..3: 0x4954414C ("ITAL")
    pub version: u32,           // 4..7: 0x00010000
    pub token_count: u32,       // 8..11
    pub sentence_count: u32,    // 12..15
    pub clause_type_mask: u16,  // 16..17
    pub syntax_flags: u8,       // 18
    pub auxiliary_flags: u8,    // 19
    pub phonology_flags: u8,    // 20
    pub morphology_flags: u8,   // 21
    pub register_tier: u8,      // 22
    pub pragmatic_flags: u8,    // 23
    pub confidence_score: f32,  // 24..27
    pub reserved: [u8; 24],     // 28..51
    pub sub_ai_active: [u8; 4], // 52..55: Syntax, Phonology, Pragmatic, Editorial
    pub tail_checksum: u64,     // 56..63
}

pub const ITALIAN_AMSV_MAGIC: u32 = 0x4954414C;

#[no_mangle]
pub unsafe extern "C" fn italian_validate_clitic_cluster(first: *const u8, first_len: usize, second: *const u8, second_len: usize) -> bool {
    if first.is_null() || second.is_null() {
        return false;
    }
    let s1 = std::slice::from_raw_parts(first, first_len);
    let s2 = std::slice::from_raw_parts(second, second_len);
    
    // Illegal unshifted chains: mi/ti/ci/vi/si + lo/la/li/le/ne
    let is_unshifted = match s1 {
        b"mi" | b"ti" | b"ci" | b"vi" | b"si" => matches!(s2, b"lo" | b"la" | b"li" | b"le" | b"ne"),
        _ => false,
    };
    !is_unshifted
}

#[no_mangle]
pub unsafe extern "C" fn italian_sync_amsv(buffer: *mut u8, len: usize, token_count: u32, confidence: f32) -> bool {
    if buffer.is_null() || len < 64 {
        return false;
    }
    let amsv = &mut *(buffer as *mut ItalianAMSV);
    amsv.magic = ITALIAN_AMSV_MAGIC;
    amsv.version = 0x00010000;
    amsv.token_count = token_count;
    amsv.confidence_score = confidence;
    amsv.sub_ai_active = [1, 1, 1, 1];
    true
}
